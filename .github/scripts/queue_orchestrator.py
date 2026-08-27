import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone


MARKER = "<!-- evolua-salesforce-ci-state -->"

TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
REPOSITORY = os.environ.get("GITHUB_REPOSITORY")

API_BASE = os.environ.get(
    "GITHUB_API_URL",
    "https://api.github.com",
).rstrip("/")

GRAPHQL_URL = os.environ.get(
    "GITHUB_GRAPHQL_URL",
    "https://api.github.com/graphql",
)

STATE_AUTHOR = os.environ.get(
    "CI_STATE_AUTHOR",
    "github-actions[bot]",
)

REQUIRED_APPROVALS = int(
    os.environ.get(
        "REQUIRED_APPROVALS",
        "1",
    )
)

HARD_BLOCK_REASONS = {
    "post_deploy_merge_failure",
    "post_deploy_target_changed",
}

DECISIVE_REVIEW_STATES = {
    "APPROVED",
    "CHANGES_REQUESTED",
    "DISMISSED",
}

ALLOWED_MERGE_STATES = {
    "CLEAN",
    "HAS_HOOKS",
    "BEHIND",
}


if not TOKEN:
    raise SystemExit(
        "GITHUB_TOKEN or GH_TOKEN is required"
    )

if not REPOSITORY or "/" not in REPOSITORY:
    raise SystemExit(
        "GITHUB_REPOSITORY is required"
    )

if REQUIRED_APPROVALS < 1:
    raise SystemExit(
        "REQUIRED_APPROVALS must be at least 1"
    )


OWNER, REPO = REPOSITORY.split("/", 1)


def utc_now():
    return format_timestamp(
        datetime.now(timezone.utc)
    )


def parse_timestamp(value):
    if not value:
        return None

    normalized = value

    if normalized.endswith("Z"):
        normalized = (
            normalized[:-1]
            + "+00:00"
        )

    result = datetime.fromisoformat(
        normalized
    )

    if result.tzinfo is None:
        result = result.replace(
            tzinfo=timezone.utc
        )

    return result.astimezone(
        timezone.utc
    )


