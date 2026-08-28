"""Salesforce pull-request queue orchestration.

The issue comment maintained by this program is deliberately *not* an
authorization primitive. It points at GitHub-owned evidence: the successful
quality run, the privileged validation run, and a check run bound to the exact
PR/head/base/validation tuple.

Only the Python standard library is used so trusted jobs never need to install
code from a pull request before using the orchestrator.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Iterable, Mapping, Optional


MARKER = "<!-- evolua-salesforce-ci-state -->"
STATE_SCHEMA_VERSION = 2
STATE_AUTHOR_ID = 41898282
QUALITY_WORKFLOW_PATH = ".github/workflows/salesforce-pr-quality.yml"
VALIDATION_WORKFLOW_PATH = ".github/workflows/salesforce-privileged-pipeline.yml"
QUALITY_JOB_NAME = "Quality Gate"
VALIDATION_JOB_NAME = "Salesforce Validate"
VALIDATION_CHECK_PREFIX = "Salesforce Validation / "

ALLOWED_TARGET_BRANCHES = frozenset({"dev", "main"})
ALLOWED_MERGE_STATES = frozenset({"CLEAN", "HAS_HOOKS"})
DECISIVE_REVIEW_STATES = frozenset({"APPROVED", "CHANGES_REQUESTED", "DISMISSED"})
TRUSTED_REVIEW_ASSOCIATIONS = frozenset({"OWNER", "MEMBER", "COLLABORATOR"})
HARD_BLOCK_REASONS = frozenset(
    {
        "post_deploy_merge_failure",
        "post_deploy_target_changed",
        "post_deploy_verification_failed",
        "cancelled_after_deploy",
    }
)
SOFT_BLOCK_REASONS = frozenset(
    {
        "validation_or_deploy_failure",
        "pre_deploy_verification_failed",
        "cancelled_before_deploy",
    }
)
STATE_STATUSES = frozenset(
    {
        "VALIDATED",
        "READY",
        "CLAIMED",
        "DEPLOYING",
        "CLOSED",
        "WAITING_VALIDATION",
        "WAITING_MERGE",
        "BLOCKED",
        "HARD_BLOCKED",
    }
)

SHA_RE = re.compile(r"\A[0-9a-f]{40}\Z")
SF_JOB_ID_RE = re.compile(r"\A0Af[A-Za-z0-9]{12}(?:[A-Za-z0-9]{3})?\Z")
OUTPUT_KEY_RE = re.compile(r"\A[A-Za-z_][A-Za-z0-9_]*\Z")
LOGIN_RE = re.compile(r"\A[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?\Z")


class QueueError(RuntimeError):
    """Base class for fail-closed orchestration errors."""


class ConfigurationError(QueueError):
    """Invalid process configuration or CLI arguments."""


class StateError(QueueError):
    """Malformed, ambiguous, or stale projected state."""


class EvidenceError(QueueError):
    """GitHub evidence does not prove the asserted state."""


class StateConflict(StateError):
    """The state changed between a read and a write."""


@dataclass(frozen=True)
class Config:
    token: str
    repository: str
    api_base: str = "https://api.github.com"
    graphql_url: str = "https://api.github.com/graphql"
    state_author: str = "github-actions[bot]"
    state_author_id: int = STATE_AUTHOR_ID
    required_approvals: int = 1
    claim_ttl_seconds: int = 4 * 60 * 60
    allowed_targets: frozenset[str] = ALLOWED_TARGET_BRANCHES
    quality_workflow_path: str = QUALITY_WORKFLOW_PATH
    validation_workflow_path: str = VALIDATION_WORKFLOW_PATH
    quality_job_name: str = QUALITY_JOB_NAME
    validation_job_name: str = VALIDATION_JOB_NAME
    validation_check_app: str = "github-actions"

    @property
    def owner(self) -> str:
        return self.repository.split("/", 1)[0]

    @property
    def repo(self) -> str:
        return self.repository.split("/", 1)[1]

    @classmethod
    def from_env(cls, env: Mapping[str, str] = os.environ) -> "Config":
        token = env.get("GITHUB_TOKEN") or env.get("GH_TOKEN") or ""
        repository = env.get("GITHUB_REPOSITORY", "")
        if not token:
            raise ConfigurationError("GITHUB_TOKEN or GH_TOKEN is required")
        if (
            repository.count("/") != 1
            or not all(repository.split("/", 1))
            or any(char in repository for char in "\r\n\0")
        ):
            raise ConfigurationError("GITHUB_REPOSITORY must be OWNER/REPO")
        required = _env_positive_int(env, "REQUIRED_APPROVALS", 1)
        claim_ttl = _env_positive_int(env, "QUEUE_CLAIM_TTL_SECONDS", 4 * 60 * 60)
        author_id = _env_positive_int(env, "CI_STATE_AUTHOR_ID", STATE_AUTHOR_ID)
        api_base = env.get("GITHUB_API_URL", "https://api.github.com").rstrip("/")
        graphql_url = env.get("GITHUB_GRAPHQL_URL", f"{api_base}/graphql")
        return cls(
            token=token,
            repository=repository,
            api_base=api_base,
            graphql_url=graphql_url,
            state_author=env.get("CI_STATE_AUTHOR", "github-actions[bot]"),
            state_author_id=author_id,
            required_approvals=required,
            claim_ttl_seconds=claim_ttl,
        )


def _env_positive_int(env: Mapping[str, str], name: str, default: int) -> int:
    raw = env.get(name, str(default))
    try:
        result = int(raw)
    except (TypeError, ValueError) as exc:
        raise ConfigurationError(f"{name} must be a positive integer") from exc
    if result < 1:
        raise ConfigurationError(f"{name} must be a positive integer")
    return result


class GitHubClient:
    """Small REST/GraphQL client with injectable I/O for offline tests."""

    def __init__(
        self,
        config: Config,
        opener: Callable[..., Any] = urllib.request.urlopen,
        sleeper: Callable[[float], None] = time.sleep,
    ) -> None:
        self.config = config
        self._opener = opener
        self._sleep = sleeper
        self._allowed_origins = {_origin(config.api_base), _origin(config.graphql_url)}

    def request(
        self,
        method: str,
        path_or_url: str,
        payload: Any = None,
        *,
        idempotent: Optional[bool] = None,
    ) -> Any:
        method = method.upper()
        if path_or_url.startswith(("http://", "https://")):
            url = path_or_url
        elif path_or_url.startswith("/"):
            url = f"{self.config.api_base}{path_or_url}"
        else:
            raise ConfigurationError("GitHub API path must start with '/'")
        if _origin(url) not in self._allowed_origins:
            raise ConfigurationError("refusing to send credentials to an untrusted origin")

        body = None if payload is None else json.dumps(payload).encode("utf-8")
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.config.token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "evolua-salesforce-queue-orchestrator",
        }
        if body is not None:
            headers["Content-Type"] = "application/json"
        if idempotent is None:
            idempotent = method in {"GET", "HEAD", "PUT", "DELETE", "PATCH"}
        attempts = 4 if idempotent else 1
        last_error: Optional[RuntimeError] = None
        for attempt in range(attempts):
            req = urllib.request.Request(url, data=body, headers=headers, method=method)
            try:
                with self._opener(req, timeout=30) as response:
                    response_body = response.read().decode("utf-8")
                    return None if not response_body else json.loads(response_body)
            except urllib.error.HTTPError as exc:
                error_body = exc.read().decode("utf-8", errors="replace")
                last_error = QueueError(f"GitHub API {exc.code}: {error_body}")
                retryable = exc.code == 429 or 500 <= exc.code < 600
                if not retryable or attempt == attempts - 1:
                    raise last_error from exc
                delay = _retry_delay(exc.headers, attempt)
            except urllib.error.URLError as exc:
                last_error = QueueError(f"GitHub API network error: {exc}")
                if attempt == attempts - 1:
                    raise last_error from exc
                delay = float(2**attempt)
            self._sleep(delay)
        raise last_error or QueueError("GitHub API request failed")

    def paginate(self, path: str, params: Optional[Mapping[str, Any]] = None) -> list[Any]:
        params = dict(params or {})
        results: list[Any] = []
        for page in range(1, 101):
            query = dict(params)
            query.update({"per_page": 100, "page": page})
            separator = "&" if "?" in path else "?"
            data = self.request("GET", f"{path}{separator}{urllib.parse.urlencode(query)}")
            if not isinstance(data, list):
                raise QueueError(f"expected list from {path}")
            results.extend(data)
            if len(data) < 100:
                return results
        raise QueueError(f"pagination limit exceeded for {path}")


def _origin(url: str) -> tuple[str, str, Optional[int]]:
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ConfigurationError(f"invalid API URL: {url!r}")
    return parsed.scheme, parsed.hostname.lower(), parsed.port


def _retry_delay(headers: Any, attempt: int) -> float:
    value = headers.get("Retry-After") if headers else None
    try:
        return max(0.0, min(float(value), 60.0)) if value is not None else float(2**attempt)
    except (TypeError, ValueError):
        return float(2**attempt)


def utc_now() -> str:
    return format_timestamp(datetime.now(timezone.utc))


def parse_timestamp(value: Any) -> datetime:
    if not isinstance(value, str) or not value or any(c in value for c in "\r\n\0"):
        raise StateError("timestamp must be a non-empty ISO-8601 string")
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        result = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise StateError(f"invalid timestamp: {value!r}") from exc
    if result.tzinfo is None:
        raise StateError("timestamp must include a timezone")
    return result.astimezone(timezone.utc)


def format_timestamp(value: datetime) -> str:
    if value.tzinfo is None:
        raise StateError("timestamp must include a timezone")
    return (
        value.astimezone(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def later_timestamp(*values: str) -> str:
    if not values:
        raise StateError("at least one timestamp is required")
    return format_timestamp(max(parse_timestamp(value) for value in values))


def _positive_int(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise StateError(f"{field} must be a positive integer")
    return value


def _sha(value: Any, field: str) -> str:
    if not isinstance(value, str) or not SHA_RE.fullmatch(value):
        raise StateError(f"{field} must be a 40-character lowercase SHA")
    return value


def _sf_job_id(value: Any) -> str:
    if not isinstance(value, str) or not SF_JOB_ID_RE.fullmatch(value):
        raise StateError("validation_id must be a Salesforce 0Af ID (15 or 18 chars)")
    return value


def _safe_text(value: Any, field: str, *, max_length: int = 200) -> str:
    if (
        not isinstance(value, str)
        or not value.strip()
        or len(value) > max_length
        or any(char in value for char in "\r\n\0")
    ):
        raise StateError(f"{field} contains invalid characters or length")
    return value.strip()


def _target(value: Any, allowed: Iterable[str] = ALLOWED_TARGET_BRANCHES) -> str:
    if not isinstance(value, str) or value not in set(allowed):
        raise StateError(f"unsupported target branch: {value!r}")
    return value


STATE_KEYS = frozenset(
    {
        "schema_version",
        "pr",
        "target_branch",
        "head_sha",
        "base_sha",
        "validation_id",
        "quality_run_id",
        "quality_run_attempt",
        "validation_run_id",
        "validation_run_attempt",
        "validation_check_run_id",
        "validated_at",
        "ready_at",
        "status",
        "blocked",
        "block_level",
        "blocked_at",
        "blocked_reason",
        "block_run_id",
        "block_head_sha",
        "claim",
        "recovery",
        "merge_block_reason",
    }
)


def validate_state(raw: Any, expected_pr: Optional[int] = None) -> dict[str, Any]:
    """Validate and copy state from an untrusted issue comment."""
    if not isinstance(raw, dict):
        raise StateError("queue state must be a JSON object")
    unknown = set(raw) - STATE_KEYS
    if unknown:
        raise StateError(f"queue state contains unknown fields: {sorted(unknown)}")
    if raw.get("schema_version") != STATE_SCHEMA_VERSION:
        raise StateError(f"queue state schema must be {STATE_SCHEMA_VERSION}")
    state = dict(raw)
    pr = _positive_int(state.get("pr"), "pr")
    if expected_pr is not None and pr != expected_pr:
        raise StateError("queue state belongs to another pull request")
    state["target_branch"] = _target(state.get("target_branch"))
    state["head_sha"] = _sha(state.get("head_sha"), "head_sha")
    state["base_sha"] = _sha(state.get("base_sha"), "base_sha")
    status = state.get("status")
    if status not in STATE_STATUSES:
        raise StateError(f"invalid queue status: {status!r}")
    if not isinstance(state.get("blocked"), bool):
        raise StateError("blocked must be boolean")

    evidence_fields = (
        "validation_id",
        "quality_run_id",
        "quality_run_attempt",
        "validation_run_id",
        "validation_run_attempt",
        "validation_check_run_id",
        "validated_at",
    )
    present = [state.get(field) is not None for field in evidence_fields]
    if any(present) and not all(present):
        raise StateError("validation evidence must be complete or entirely absent")
    if all(present):
        state["validation_id"] = _sf_job_id(state["validation_id"])
        for field in evidence_fields[1:-1]:
            state[field] = _positive_int(state[field], field)
        parse_timestamp(state["validated_at"])
    elif status not in {"WAITING_VALIDATION", "CLOSED", "HARD_BLOCKED"}:
        raise StateError(f"status {status} requires validation evidence")

    ready_at = state.get("ready_at")
    if ready_at is not None:
        parse_timestamp(ready_at)
    level = state.get("block_level")
    if state["blocked"]:
        if level not in {"SOFT", "HARD"}:
            raise StateError("blocked state requires SOFT or HARD block_level")
        if not state.get("blocked_at") or not state.get("blocked_reason"):
            raise StateError("blocked state requires time and reason")
        parse_timestamp(state["blocked_at"])
        _safe_text(state["blocked_reason"], "blocked_reason")
        if state.get("block_run_id") is not None:
            _positive_int(state["block_run_id"], "block_run_id")
        if state.get("block_head_sha") is not None:
            _sha(state["block_head_sha"], "block_head_sha")
    elif any(
        state.get(field) is not None
        for field in ("block_level", "blocked_at", "blocked_reason", "block_run_id", "block_head_sha")
    ):
        raise StateError("unblocked state cannot retain block fields")
    claim = state.get("claim")
    if claim is not None:
        state["claim"] = validate_claim(claim, state)
    recovery = state.get("recovery")
    if recovery is not None:
        state["recovery"] = validate_recovery(recovery)
    merge_reason = state.get("merge_block_reason")
    if merge_reason is not None:
        _safe_text(merge_reason, "merge_block_reason")
    return state


def validate_claim(raw: Any, state: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(raw, dict) or set(raw) != {
        "run_id",
        "run_attempt",
        "claimed_at",
        "expires_at",
        "head_sha",
        "base_sha",
        "validation_check_run_id",
    }:
        raise StateError("claim has invalid fields")
    claim = dict(raw)
    _positive_int(claim["run_id"], "claim.run_id")
    _positive_int(claim["run_attempt"], "claim.run_attempt")
    _sha(claim["head_sha"], "claim.head_sha")
    _sha(claim["base_sha"], "claim.base_sha")
    _positive_int(claim["validation_check_run_id"], "claim.validation_check_run_id")
    claimed = parse_timestamp(claim["claimed_at"])
    expires = parse_timestamp(claim["expires_at"])
    if expires <= claimed:
        raise StateError("claim expiration must be after acquisition")
    if claim["head_sha"] != state["head_sha"]:
        raise StateError("claim is for another head")
    if claim["validation_check_run_id"] != state.get("validation_check_run_id"):
        raise StateError("claim is for another validation")
    return claim


def validate_recovery(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict) or set(raw) != {"run_id", "actor", "at", "ticket", "reason"}:
        raise StateError("recovery has invalid fields")
    recovery = dict(raw)
    _positive_int(recovery["run_id"], "recovery.run_id")
    actor = _safe_text(recovery["actor"], "recovery.actor", max_length=39)
    if not LOGIN_RE.fullmatch(actor):
        raise StateError("recovery.actor is not a GitHub login")
    parse_timestamp(recovery["at"])
    _safe_text(recovery["ticket"], "recovery.ticket")
    _safe_text(recovery["reason"], "recovery.reason")
    return recovery


def parse_state(body: Any) -> Any:
    if not isinstance(body, str) or len(body) > 60_000:
        raise StateError("state comment body is invalid")
    prefix = f"{MARKER}\n"
    if not body.startswith(prefix):
        raise StateError("state marker must be the first line")
    try:
        return json.loads(body[len(prefix) :])
    except json.JSONDecodeError as exc:
        raise StateError("state comment contains invalid JSON") from exc


def render_state(state: Mapping[str, Any]) -> str:
    validated = validate_state(state, expected_pr=state.get("pr"))
    return f"{MARKER}\n{json.dumps(validated, sort_keys=True, indent=2)}"


def state_revision(comment: Optional[Mapping[str, Any]]) -> Optional[tuple[int, str, str]]:
    if comment is None:
        return None
    comment_id = _positive_int(comment.get("id"), "comment.id")
    updated_at = comment.get("updated_at") or comment.get("created_at")
    parse_timestamp(updated_at)
    body = comment.get("body")
    if not isinstance(body, str):
        raise StateError("state comment body is missing")
    return comment_id, updated_at, body


class StateStore:
    def __init__(self, api: Any, config: Config) -> None:
        self.api = api
        self.config = config

    def find(self, number: int) -> tuple[Optional[dict[str, Any]], Optional[dict[str, Any]]]:
        comments = self.api.paginate(
            f"/repos/{self.config.repository}/issues/{number}/comments"
        )
        matches = []
        for comment in comments:
            user = comment.get("user") or {}
            if (
                user.get("login") == self.config.state_author
                and user.get("type") == "Bot"
                and user.get("id") == self.config.state_author_id
                and isinstance(comment.get("body"), str)
                and comment["body"].startswith(f"{MARKER}\n")
            ):
                matches.append(comment)
        if len(matches) > 1:
            raise StateError(f"PR #{number} has multiple canonical state comments")
        if not matches:
            return None, None
        comment = matches[0]
        return comment, validate_state(parse_state(comment["body"]), number)

    def save(
        self,
        number: int,
        state: Mapping[str, Any],
        expected_revision: Optional[tuple[int, str, str]],
    ) -> dict[str, Any]:
        body = render_state(state)
        current_comment, _ = self.find(number)
        current_revision = state_revision(current_comment)
        if current_revision != expected_revision:
            raise StateConflict(f"PR #{number} state changed concurrently")
        if current_comment:
            result = self.api.request(
                "PATCH",
                f"/repos/{self.config.repository}/issues/comments/{current_comment['id']}",
                {"body": body},
            )
        else:
            result = self.api.request(
                "POST",
                f"/repos/{self.config.repository}/issues/{number}/comments",
                {"body": body},
            )
        if not isinstance(result, dict):
            raise StateError("GitHub did not return the saved state comment")
        if result.get("body") != body:
            raise StateConflict("saved state was not read back exactly")
        return result


@dataclass(frozen=True)
class Candidate:
    number: int
    head_sha: str
    current_base_sha: str
    ready_at: str
    validation_completed_at: str
    state: dict[str, Any]
    comment: dict[str, Any]


def _workflow_path(value: Any) -> Any:
    return value.split("@", 1)[0] if isinstance(value, str) else value


def _server_completion(*objects: Mapping[str, Any]) -> str:
    values = []
    for obj in objects:
        value = obj.get("completed_at") or obj.get("updated_at")
        if value:
            parse_timestamp(value)
            values.append(value)
    if not values:
        raise EvidenceError("GitHub evidence has no server completion timestamp")
    return later_timestamp(*values)


class QueueOrchestrator:
    def __init__(
        self,
        api: Any,
        config: Config,
        *,
        clock: Callable[[], datetime] = lambda: datetime.now(timezone.utc),
        sleeper: Callable[[float], None] = time.sleep,
    ) -> None:
        self.api = api
        self.config = config
        self.store = StateStore(api, config)
        self.clock = clock
        self.sleeper = sleeper

    def now(self) -> str:
        return format_timestamp(self.clock())

    def get_pr(self, number: int) -> dict[str, Any]:
        data = self.api.request("GET", f"/repos/{self.config.repository}/pulls/{number}")
        if not isinstance(data, dict):
            raise EvidenceError(f"PR #{number} was not returned by GitHub")
        return data

    def current_base_sha(self, target_branch: str) -> str:
        encoded = urllib.parse.quote(target_branch, safe="")
        data = self.api.request(
            "GET", f"/repos/{self.config.repository}/git/ref/heads/{encoded}"
        )
        try:
            return _sha(data["object"]["sha"], "current base SHA")
        except (KeyError, TypeError) as exc:
            raise EvidenceError("target branch ref response is malformed") from exc

    def assert_live_pr(
        self,
        pr: Mapping[str, Any],
        number: int,
        target_branch: str,
        head_sha: str,
    ) -> None:
        if pr.get("number") not in {None, number}:
            raise EvidenceError("GitHub returned a different pull request")
        if pr.get("state") != "open":
            raise EvidenceError("pull request is not open")
        if pr.get("draft"):
            raise EvidenceError("pull request is a draft")
        if (pr.get("base") or {}).get("ref") != target_branch:
            raise EvidenceError("pull request target branch changed")
        if (pr.get("head") or {}).get("sha") != head_sha:
            raise EvidenceError("pull request head changed")
        head_repo = ((pr.get("head") or {}).get("repo") or {}).get("full_name")
        if head_repo != self.config.repository:
            raise EvidenceError("fork pull requests are not eligible")

    def graphql_review_decision(self, number: int) -> Optional[str]:
        query = """
        query($owner: String!, $repo: String!, $number: Int!) {
          repository(owner: $owner, name: $repo) {
            pullRequest(number: $number) { reviewDecision }
          }
        }
        """
        data = self.api.request(
            "POST",
            self.config.graphql_url,
            {
                "query": query,
                "variables": {
                    "owner": self.config.owner,
                    "repo": self.config.repo,
                    "number": number,
                },
            },
            idempotent=True,
        )
        if not isinstance(data, dict):
            raise EvidenceError("GraphQL review response is malformed")
        if data.get("errors"):
            raise EvidenceError(f"GraphQL review error: {json.dumps(data['errors'])}")
        try:
            pull = data["data"]["repository"]["pullRequest"]
        except (KeyError, TypeError) as exc:
            raise EvidenceError("GraphQL review response is malformed") from exc
        return None if pull is None else pull.get("reviewDecision")

    def approval_time(self, number: int, head_sha: str, author_login: str) -> Optional[str]:
        reviews = self.api.paginate(
            f"/repos/{self.config.repository}/pulls/{number}/reviews"
        )
        latest_by_user: dict[str, Mapping[str, Any]] = {}
        for review in reviews:
            user = review.get("user") or {}
            login = user.get("login")
            if (
                review.get("commit_id") != head_sha
                or review.get("state") not in DECISIVE_REVIEW_STATES
                or review.get("author_association") not in TRUSTED_REVIEW_ASSOCIATIONS
                or user.get("type") == "Bot"
                or not isinstance(login, str)
                or login.casefold() == author_login.casefold()
                or not review.get("submitted_at")
            ):
                continue
            current_time = parse_timestamp(review["submitted_at"])
            previous = latest_by_user.get(login.casefold())
            if previous is None or current_time > parse_timestamp(previous["submitted_at"]):
                latest_by_user[login.casefold()] = review
        latest = list(latest_by_user.values())
        if any(review.get("state") == "CHANGES_REQUESTED" for review in latest):
            return None
        approvals = sorted(
            parse_timestamp(review["submitted_at"])
            for review in latest
            if review.get("state") == "APPROVED"
        )
        if len(approvals) < self.config.required_approvals:
            return None
        decision = self.graphql_review_decision(number)
        if decision in {"CHANGES_REQUESTED", "REVIEW_REQUIRED"}:
            return None
        return format_timestamp(approvals[self.config.required_approvals - 1])

    def merge_readiness(self, number: int, head_sha: str) -> tuple[bool, str]:
        query = """
        query($owner: String!, $repo: String!, $number: Int!) {
          repository(owner: $owner, name: $repo) {
            pullRequest(number: $number) {
              state isDraft headRefOid baseRefName mergeable mergeStateStatus reviewDecision
            }
          }
        }
        """
        payload = {
            "query": query,
            "variables": {
                "owner": self.config.owner,
                "repo": self.config.repo,
                "number": number,
            },
        }
        pull: Optional[Mapping[str, Any]] = None
        for attempt in range(3):
            data = self.api.request(
                "POST", self.config.graphql_url, payload, idempotent=True
            )
            if not isinstance(data, dict) or data.get("errors"):
                raise EvidenceError("GraphQL merge response is malformed or contains errors")
            try:
                pull = data["data"]["repository"]["pullRequest"]
            except (KeyError, TypeError) as exc:
                raise EvidenceError("GraphQL merge response is malformed") from exc
            if not pull:
                return False, "pull_request_not_found"
            if pull.get("mergeable") != "UNKNOWN" and pull.get("mergeStateStatus") != "UNKNOWN":
                break
            if attempt < 2:
                self.sleeper(2)
        assert pull is not None
        if pull.get("state") != "OPEN":
            return False, "pull_request_not_open"
        if pull.get("isDraft"):
            return False, "pull_request_is_draft"
        if pull.get("headRefOid") != head_sha:
            return False, "head_changed"
        if pull.get("mergeable") != "MERGEABLE":
            return False, f"mergeable_{pull.get('mergeable')}"
        merge_state = pull.get("mergeStateStatus")
        if merge_state not in ALLOWED_MERGE_STATES:
            return False, f"merge_state_{merge_state}"
        if pull.get("reviewDecision") in {"CHANGES_REQUESTED", "REVIEW_REQUIRED"}:
            return False, "review_not_satisfied"
        return True, str(merge_state)

    def _run_jobs(self, run_id: int, attempt: int) -> list[Mapping[str, Any]]:
        data = self.api.request(
            "GET",
            f"/repos/{self.config.repository}/actions/runs/{run_id}/attempts/{attempt}/jobs?per_page=100",
        )
        if not isinstance(data, dict) or not isinstance(data.get("jobs"), list):
            raise EvidenceError("workflow jobs response is malformed")
        if data.get("total_count", len(data["jobs"])) > len(data["jobs"]):
            raise EvidenceError("workflow has more than 100 jobs; refusing partial evidence")
        return data["jobs"]

    def verify_quality_evidence(
        self, state: Mapping[str, Any], pr: Mapping[str, Any]
    ) -> str:
        run_id = state["quality_run_id"]
        attempt = state["quality_run_attempt"]
        run = self.api.request(
            "GET", f"/repos/{self.config.repository}/actions/runs/{run_id}"
        )
        if not isinstance(run, dict):
            raise EvidenceError("quality workflow run response is malformed")
        expected = {
            "path": self.config.quality_workflow_path,
            "event": "pull_request",
            "status": "completed",
            "conclusion": "success",
            "head_sha": state["head_sha"],
            "run_attempt": attempt,
        }
        for field, value in expected.items():
            actual = _workflow_path(run.get(field)) if field == "path" else run.get(field)
            if actual != value:
                raise EvidenceError(f"quality run has unexpected {field}: {actual!r}")
        if ((run.get("repository") or {}).get("full_name")) != self.config.repository:
            raise EvidenceError("quality run belongs to another repository")
        if ((run.get("head_repository") or {}).get("full_name")) != self.config.repository:
            raise EvidenceError("quality run used a fork")
        matching_pr = any(
            item.get("number") == state["pr"]
            and (item.get("head") or {}).get("sha") == state["head_sha"]
            and (item.get("base") or {}).get("ref") == state["target_branch"]
            for item in run.get("pull_requests") or []
        )
        if not matching_pr:
            raise EvidenceError("quality run is not tied to this PR/head/base")
        jobs = self._run_jobs(run_id, attempt)
        matches = [job for job in jobs if job.get("name") == self.config.quality_job_name]
        if len(matches) != 1 or matches[0].get("conclusion") != "success":
            raise EvidenceError("Quality Gate job did not complete successfully")
        return _server_completion(matches[0], run)

    def verify_validation_run_metadata(self, state: Mapping[str, Any]) -> Mapping[str, Any]:
        run_id = state["validation_run_id"]
        run = self.api.request(
            "GET", f"/repos/{self.config.repository}/actions/runs/{run_id}"
        )
        if not isinstance(run, dict):
            raise EvidenceError("validation workflow run response is malformed")
        expected = {
            "path": self.config.validation_workflow_path,
            "event": "workflow_run",
            "run_attempt": state["validation_run_attempt"],
        }
        for field, value in expected.items():
            actual = _workflow_path(run.get(field)) if field == "path" else run.get(field)
            if actual != value:
                raise EvidenceError(f"validation run has unexpected {field}: {actual!r}")
        if ((run.get("repository") or {}).get("full_name")) != self.config.repository:
            raise EvidenceError("validation run belongs to another repository")
        if ((run.get("head_repository") or {}).get("full_name")) != self.config.repository:
            raise EvidenceError("validation run used another repository")
        if run.get("status") == "completed" and run.get("conclusion") != "success":
            raise EvidenceError("validation workflow concluded unsuccessfully")
        return run

    def validation_external_id(self, state: Mapping[str, Any]) -> str:
        fields = (
            "sfq-v2",
            str(state["pr"]),
            state["target_branch"],
            state["head_sha"],
            state["base_sha"],
            state["validation_id"],
            str(state["quality_run_id"]),
            str(state["quality_run_attempt"]),
            str(state["validation_run_id"]),
            str(state["validation_run_attempt"]),
        )
        return ":".join(fields)

    def _assert_check(self, state: Mapping[str, Any], check: Mapping[str, Any]) -> None:
        expected = {
            "name": f"{VALIDATION_CHECK_PREFIX}{state['target_branch']}",
            "head_sha": state["head_sha"],
            "status": "completed",
            "conclusion": "success",
            "external_id": self.validation_external_id(state),
        }
        for field, value in expected.items():
            if check.get(field) != value:
                raise EvidenceError(f"validation check has unexpected {field}")
        app_slug = ((check.get("app") or {}).get("slug"))
        if app_slug is not None and app_slug != self.config.validation_check_app:
            raise EvidenceError("validation check was created by an unexpected app")

    def verify_validation_check_only(self, state: Mapping[str, Any]) -> None:
        check = self.api.request(
            "GET",
            f"/repos/{self.config.repository}/check-runs/{state['validation_check_run_id']}",
        )
        if not isinstance(check, dict):
            raise EvidenceError("validation check response is malformed")
        self._assert_check(state, check)
        if ((check.get("app") or {}).get("slug")) != self.config.validation_check_app:
            raise EvidenceError("validation check was created by an unexpected app")

    def verify_validation_evidence(self, state: Mapping[str, Any]) -> str:
        self.verify_validation_run_metadata(state)
        check = self.api.request(
            "GET",
            f"/repos/{self.config.repository}/check-runs/{state['validation_check_run_id']}",
        )
        if not isinstance(check, dict):
            raise EvidenceError("validation check response is malformed")
        self._assert_check(state, check)
        if ((check.get("app") or {}).get("slug")) != self.config.validation_check_app:
            raise EvidenceError("validation check was created by an unexpected app")
        jobs = self._run_jobs(state["validation_run_id"], state["validation_run_attempt"])
        matches = [job for job in jobs if job.get("name") == self.config.validation_job_name]
        if len(matches) != 1 or matches[0].get("conclusion") != "success":
            raise EvidenceError("Salesforce Validate job did not complete successfully")
        check_time = check.get("completed_at")
        parse_timestamp(check_time)
        return later_timestamp(check_time, _server_completion(matches[0]))

    def _candidate(
        self,
        pr: Mapping[str, Any],
        comment: dict[str, Any],
        state: dict[str, Any],
        run_id: int,
        now: datetime,
    ) -> Candidate:
        number = state["pr"]
        self.assert_live_pr(pr, number, state["target_branch"], state["head_sha"])
        if state["blocked"]:
            raise EvidenceError("pull request is blocked")
        if state.get("validation_id") is None:
            raise EvidenceError("pull request needs a new validation")
        claim = state.get("claim")
        if claim and claim["run_id"] != run_id and parse_timestamp(claim["expires_at"]) > now:
            raise EvidenceError(f"candidate is claimed by run {claim['run_id']}")
        self.verify_quality_evidence(state, pr)
        validation_completed = self.verify_validation_evidence(state)
        author = ((pr.get("user") or {}).get("login"))
        if not isinstance(author, str):
            raise EvidenceError("pull request author is missing")
        approved_at = self.approval_time(number, state["head_sha"], author)
        if not approved_at:
            raise EvidenceError("required approvals are not satisfied")
        ready_at = later_timestamp(validation_completed, approved_at)
        merge_ready, reason = self.merge_readiness(number, state["head_sha"])
        if not merge_ready:
            raise EvidenceError(reason)
        return Candidate(
            number=number,
            head_sha=state["head_sha"],
            current_base_sha=self.current_base_sha(state["target_branch"]),
            ready_at=ready_at,
            validation_completed_at=validation_completed,
            state=state,
            comment=comment,
        )

    def _all_target_states(
        self, target_branch: str
    ) -> list[tuple[Mapping[str, Any], dict[str, Any], dict[str, Any]]]:
        pulls = self.api.paginate(
            f"/repos/{self.config.repository}/pulls",
            {
                "state": "all",
                "base": target_branch,
                "sort": "created",
                "direction": "asc",
            },
        )
        states = []
        for pr in pulls:
            number = pr.get("number")
            if isinstance(number, bool) or not isinstance(number, int) or number < 1:
                continue
            try:
                comment, state = self.store.find(number)
            except StateError as exc:
                print(f"PR #{number} skipped: invalid state: {exc}", file=sys.stderr)
                continue
            if comment and state and state["target_branch"] == target_branch:
                states.append((pr, comment, state))
        return states

    def target_hard_blocks(self, target_branch: str) -> list[dict[str, Any]]:
        return [
            state
            for _pr, _comment, state in self._all_target_states(target_branch)
            if state["blocked"] and state["block_level"] == "HARD"
        ]

    def record_validation(self, args: argparse.Namespace) -> None:
        number = _positive_int(args.pr, "pr")
        target = _target(args.target_branch, self.config.allowed_targets)
        head = _sha(args.head_sha, "head_sha")
        base = _sha(args.base_sha, "base_sha")
        validation_id = _sf_job_id(args.validation_id)
        quality_run_id = _positive_int(args.quality_run_id, "quality_run_id")
        quality_attempt = _positive_int(args.quality_run_attempt, "quality_run_attempt")
        validation_run_id = _positive_int(args.validation_run_id, "validation_run_id")
        validation_attempt = _positive_int(
            args.validation_run_attempt, "validation_run_attempt"
        )
        pr = self.get_pr(number)
        self.assert_live_pr(pr, number, target, head)
        if self.current_base_sha(target) != base:
            raise StateConflict("target branch changed before validation was recorded")
        old_comment, old_state = self.store.find(number)
        old_revision = state_revision(old_comment)
        if old_state and old_state["blocked"] and old_state["block_level"] == "HARD":
            raise StateError("target is hard-blocked; manual recovery is required")

        state = {
            "schema_version": STATE_SCHEMA_VERSION,
            "pr": number,
            "target_branch": target,
            "head_sha": head,
            "base_sha": base,
            "validation_id": validation_id,
            "quality_run_id": quality_run_id,
            "quality_run_attempt": quality_attempt,
            "validation_run_id": validation_run_id,
            "validation_run_attempt": validation_attempt,
            "validation_check_run_id": 1,
            "validated_at": self.now(),
            "ready_at": None,
            "status": "VALIDATED",
            "blocked": False,
            "block_level": None,
            "blocked_at": None,
            "blocked_reason": None,
            "block_run_id": None,
            "block_head_sha": None,
            "claim": None,
            "recovery": old_state.get("recovery") if old_state else None,
            "merge_block_reason": None,
        }
        self.verify_quality_evidence(state, pr)
        self.verify_validation_run_metadata(state)

        same_evidence = old_state and all(
            old_state.get(field) == state.get(field)
            for field in (
                "pr",
                "target_branch",
                "head_sha",
                "base_sha",
                "validation_id",
                "quality_run_id",
                "quality_run_attempt",
                "validation_run_id",
                "validation_run_attempt",
            )
        )
        if same_evidence:
            self.verify_validation_check_only(old_state)
            return

        completed_at = self.now()
        state["validated_at"] = completed_at
        check = self.api.request(
            "POST",
            f"/repos/{self.config.repository}/check-runs",
            {
                "name": f"{VALIDATION_CHECK_PREFIX}{target}",
                "head_sha": head,
                "status": "completed",
                "conclusion": "success",
                "completed_at": completed_at,
                "external_id": self.validation_external_id(state),
                "details_url": (
                    f"https://github.com/{self.config.repository}/actions/runs/"
                    f"{validation_run_id}/attempts/{validation_attempt}"
                ),
                "output": {
                    "title": "Salesforce validation completed",
                    "summary": (
                        f"PR #{number} at {head} was validated against {target} at {base}."
                    ),
                },
            },
        )
        if not isinstance(check, dict):
            raise EvidenceError("GitHub did not return the validation check")
        state["validation_check_run_id"] = _positive_int(check.get("id"), "check.id")
        check_completed = check.get("completed_at") or completed_at
        parse_timestamp(check_completed)
        state["validated_at"] = check_completed
        self._assert_check(state, check)
        self.store.save(number, state, old_revision)

    def sync_ready(self, args: argparse.Namespace) -> None:
        comment, state = self.store.find(args.pr)
        if not comment or not state:
            return
        revision = state_revision(comment)
        pr = self.get_pr(args.pr)
        if pr.get("state") != "open":
            state.update({"ready_at": None, "status": "CLOSED", "claim": None})
        elif state["blocked"]:
            state.update(
                {
                    "ready_at": None,
                    "status": "HARD_BLOCKED" if state["block_level"] == "HARD" else "BLOCKED",
                    "claim": None,
                }
            )
        elif (pr.get("head") or {}).get("sha") != state["head_sha"]:
            state.update({"ready_at": None, "status": "WAITING_VALIDATION", "claim": None})
        elif state.get("validation_id") is None:
            state.update({"ready_at": None, "status": "WAITING_VALIDATION", "claim": None})
        else:
            author = ((pr.get("user") or {}).get("login")) or ""
            approved = self.approval_time(args.pr, state["head_sha"], author)
            if approved:
                state["ready_at"] = later_timestamp(state["validated_at"], approved)
                state["status"] = "READY"
            else:
                state.update({"ready_at": None, "status": "VALIDATED", "claim": None})
        self.store.save(args.pr, state, revision)

    def select_next(self, args: argparse.Namespace) -> None:
        target = _target(args.target_branch, self.config.allowed_targets)
        run_id = _positive_int(args.run_id, "run_id")
        run_attempt = _positive_int(args.run_attempt, "run_attempt")
        for retry in range(3):
            target_states = self._all_target_states(target)
            hard = [
                state
                for _pr, _comment, state in target_states
                if state["blocked"] and state["block_level"] == "HARD"
            ]
            if hard:
                write_output(args.github_output, "found", "false")
                write_output(args.github_output, "hard_blocked", "true")
                write_output(args.github_output, "hard_blocked_pr", str(min(s["pr"] for s in hard)))
                return
            now = self.clock().astimezone(timezone.utc)
            candidates: list[Candidate] = []
            for pr, comment, state in target_states:
                if pr.get("state") != "open" or pr.get("draft"):
                    continue
                try:
                    candidates.append(self._candidate(pr, comment, state, run_id, now))
                except (EvidenceError, StateError) as exc:
                    print(f"PR #{state['pr']} skipped: {exc}", file=sys.stderr)
            candidates.sort(key=lambda item: (parse_timestamp(item.ready_at), item.number))
            if not candidates:
                write_output(args.github_output, "found", "false")
                write_output(args.github_output, "hard_blocked", "false")
                return
            selected = candidates[0]
            state = dict(selected.state)
            state["claim"] = self._new_claim(
                run_id,
                run_attempt,
                selected.head_sha,
                selected.current_base_sha,
                state["validation_check_run_id"],
            )
            state["ready_at"] = selected.ready_at
            state["status"] = "CLAIMED"
            state.pop("merge_block_reason", None)
            try:
                self.store.save(selected.number, state, state_revision(selected.comment))
                _saved_comment, saved_state = self.store.find(selected.number)
                if not saved_state or saved_state.get("claim") != state["claim"]:
                    raise StateConflict("candidate claim was overwritten")
            except StateConflict:
                if retry == 2:
                    raise
                continue
            self._write_candidate_outputs(args.github_output, selected, saved_state)
            return
        raise StateConflict("could not claim a queue candidate")

    def _new_claim(
        self,
        run_id: int,
        run_attempt: int,
        head_sha: str,
        base_sha: str,
        check_id: int,
    ) -> dict[str, Any]:
        claimed = self.clock().astimezone(timezone.utc)
        return {
            "run_id": run_id,
            "run_attempt": run_attempt,
            "claimed_at": format_timestamp(claimed),
            "expires_at": format_timestamp(
                claimed + timedelta(seconds=self.config.claim_ttl_seconds)
            ),
            "head_sha": head_sha,
            "base_sha": base_sha,
            "validation_check_run_id": check_id,
        }

    def _write_candidate_outputs(
        self, path: Optional[str], candidate: Candidate, state: Mapping[str, Any]
    ) -> None:
        outputs = {
            "found": "true",
            "hard_blocked": "false",
            "pr_number": str(candidate.number),
            "head_sha": candidate.head_sha,
            "validation_id": state["validation_id"],
            "validation_check_run_id": str(state["validation_check_run_id"]),
            "validated_base_sha": state["base_sha"],
            "selected_base_sha": candidate.current_base_sha,
            "ready_at": candidate.ready_at,
            "claim_expires_at": state["claim"]["expires_at"],
        }
        for key, value in outputs.items():
            write_output(path, key, value)

    def verify_selected(self, args: argparse.Namespace) -> None:
        run_id = _positive_int(args.run_id, "run_id")
        run_attempt = _positive_int(args.run_attempt, "run_attempt")
        expected_head = _sha(args.expected_head_sha, "expected_head_sha")
        expected_base = _sha(args.expected_base_sha, "expected_base_sha")
        expected_check = _positive_int(args.expected_check_run_id, "expected_check_run_id")
        comment, state = self.store.find(args.pr)
        if not comment or not state:
            raise StateError("selected PR has no state")
        if state["head_sha"] != expected_head or state.get("validation_check_run_id") != expected_check:
            raise StateConflict("selected validation changed")
        claim = state.get("claim")
        if not claim or claim["run_id"] != run_id or claim["run_attempt"] != run_attempt:
            raise StateConflict("selected PR is not claimed by this run")
        if claim["head_sha"] != expected_head or claim["base_sha"] != expected_base:
            raise StateConflict("claim does not match the selected head/base")
        hard = self.target_hard_blocks(state["target_branch"])
        if hard:
            raise StateError(f"target is hard-blocked by PR #{hard[0]['pr']}")
        pr = self.get_pr(args.pr)
        candidate = self._candidate(
            pr, comment, state, run_id, self.clock().astimezone(timezone.utc)
        )
        if candidate.current_base_sha != expected_base:
            raise StateConflict("target branch changed after queue selection")
        revision = state_revision(comment)
        state["claim"] = self._new_claim(
            run_id, run_attempt, expected_head, expected_base, expected_check
        )
        state["status"] = "DEPLOYING" if args.phase == "pre-deploy" else "CLAIMED"
        self.store.save(args.pr, state, revision)
        write_output(args.github_output, "verified", "true")

    def defer(self, args: argparse.Namespace) -> None:
        reason = _safe_text(args.reason, "reason")
        is_hard = reason in HARD_BLOCK_REASONS or reason.startswith("post_deploy_")
        if not is_hard and reason not in SOFT_BLOCK_REASONS:
            raise StateError(f"unsupported defer reason: {reason}")
        expected_head = _sha(args.expected_head_sha, "expected_head_sha")
        run_id = _positive_int(args.run_id, "run_id")
        comment, state = self.store.find(args.pr)
        if not comment or not state:
            raise StateError("cannot defer a PR without state")
        claim = state.get("claim")
        stale = (
            state["head_sha"] != expected_head
            or not claim
            or claim["run_id"] != run_id
            or (
                args.expected_check_run_id is not None
                and state.get("validation_check_run_id") != args.expected_check_run_id
            )
        )
        if stale and not is_hard:
            print("stale soft defer ignored", file=sys.stderr)
            return
        revision = state_revision(comment)
        state.update(
            {
                "ready_at": None,
                "blocked": True,
                "block_level": "HARD" if is_hard else "SOFT",
                "blocked_at": self.now(),
                "blocked_reason": reason,
                "block_run_id": run_id,
                "block_head_sha": expected_head,
                "status": "HARD_BLOCKED" if is_hard else "BLOCKED",
                "claim": None,
            }
        )
        self.store.save(args.pr, state, revision)

    def recover(self, args: argparse.Namespace) -> None:
        expected_head = _sha(args.expected_head_sha, "expected_head_sha")
        run_id = _positive_int(args.run_id, "run_id")
        actor = _safe_text(args.actor, "actor", max_length=39)
        if not LOGIN_RE.fullmatch(actor):
            raise StateError("actor is not a GitHub login")
        ticket = _safe_text(args.ticket, "ticket")
        reason = _safe_text(args.reason, "reason")
        comment, state = self.store.find(args.pr)
        if not comment or not state:
            raise StateError("cannot recover a PR without state")
        if not state["blocked"] or state["block_level"] != "HARD":
            raise StateError("only a hard-blocked PR can be recovered")
        pr = self.get_pr(args.pr)
        current_head = _sha((pr.get("head") or {}).get("sha"), "current PR head")
        if current_head != expected_head:
            raise StateConflict("pull request head does not match recovery request")
        target = _target((pr.get("base") or {}).get("ref"), self.config.allowed_targets)
        base = self.current_base_sha(target)
        revision = state_revision(comment)
        recovered = {
            "schema_version": STATE_SCHEMA_VERSION,
            "pr": args.pr,
            "target_branch": target,
            "head_sha": current_head,
            "base_sha": base,
            "validation_id": None,
            "quality_run_id": None,
            "quality_run_attempt": None,
            "validation_run_id": None,
            "validation_run_attempt": None,
            "validation_check_run_id": None,
            "validated_at": None,
            "ready_at": None,
            "status": "WAITING_VALIDATION",
            "blocked": False,
            "block_level": None,
            "blocked_at": None,
            "blocked_reason": None,
            "block_run_id": None,
            "block_head_sha": None,
            "claim": None,
            "recovery": {
                "run_id": run_id,
                "actor": actor,
                "at": self.now(),
                "ticket": ticket,
                "reason": reason,
            },
            "merge_block_reason": None,
        }
        self.store.save(args.pr, recovered, revision)


def write_output(path: Optional[str], key: str, value: Any) -> None:
    if not isinstance(key, str) or not OUTPUT_KEY_RE.fullmatch(key):
        raise StateError("invalid GitHub output key")
    if not isinstance(value, str):
        value = str(value)
    if any(char in value for char in "\r\n\0"):
        raise StateError(f"GitHub output {key} contains a control character")
    if path:
        with open(path, "a", encoding="utf-8") as handle:
            handle.write(f"{key}={value}\n")
    else:
        print(f"{key}={value}")


def _event_quality_provenance(env: Mapping[str, str]) -> tuple[Optional[int], Optional[int]]:
    path = env.get("GITHUB_EVENT_PATH")
    if not path:
        return None, None
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
        run = payload.get("workflow_run") or {}
        return int(run["id"]), int(run.get("run_attempt", 1))
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError):
        return None, None


def _resolve_runtime_args(args: argparse.Namespace, env: Mapping[str, str]) -> None:
    quality_id, quality_attempt = _event_quality_provenance(env)
    fallbacks = {
        "quality_run_id": quality_id,
        "quality_run_attempt": quality_attempt,
        "validation_run_id": env.get("GITHUB_RUN_ID"),
        "validation_run_attempt": env.get("GITHUB_RUN_ATTEMPT", "1"),
        "run_id": env.get("GITHUB_RUN_ID"),
        "run_attempt": env.get("GITHUB_RUN_ATTEMPT", "1"),
        "actor": env.get("GITHUB_ACTOR"),
    }
    for name, fallback in fallbacks.items():
        if hasattr(args, name) and getattr(args, name) is None and fallback is not None:
            try:
                fallback = int(fallback) if name.endswith(("_id", "_attempt")) else fallback
            except (TypeError, ValueError) as exc:
                raise ConfigurationError(f"{name} must be an integer") from exc
            setattr(args, name, fallback)
    for name in (
        "quality_run_id",
        "quality_run_attempt",
        "validation_run_id",
        "validation_run_attempt",
        "run_id",
        "run_attempt",
        "actor",
    ):
        if hasattr(args, name) and getattr(args, name) is None:
            raise ConfigurationError(
                f"--{name.replace('_', '-')} or its GitHub environment value is required"
            )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)

    record = commands.add_parser("record-validation")
    record.add_argument("--pr", required=True, type=int)
    record.add_argument("--target-branch", required=True)
    record.add_argument("--head-sha", required=True)
    record.add_argument("--base-sha", required=True)
    record.add_argument("--validation-id", required=True)
    record.add_argument("--quality-run-id", type=int)
    record.add_argument("--quality-run-attempt", type=int)
    record.add_argument("--validation-run-id", type=int)
    record.add_argument("--validation-run-attempt", type=int)
    record.set_defaults(method="record_validation")

    ready = commands.add_parser("sync-ready")
    ready.add_argument("--pr", required=True, type=int)
    ready.set_defaults(method="sync_ready")

    select = commands.add_parser("select-next")
    select.add_argument("--target-branch", required=True)
    select.add_argument("--github-output")
    select.add_argument("--run-id", type=int)
    select.add_argument("--run-attempt", type=int)
    select.set_defaults(method="select_next")

    verify = commands.add_parser("verify-selected")
    verify.add_argument("--pr", required=True, type=int)
    verify.add_argument("--expected-head-sha", required=True)
    verify.add_argument("--expected-base-sha", required=True)
    verify.add_argument("--expected-check-run-id", required=True, type=int)
    verify.add_argument("--phase", required=True, choices=("pre-deploy", "pre-merge"))
    verify.add_argument("--github-output")
    verify.add_argument("--run-id", type=int)
    verify.add_argument("--run-attempt", type=int)
    verify.set_defaults(method="verify_selected")

    blocked = commands.add_parser("defer")
    blocked.add_argument("--pr", required=True, type=int)
    blocked.add_argument("--reason", required=True)
    blocked.add_argument("--expected-head-sha", required=True)
    blocked.add_argument("--expected-check-run-id", type=int)
    blocked.add_argument("--run-id", type=int)
    blocked.set_defaults(method="defer")

    recover = commands.add_parser("recover")
    recover.add_argument("--pr", required=True, type=int)
    recover.add_argument("--expected-head-sha", required=True)
    recover.add_argument("--ticket", required=True)
    recover.add_argument("--reason", required=True)
    recover.add_argument("--actor")
    recover.add_argument("--run-id", type=int)
    recover.set_defaults(method="recover")
    return parser


def main(argv: Optional[list[str]] = None, env: Mapping[str, str] = os.environ) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    _resolve_runtime_args(args, env)
    config = Config.from_env(env)
    orchestrator = QueueOrchestrator(GitHubClient(config), config)
    getattr(orchestrator, args.method)(args)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except QueueError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