def format_timestamp(value):
    return (
        value
        .astimezone(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def later_timestamp(*values):
    parsed = [
        parse_timestamp(value)
        for value in values
        if value
    ]

    if not parsed:
        return None

    return format_timestamp(
        max(parsed)
    )


def request(
    method,
    path_or_url,
    payload=None,
):
    if path_or_url.startswith("http"):
        url = path_or_url
    else:
        url = f"{API_BASE}{path_or_url}"

    body = None

    if payload is not None:
        body = json.dumps(
            payload
        ).encode("utf-8")

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {TOKEN}",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "evolua-salesforce-queue-orchestrator",
    }

    if body is not None:
        headers["Content-Type"] = (
            "application/json"
        )

    last_error = None

    for attempt in range(4):
        req = urllib.request.Request(
            url,
            data=body,
            headers=headers,
            method=method,
        )

        try:
            with urllib.request.urlopen(
                req,
                timeout=30,
            ) as response:
                response_body = (
                    response.read()
                    .decode("utf-8")
                )

                if not response_body:
                    return None

                return json.loads(
                    response_body
                )

        except urllib.error.HTTPError as exc:
            error_body = (
                exc.read()
                .decode(
                    "utf-8",
                    errors="replace",
                )
            )

            last_error = RuntimeError(
                f"GitHub API {exc.code}: {error_body}"
            )

            retryable = (
                exc.code == 429
                or 500 <= exc.code < 600
            )

            if not retryable or attempt == 3:
                raise last_error from exc

        except urllib.error.URLError as exc:
            last_error = RuntimeError(
                f"GitHub API network error: {exc}"
            )

            if attempt == 3:
                raise last_error from exc

        time.sleep(2 ** attempt)

    raise last_error


def paginate(
    path,
    params=None,
):
    params = dict(params or {})
    page = 1
    results = []

    while True:
        query = dict(params)
        query["per_page"] = 100
        query["page"] = page

        url = (
            f"{path}?"
            f"{urllib.parse.urlencode(query)}"
        )

        data = request(
            "GET",
            url,
        )

        if not isinstance(data, list):
            raise RuntimeError(
                f"Expected list from {path}"
            )

        results.extend(data)

        if len(data) < 100:
            return results

        page += 1


def get_pr(number):
    return request(
        "GET",
        f"/repos/{REPOSITORY}/pulls/{number}",
    )


def review_decision(number):
    query = """
    query(
      $owner: String!,
      $repo: String!,
      $number: Int!
    ) {
      repository(
        owner: $owner,
        name: $repo
      ) {
        pullRequest(number: $number) {
          reviewDecision
        }
      }
    }
    """

    payload = {
        "query": query,
        "variables": {
            "owner": OWNER,
            "repo": REPO,
            "number": int(number),
        },
    }

    data = request(
        "POST",
        GRAPHQL_URL,
        payload,
    )

    errors = data.get("errors")

    if errors:
        raise RuntimeError(
            json.dumps(errors)
        )

    pull_request = (
        data
        .get("data", {})
        .get("repository", {})
        .get("pullRequest")
    )

    if not pull_request:
        return None

    return pull_request.get(
        "reviewDecision"
    )


def approval_time(
    number,
    head_sha,
):
    reviews = paginate(
        f"/repos/{REPOSITORY}/pulls/{number}/reviews"
    )

    latest_by_user = {}

    for review in reviews:
        if review.get("commit_id") != head_sha:
            continue

        state = review.get("state")

        if state not in DECISIVE_REVIEW_STATES:
            continue

        user = (
            review.get("user")
            or {}
        ).get("login")

        submitted_at = review.get(
            "submitted_at"
        )

        if not user or not submitted_at:
            continue

        previous = latest_by_user.get(user)

        if previous is None:
            latest_by_user[user] = review
            continue

        previous_time = parse_timestamp(
            previous.get("submitted_at")
        )
        current_time = parse_timestamp(
            submitted_at
        )

        if current_time > previous_time:
            latest_by_user[user] = review

    latest_reviews = list(
        latest_by_user.values()
    )

    if any(
        review.get("state")
        == "CHANGES_REQUESTED"
        for review in latest_reviews
    ):
        return None

    approvals = sorted(
        [
            parse_timestamp(
                review["submitted_at"]
            )
            for review in latest_reviews
            if review.get("state")
            == "APPROVED"
        ]
    )

    if len(approvals) < REQUIRED_APPROVALS:
        return None

    decision = review_decision(number)

    if decision in {
        "CHANGES_REQUESTED",
        "REVIEW_REQUIRED",
    }:
        return None

    threshold = approvals[
        REQUIRED_APPROVALS - 1
    ]

    return format_timestamp(threshold)


def merge_readiness(
    number,
    head_sha,
):
    query = """
    query(
      $owner: String!,
      $repo: String!,
      $number: Int!
    ) {
      repository(
        owner: $owner,
        name: $repo
      ) {
        pullRequest(number: $number) {
          state
          isDraft
          headRefOid
          baseRefName
          mergeable
          mergeStateStatus
          reviewDecision
        }
      }
    }
    """

    payload = {
        "query": query,
        "variables": {
            "owner": OWNER,
            "repo": REPO,
            "number": int(number),
        },
    }

    pull_request = None

    for attempt in range(3):
        data = request(
            "POST",
            GRAPHQL_URL,
            payload,
        )

        errors = data.get("errors")

        if errors:
            raise RuntimeError(
                json.dumps(errors)
            )

        pull_request = (
            data
            .get("data", {})
            .get("repository", {})
            .get("pullRequest")
        )

        if not pull_request:
            return False, "pull_request_not_found"

        mergeable = pull_request.get(
            "mergeable"
        )
        merge_state = pull_request.get(
            "mergeStateStatus"
        )

        if (
            mergeable != "UNKNOWN"
            and merge_state != "UNKNOWN"
        ):
            break

        if attempt < 2:
            time.sleep(2)

    if pull_request.get("state") != "OPEN":
        return False, "pull_request_not_open"

    if pull_request.get("isDraft"):
        return False, "pull_request_is_draft"

    if pull_request.get("headRefOid") != head_sha:
        return False, "head_changed"

    if pull_request.get("mergeable") != "MERGEABLE":
        return (
            False,
            f"mergeable_{pull_request.get('mergeable')}",
        )

    merge_state = pull_request.get(
        "mergeStateStatus"
    )

    if merge_state not in ALLOWED_MERGE_STATES:
        return (
            False,
            f"merge_state_{merge_state}",
        )

    if pull_request.get(
        "reviewDecision"
    ) in {
        "CHANGES_REQUESTED",
        "REVIEW_REQUIRED",
    }:
        return False, "review_not_satisfied"

    return True, merge_state


def parse_state(body):
    if MARKER not in body:
        return None

    raw = (
        body
        .split(MARKER, 1)[1]
        .strip()
    )

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def find_state_comment(number):
    comments = paginate(
        f"/repos/{REPOSITORY}/issues/{number}/comments"
    )

    for comment in reversed(comments):
        user = comment.get("user") or {}
        login = user.get("login")
        user_type = user.get("type")
        body = comment.get("body") or ""

        if (
            login == STATE_AUTHOR
            and user_type == "Bot"
            and MARKER in body
        ):
            state = parse_state(body)

            if state is not None:
                return comment, state

    return None, None


def save_state(
    number,
    state,
):
    comment, _ = find_state_comment(number)

    body = (
        f"{MARKER}\n"
        f"{json.dumps(state, sort_keys=True, indent=2)}"
    )

    if comment:
        request(
            "PATCH",
            (
                f"/repos/{REPOSITORY}"
                f"/issues/comments/{comment['id']}"
            ),
            {"body": body},
        )
        return

    request(
        "POST",
        (
            f"/repos/{REPOSITORY}"
            f"/issues/{number}/comments"
        ),
        {"body": body},
    )


def record_validation(args):
    _, old_state = find_state_comment(args.pr)
    old_state = old_state or {}

    if (
        old_state.get("blocked")
        and old_state.get("block_level")
        == "HARD"
    ):
        raise RuntimeError(
            "Pull Request is hard-blocked because Salesforce may already differ from GitHub. Manual recovery is required before this PR can be processed again."
        )

    state = {
        "pr": int(args.pr),
        "target_branch": args.target_branch,
        "head_sha": args.head_sha,
        "base_sha": args.base_sha,
        "validation_id": args.validation_id,
        "validated_at": utc_now(),
        "ready_at": None,
        "blocked": False,
        "block_level": None,
        "blocked_at": None,
        "blocked_reason": None,
        "status": "VALIDATED",
    }

    save_state(args.pr, state)


def sync_ready(args):
    pr = get_pr(args.pr)
    _, state = find_state_comment(args.pr)

    if not state:
        return

    if pr.get("state") != "open":
        state["ready_at"] = None
        state["status"] = "CLOSED"
        save_state(args.pr, state)
        return

    if state.get("blocked"):
        state["ready_at"] = None
        state["status"] = (
            "HARD_BLOCKED"
            if state.get("block_level") == "HARD"
            else "BLOCKED"
        )
        save_state(args.pr, state)
        return

    current_head = pr["head"]["sha"]

    valid_validation = (
        state.get("head_sha")
        == current_head
        and state.get("validated_at")
    )

    if not valid_validation:
        state["ready_at"] = None
        state["status"] = "WAITING_VALIDATION"
        save_state(args.pr, state)
        return

    approved_at = approval_time(
        args.pr,
        current_head,
    )

    if not approved_at:
        state["ready_at"] = None
        state["status"] = "VALIDATED"
        save_state(args.pr, state)
        return

    ready_at = later_timestamp(
        state["validated_at"],
        approved_at,
    )

    state["ready_at"] = ready_at
    state["status"] = "READY"
    save_state(args.pr, state)


def select_next(args):
    pull_requests = paginate(
        f"/repos/{REPOSITORY}/pulls",
        {
            "state": "open",
            "base": args.target_branch,
            "sort": "created",
            "direction": "asc",
        },
    )

    candidates = []

    for pr in pull_requests:
        if pr.get("draft"):
            continue

        number = pr["number"]
        head_sha = pr["head"]["sha"]

        _, state = find_state_comment(number)

        if not state:
            continue

        if state.get("target_branch") != args.target_branch:
            continue

        if state.get("blocked"):
            continue

        if state.get("head_sha") != head_sha:
            if state.get("status") != "WAITING_VALIDATION":
                state["ready_at"] = None
                state["status"] = "WAITING_VALIDATION"
                save_state(number, state)
            continue

        validated_at = state.get("validated_at")

        if not validated_at:
            continue

        approved_at = approval_time(
            number,
            head_sha,
        )

        if not approved_at:
            if (
                state.get("ready_at") is not None
                or state.get("status") != "VALIDATED"
            ):
                state["ready_at"] = None
                state["status"] = "VALIDATED"
                save_state(number, state)
            continue

        ready_at = later_timestamp(
            validated_at,
            approved_at,
        )

        merge_ready, merge_reason = (
            merge_readiness(
                number,
                head_sha,
            )
        )

        if not merge_ready:
            state["ready_at"] = ready_at
            state["status"] = "WAITING_MERGE"
            state["merge_block_reason"] = (
                merge_reason
            )
            save_state(number, state)
            print(
                f"PR #{number} skipped: {merge_reason}",
                file=sys.stderr,
            )
            continue

        state.pop(
            "merge_block_reason",
            None,
        )

        if (
            state.get("ready_at") != ready_at
            or state.get("status") != "READY"
        ):
            state["ready_at"] = ready_at
            state["status"] = "READY"
            save_state(number, state)

        candidates.append(
            (
                parse_timestamp(ready_at),
                number,
                head_sha,
                state,
            )
        )

    candidates.sort(
        key=lambda item: (
            item[0],
            item[1],
        )
    )

    if not candidates:
        write_output(
            args.github_output,
            "found",
            "false",
        )
        return

    (
        ready_at_dt,
        number,
        head_sha,
        state,
    ) = candidates[0]

    write_output(
        args.github_output,
        "found",
        "true",
    )
    write_output(
        args.github_output,
        "pr_number",
        str(number),
    )
    write_output(
        args.github_output,
        "head_sha",
        head_sha,
    )
    write_output(
        args.github_output,
        "validation_id",
        state.get("validation_id") or "",
    )
    write_output(
        args.github_output,
        "validated_base_sha",
        state.get("base_sha") or "",
    )
    write_output(
        args.github_output,
        "ready_at",
        format_timestamp(ready_at_dt),
    )


def defer(args):
    _, state = find_state_comment(args.pr)

    if not state:
        return

    is_hard = (
        args.reason in HARD_BLOCK_REASONS
        or args.reason.startswith(
            "post_deploy_"
        )
    )

    state["ready_at"] = None
    state["blocked"] = True
    state["block_level"] = (
        "HARD"
        if is_hard
        else "SOFT"
    )
    state["blocked_at"] = utc_now()
    state["blocked_reason"] = args.reason
    state["status"] = (
        "HARD_BLOCKED"
        if is_hard
        else "BLOCKED"
    )

    save_state(args.pr, state)


def write_output(
    path,
    key,
    value,
):
    if path:
        with open(
            path,
            "a",
            encoding="utf-8",
        ) as handle:
            handle.write(
                f"{key}={value}\n"
            )
        return

    print(f"{key}={value}")


def build_parser():
    parser = argparse.ArgumentParser()

    commands = parser.add_subparsers(
        dest="command",
        required=True,
    )

    record = commands.add_parser(
        "record-validation"
    )
    record.add_argument(
        "--pr",
        required=True,
        type=int,
    )
    record.add_argument(
        "--target-branch",
        required=True,
    )
    record.add_argument(
        "--head-sha",
        required=True,
    )
    record.add_argument(
        "--base-sha",
        required=True,
    )
    record.add_argument(
        "--validation-id",
        required=True,
    )
    record.set_defaults(
        func=record_validation
    )

    ready = commands.add_parser(
        "sync-ready"
    )
    ready.add_argument(
        "--pr",
        required=True,
        type=int,
    )
    ready.set_defaults(
        func=sync_ready
    )

    select = commands.add_parser(
        "select-next"
    )
    select.add_argument(
        "--target-branch",
        required=True,
    )
    select.add_argument(
        "--github-output",
    )
    select.set_defaults(
        func=select_next
    )

    blocked = commands.add_parser(
        "defer"
    )
    blocked.add_argument(
        "--pr",
        required=True,
        type=int,
    )
    blocked.add_argument(
        "--reason",
        required=True,
    )
    blocked.set_defaults(
        func=defer
    )

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(
            str(exc),
            file=sys.stderr,
        )
        raise
