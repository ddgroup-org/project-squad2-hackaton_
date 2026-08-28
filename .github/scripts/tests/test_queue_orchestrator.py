"""Offline unit tests for the pull-request queue orchestrator.

These tests exercise the trust boundary of the orchestrator: everything that
parses or validates data the CI job did not produce itself (issue comments,
GitHub API responses, CLI arguments, environment variables). No network access
and no Salesforce CLI are required.
"""

import io
import json
import os
import sys
import tempfile
import unittest
import urllib.error
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import queue_orchestrator as qo  # noqa: E402


SHA_A = "a" * 40
SHA_B = "b" * 40
SHA_C = "c" * 40
JOB_ID = "0Af000000000001"


def make_state(**overrides):
    """A minimal state that validate_state accepts, plus overrides."""
    state = {
        "schema_version": qo.STATE_SCHEMA_VERSION,
        "pr": 7,
        "target_branch": "dev",
        "head_sha": SHA_A,
        "base_sha": SHA_B,
        "validation_id": JOB_ID,
        "quality_run_id": 100,
        "quality_run_attempt": 1,
        "validation_run_id": 200,
        "validation_run_attempt": 1,
        "validation_check_run_id": 300,
        "validated_at": "2026-08-27T10:00:00Z",
        "ready_at": None,
        "status": "VALIDATED",
        "blocked": False,
    }
    state.update(overrides)
    return state


def config(**overrides):
    values = {"token": "t0ken", "repository": "ddgroup-org/repo"}
    values.update(overrides)
    return qo.Config(**values)


class ConfigFromEnvTests(unittest.TestCase):
    def test_requires_a_token(self):
        with self.assertRaises(qo.ConfigurationError):
            qo.Config.from_env({"GITHUB_REPOSITORY": "o/r"})

    def test_accepts_gh_token_alias(self):
        cfg = qo.Config.from_env({"GH_TOKEN": "x", "GITHUB_REPOSITORY": "o/r"})
        self.assertEqual(cfg.owner, "o")
        self.assertEqual(cfg.repo, "r")

    def test_rejects_malformed_repository(self):
        for repository in ("", "owner", "owner/", "/repo", "a/b/c", "o/r\n"):
            with self.subTest(repository=repository):
                with self.assertRaises(qo.ConfigurationError):
                    qo.Config.from_env({"GITHUB_TOKEN": "x", "GITHUB_REPOSITORY": repository})

    def test_graphql_url_follows_api_base_by_default(self):
        cfg = qo.Config.from_env(
            {
                "GITHUB_TOKEN": "x",
                "GITHUB_REPOSITORY": "o/r",
                "GITHUB_API_URL": "https://ghe.example.com/api/v3/",
            }
        )
        self.assertEqual(cfg.api_base, "https://ghe.example.com/api/v3")
        self.assertEqual(cfg.graphql_url, "https://ghe.example.com/api/v3/graphql")

    def test_rejects_non_positive_required_approvals(self):
        for value in ("0", "-1", "two", ""):
            with self.subTest(value=value):
                with self.assertRaises(qo.ConfigurationError):
                    qo.Config.from_env(
                        {
                            "GITHUB_TOKEN": "x",
                            "GITHUB_REPOSITORY": "o/r",
                            "REQUIRED_APPROVALS": value,
                        }
                    )


class TimestampTests(unittest.TestCase):
    def test_parses_zulu_and_offset_forms_to_utc(self):
        self.assertEqual(
            qo.parse_timestamp("2026-08-27T12:00:00Z"),
            qo.parse_timestamp("2026-08-27T09:00:00-03:00"),
        )

    def test_rejects_naive_timestamp(self):
        with self.assertRaises(qo.StateError):
            qo.parse_timestamp("2026-08-27T12:00:00")

    def test_rejects_non_string_and_control_characters(self):
        for value in (None, 17, "", "2026-08-27T12:00:00Z\n"):
            with self.subTest(value=value):
                with self.assertRaises(qo.StateError):
                    qo.parse_timestamp(value)

    def test_format_drops_microseconds_and_uses_zulu(self):
        moment = datetime(2026, 8, 27, 12, 0, 0, 123456, tzinfo=timezone.utc)
        self.assertEqual(qo.format_timestamp(moment), "2026-08-27T12:00:00Z")

    def test_format_rejects_naive_datetime(self):
        with self.assertRaises(qo.StateError):
            qo.format_timestamp(datetime(2026, 8, 27, 12, 0, 0))

    def test_later_timestamp_picks_the_maximum(self):
        self.assertEqual(
            qo.later_timestamp("2026-08-27T10:00:00Z", "2026-08-27T11:00:00Z"),
            "2026-08-27T11:00:00Z",
        )

    def test_later_timestamp_requires_a_value(self):
        with self.assertRaises(qo.StateError):
            qo.later_timestamp()


class FieldValidatorTests(unittest.TestCase):
    def test_sha_must_be_forty_lowercase_hex(self):
        self.assertEqual(qo._sha(SHA_A, "head_sha"), SHA_A)
        for value in ("A" * 40, "a" * 39, "a" * 41, "", None, "g" * 40):
            with self.subTest(value=value):
                with self.assertRaises(qo.StateError):
                    qo._sha(value, "head_sha")

    def test_salesforce_job_id_accepts_15_and_18_characters(self):
        self.assertEqual(qo._sf_job_id(JOB_ID), JOB_ID)
        self.assertEqual(qo._sf_job_id(JOB_ID + "AAA"), JOB_ID + "AAA")
        for value in ("0Af", "0Xf000000000001", JOB_ID + "A", None):
            with self.subTest(value=value):
                with self.assertRaises(qo.StateError):
                    qo._sf_job_id(value)

    def test_positive_int_rejects_bool(self):
        # bool is a subclass of int; letting True through would corrupt run ids.
        with self.assertRaises(qo.StateError):
            qo._positive_int(True, "pr")
        with self.assertRaises(qo.StateError):
            qo._positive_int(0, "pr")
        self.assertEqual(qo._positive_int(3, "pr"), 3)

    def test_safe_text_rejects_newlines_and_overlong_values(self):
        self.assertEqual(qo._safe_text("  ok  ", "reason"), "ok")
        for value in ("", "   ", "a\nb", "a\r", "x" * 201, None):
            with self.subTest(value=value):
                with self.assertRaises(qo.StateError):
                    qo._safe_text(value, "reason")

    def test_target_branch_allowlist(self):
        self.assertEqual(qo._target("main"), "main")
        for value in ("Main", "dev2", "", None):
            with self.subTest(value=value):
                with self.assertRaises(qo.StateError):
                    qo._target(value)


class ValidateStateTests(unittest.TestCase):
    def test_accepts_a_well_formed_state(self):
        state = qo.validate_state(make_state(), expected_pr=7)
        self.assertEqual(state["status"], "VALIDATED")

    def test_rejects_unknown_fields(self):
        with self.assertRaises(qo.StateError):
            qo.validate_state(make_state(injected="anything"))

    def test_rejects_wrong_schema_version(self):
        with self.assertRaises(qo.StateError):
            qo.validate_state(make_state(schema_version=qo.STATE_SCHEMA_VERSION + 1))

    def test_rejects_state_belonging_to_another_pull_request(self):
        with self.assertRaises(qo.StateError):
            qo.validate_state(make_state(), expected_pr=8)

    def test_rejects_partial_validation_evidence(self):
        state = make_state()
        del state["validation_check_run_id"]
        with self.assertRaises(qo.StateError):
            qo.validate_state(state)

    def test_status_requiring_evidence_cannot_omit_it(self):
        state = {
            "schema_version": qo.STATE_SCHEMA_VERSION,
            "pr": 7,
            "target_branch": "dev",
            "head_sha": SHA_A,
            "base_sha": SHA_B,
            "status": "READY",
            "blocked": False,
        }
        with self.assertRaises(qo.StateError):
            qo.validate_state(state)

    def test_waiting_validation_may_omit_evidence(self):
        state = {
            "schema_version": qo.STATE_SCHEMA_VERSION,
            "pr": 7,
            "target_branch": "dev",
            "head_sha": SHA_A,
            "base_sha": SHA_B,
            "status": "WAITING_VALIDATION",
            "blocked": False,
        }
        self.assertEqual(qo.validate_state(state)["status"], "WAITING_VALIDATION")

    def test_blocked_state_requires_level_time_and_reason(self):
        with self.assertRaises(qo.StateError):
            qo.validate_state(make_state(status="BLOCKED", blocked=True))
        state = qo.validate_state(
            make_state(
                status="BLOCKED",
                blocked=True,
                block_level="SOFT",
                blocked_at="2026-08-27T11:00:00Z",
                blocked_reason="validation_or_deploy_failure",
            )
        )
        self.assertEqual(state["block_level"], "SOFT")

    def test_unblocked_state_cannot_retain_block_fields(self):
        with self.assertRaises(qo.StateError):
            qo.validate_state(make_state(blocked=False, block_level="SOFT"))

    def test_rejects_invalid_status(self):
        with self.assertRaises(qo.StateError):
            qo.validate_state(make_state(status="ALMOST_READY"))

    def test_rejects_non_boolean_blocked(self):
        with self.assertRaises(qo.StateError):
            qo.validate_state(make_state(blocked="false"))


class ClaimAndRecoveryTests(unittest.TestCase):
    def claim(self, **overrides):
        claim = {
            "run_id": 900,
            "run_attempt": 1,
            "claimed_at": "2026-08-27T10:00:00Z",
            "expires_at": "2026-08-27T14:00:00Z",
            "head_sha": SHA_A,
            "base_sha": SHA_B,
            "validation_check_run_id": 300,
        }
        claim.update(overrides)
        return claim

    def test_accepts_a_matching_claim(self):
        state = qo.validate_state(make_state(claim=self.claim()))
        self.assertEqual(state["claim"]["run_id"], 900)

    def test_rejects_claim_for_another_head(self):
        with self.assertRaises(qo.StateError):
            qo.validate_state(make_state(claim=self.claim(head_sha=SHA_C)))

    def test_rejects_claim_for_another_validation(self):
        with self.assertRaises(qo.StateError):
            qo.validate_state(make_state(claim=self.claim(validation_check_run_id=999)))

    def test_rejects_expiry_before_acquisition(self):
        with self.assertRaises(qo.StateError):
            qo.validate_state(
                make_state(claim=self.claim(expires_at="2026-08-27T09:00:00Z"))
            )

    def test_rejects_claim_with_extra_fields(self):
        with self.assertRaises(qo.StateError):
            qo.validate_state(make_state(claim=self.claim(extra=1)))

    def test_recovery_requires_a_github_login(self):
        recovery = {
            "run_id": 5,
            "actor": "not a login",
            "at": "2026-08-27T10:00:00Z",
            "ticket": "OPS-1",
            "reason": "manual reconciliation",
        }
        with self.assertRaises(qo.StateError):
            qo.validate_recovery(recovery)
        recovery["actor"] = "octocat"
        self.assertEqual(qo.validate_recovery(recovery)["actor"], "octocat")


class StateCommentTests(unittest.TestCase):
    def test_marker_must_be_the_first_line(self):
        payload = json.dumps(make_state())
        with self.assertRaises(qo.StateError):
            qo.parse_state(f"chatty preamble\n{qo.MARKER}\n{payload}")

    def test_a_single_leading_space_does_not_smuggle_state_through(self):
        # Guards the `startswith` check specifically: with a one-character
        # preamble the payload still slices to valid JSON, so a containment
        # check ("marker anywhere") would accept this body.
        payload = json.dumps(make_state())
        body = f" {qo.MARKER}\n{payload}"
        self.assertEqual(json.loads(body[len(qo.MARKER) + 1 :]), json.loads(payload))
        with self.assertRaises(qo.StateError):
            qo.parse_state(body)

    def test_rejects_invalid_json_and_oversized_bodies(self):
        with self.assertRaises(qo.StateError):
            qo.parse_state(f"{qo.MARKER}\nnot json")
        with self.assertRaises(qo.StateError):
            qo.parse_state(f"{qo.MARKER}\n" + "x" * 60_001)

    def test_render_then_parse_round_trips(self):
        body = qo.render_state(make_state())
        self.assertTrue(body.startswith(f"{qo.MARKER}\n"))
        self.assertEqual(qo.parse_state(body)["pr"], 7)

    def test_render_refuses_to_serialise_invalid_state(self):
        with self.assertRaises(qo.StateError):
            qo.render_state(make_state(status="NOPE"))

    def test_state_revision_uses_updated_at_then_created_at(self):
        revision = qo.state_revision(
            {"id": 5, "created_at": "2026-08-27T10:00:00Z", "body": "b"}
        )
        self.assertEqual(revision, (5, "2026-08-27T10:00:00Z", "b"))
        self.assertIsNone(qo.state_revision(None))


class FakeApi:
    """Records requests and replays scripted responses."""

    def __init__(self, comments=None, responses=None):
        self.comments = list(comments or [])
        self.responses = list(responses or [])
        self.calls = []

    def paginate(self, path, params=None):
        self.calls.append(("GET", path))
        return list(self.comments)

    def request(self, method, path, payload=None, **kwargs):
        self.calls.append((method, path))
        if self.responses:
            return self.responses.pop(0)
        return {"id": 1, "body": payload["body"]} if payload else None


def bot_comment(comment_id, state, updated_at="2026-08-27T10:00:00Z"):
    return {
        "id": comment_id,
        "updated_at": updated_at,
        "body": qo.render_state(state),
        "user": {"login": "github-actions[bot]", "type": "Bot", "id": qo.STATE_AUTHOR_ID},
    }


class StateStoreTests(unittest.TestCase):
    def test_ignores_comments_that_are_not_from_the_canonical_bot(self):
        impostor = bot_comment(1, make_state())
        impostor["user"] = {"login": "attacker", "type": "User", "id": 4242}
        store = qo.StateStore(FakeApi(comments=[impostor]), config())
        self.assertEqual(store.find(7), (None, None))

    def test_ignores_a_bot_login_with_the_wrong_account_id(self):
        spoofed = bot_comment(1, make_state())
        spoofed["user"]["id"] = 999
        store = qo.StateStore(FakeApi(comments=[spoofed]), config())
        self.assertEqual(store.find(7), (None, None))

    def test_refuses_to_guess_between_two_canonical_comments(self):
        api = FakeApi(comments=[bot_comment(1, make_state()), bot_comment(2, make_state())])
        with self.assertRaises(qo.StateError):
            qo.StateStore(api, config()).find(7)

    def test_find_returns_validated_state(self):
        api = FakeApi(comments=[bot_comment(1, make_state())])
        comment, state = qo.StateStore(api, config()).find(7)
        self.assertEqual(comment["id"], 1)
        self.assertEqual(state["pr"], 7)

    def test_save_detects_a_concurrent_write(self):
        api = FakeApi(comments=[bot_comment(1, make_state(), "2026-08-27T12:00:00Z")])
        store = qo.StateStore(api, config())
        stale = (1, "2026-08-27T10:00:00Z", "old body")
        with self.assertRaises(qo.StateConflict):
            store.save(7, make_state(), stale)

    def test_save_detects_a_comment_that_appeared_after_the_read(self):
        api = FakeApi(comments=[bot_comment(1, make_state())])
        with self.assertRaises(qo.StateConflict):
            qo.StateStore(api, config()).save(7, make_state(), None)

    def test_save_rejects_a_body_that_does_not_read_back_exactly(self):
        api = FakeApi(comments=[], responses=[{"id": 1, "body": "tampered"}])
        with self.assertRaises(qo.StateConflict):
            qo.StateStore(api, config()).save(7, make_state(), None)

    def test_save_creates_a_comment_when_none_exists(self):
        api = FakeApi(comments=[])
        result = qo.StateStore(api, config()).save(7, make_state(), None)
        self.assertEqual(result["body"], qo.render_state(make_state()))
        self.assertIn(("POST", "/repos/ddgroup-org/repo/issues/7/comments"), api.calls)


class _Response:
    def __init__(self, body):
        self._body = body

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        return False

    def read(self):
        return self._body


def http_error(code, headers=None):
    return urllib.error.HTTPError(
        "https://api.github.com/x", code, "err", headers or {}, io.BytesIO(b"boom")
    )


class GitHubClientTests(unittest.TestCase):
    def client(self, opener):
        self.slept = []
        return qo.GitHubClient(config(), opener=opener, sleeper=self.slept.append)

    def test_refuses_to_send_credentials_to_another_origin(self):
        client = self.client(lambda *a, **k: self.fail("must not be called"))
        with self.assertRaises(qo.ConfigurationError):
            client.request("GET", "https://evil.example.com/steal")

    def test_relative_path_must_be_absolute(self):
        client = self.client(lambda *a, **k: self.fail("must not be called"))
        with self.assertRaises(qo.ConfigurationError):
            client.request("GET", "repos/o/r")

    def test_retries_idempotent_request_until_success(self):
        attempts = []

        def opener(request, timeout=None):
            attempts.append(request.full_url)
            if len(attempts) < 3:
                raise http_error(500)
            return _Response(b'{"ok": true}')

        self.assertEqual(self.client(opener).request("GET", "/x"), {"ok": True})
        self.assertEqual(len(attempts), 3)
        self.assertEqual(self.slept, [1.0, 2.0])

    def test_does_not_retry_a_post(self):
        attempts = []

        def opener(request, timeout=None):
            attempts.append(request.full_url)
            raise http_error(500)

        with self.assertRaises(qo.QueueError):
            self.client(opener).request("POST", "/x", {"a": 1})
        self.assertEqual(len(attempts), 1)

    def test_does_not_retry_a_client_error(self):
        attempts = []

        def opener(request, timeout=None):
            attempts.append(request.full_url)
            raise http_error(404)

        with self.assertRaises(qo.QueueError):
            self.client(opener).request("GET", "/x")
        self.assertEqual(len(attempts), 1)

    def test_honours_retry_after_header_within_bounds(self):
        self.assertEqual(qo._retry_delay({"Retry-After": "5"}, 0), 5.0)
        self.assertEqual(qo._retry_delay({"Retry-After": "9999"}, 0), 60.0)
        self.assertEqual(qo._retry_delay({"Retry-After": "nonsense"}, 2), 4.0)
        self.assertEqual(qo._retry_delay(None, 3), 8.0)

    def test_empty_body_becomes_none(self):
        self.assertIsNone(self.client(lambda *a, **k: _Response(b"")).request("GET", "/x"))

    def test_paginate_stops_on_a_short_page(self):
        pages = [[{"n": i} for i in range(100)], [{"n": 100}]]

        def opener(request, timeout=None):
            return _Response(json.dumps(pages.pop(0)).encode("utf-8"))

        self.assertEqual(len(self.client(opener).paginate("/items")), 101)

    def test_paginate_rejects_a_non_list_payload(self):
        with self.assertRaises(qo.QueueError):
            self.client(lambda *a, **k: _Response(b'{"not": "a list"}')).paginate("/items")


class WriteOutputTests(unittest.TestCase):
    def test_appends_key_value_pairs(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "out")
            qo.write_output(path, "found", "true")
            qo.write_output(path, "pr_number", 7)
            with open(path, encoding="utf-8") as handle:
                self.assertEqual(handle.read(), "found=true\npr_number=7\n")

    def test_rejects_an_invalid_key(self):
        for key in ("2bad", "with-dash", "", "a b"):
            with self.subTest(key=key):
                with self.assertRaises(qo.StateError):
                    qo.write_output(None, key, "v")

    def test_rejects_a_value_that_could_forge_extra_outputs(self):
        with self.assertRaises(qo.StateError):
            qo.write_output(None, "found", "true\nadmin=true")


class RuntimeArgumentTests(unittest.TestCase):
    def test_select_next_fills_run_identity_from_the_environment(self):
        args = qo.build_parser().parse_args(["select-next", "--target-branch", "dev"])
        qo._resolve_runtime_args(args, {"GITHUB_RUN_ID": "55", "GITHUB_RUN_ATTEMPT": "2"})
        self.assertEqual((args.run_id, args.run_attempt), (55, 2))
        self.assertEqual(args.method, "select_next")

    def test_missing_run_identity_is_a_configuration_error(self):
        args = qo.build_parser().parse_args(["select-next", "--target-branch", "dev"])
        with self.assertRaises(qo.ConfigurationError):
            qo._resolve_runtime_args(args, {})

    def test_non_integer_run_id_is_a_configuration_error(self):
        args = qo.build_parser().parse_args(["select-next", "--target-branch", "dev"])
        with self.assertRaises(qo.ConfigurationError):
            qo._resolve_runtime_args(args, {"GITHUB_RUN_ID": "abc"})

    def test_recover_requires_an_actor(self):
        args = qo.build_parser().parse_args(
            [
                "recover",
                "--pr",
                "7",
                "--expected-head-sha",
                SHA_A,
                "--ticket",
                "OPS-1",
                "--reason",
                "reconciled by hand",
            ]
        )
        with self.assertRaises(qo.ConfigurationError):
            qo._resolve_runtime_args(args, {"GITHUB_RUN_ID": "1"})
        qo._resolve_runtime_args(args, {"GITHUB_RUN_ID": "1", "GITHUB_ACTOR": "octocat"})
        self.assertEqual(args.actor, "octocat")

    def test_quality_provenance_is_read_from_the_event_payload(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "event.json")
            with open(path, "w", encoding="utf-8") as handle:
                json.dump({"workflow_run": {"id": 4242, "run_attempt": 3}}, handle)
            self.assertEqual(
                qo._event_quality_provenance({"GITHUB_EVENT_PATH": path}), (4242, 3)
            )

    def test_missing_or_malformed_event_payload_is_tolerated(self):
        self.assertEqual(qo._event_quality_provenance({}), (None, None))
        self.assertEqual(
            qo._event_quality_provenance({"GITHUB_EVENT_PATH": "/nonexistent/event.json"}),
            (None, None),
        )

    def test_every_subcommand_binds_an_orchestrator_method(self):
        commands = {
            "record-validation": [
                "--pr", "7",
                "--target-branch", "dev",
                "--head-sha", SHA_A,
                "--base-sha", SHA_B,
                "--validation-id", JOB_ID,
            ],
            "sync-ready": ["--pr", "7"],
            "select-next": ["--target-branch", "dev"],
            "verify-selected": [
                "--pr", "7",
                "--expected-head-sha", SHA_A,
                "--expected-base-sha", SHA_B,
                "--expected-check-run-id", "300",
                "--phase", "pre-deploy",
            ],
            "defer": ["--pr", "7", "--reason", "x", "--expected-head-sha", SHA_A],
            "recover": [
                "--pr", "7",
                "--expected-head-sha", SHA_A,
                "--ticket", "OPS-1",
                "--reason", "manual",
            ],
        }
        for command, argv in commands.items():
            with self.subTest(command=command):
                args = qo.build_parser().parse_args([command] + argv)
                self.assertTrue(hasattr(qo.QueueOrchestrator, args.method))


class BlockReasonTests(unittest.TestCase):
    def test_hard_and_soft_reasons_do_not_overlap(self):
        self.assertEqual(qo.HARD_BLOCK_REASONS & qo.SOFT_BLOCK_REASONS, frozenset())

    def test_every_block_reason_is_safe_state_text(self):
        for reason in qo.HARD_BLOCK_REASONS | qo.SOFT_BLOCK_REASONS:
            with self.subTest(reason=reason):
                self.assertEqual(qo._safe_text(reason, "blocked_reason"), reason)


class ServerCompletionTests(unittest.TestCase):
    def test_prefers_the_latest_completion_timestamp(self):
        self.assertEqual(
            qo._server_completion(
                {"completed_at": "2026-08-27T10:00:00Z"},
                {"updated_at": "2026-08-27T11:00:00Z"},
            ),
            "2026-08-27T11:00:00Z",
        )

    def test_requires_at_least_one_server_timestamp(self):
        with self.assertRaises(qo.EvidenceError):
            qo._server_completion({}, {})


class ClockTests(unittest.TestCase):
    def test_orchestrator_now_uses_the_injected_clock(self):
        fixed = datetime(2026, 8, 27, 12, 0, 0, tzinfo=timezone.utc)
        orchestrator = qo.QueueOrchestrator(FakeApi(), config(), clock=lambda: fixed)
        self.assertEqual(orchestrator.now(), "2026-08-27T12:00:00Z")

    def test_utc_now_is_a_zulu_timestamp(self):
        now = qo.parse_timestamp(qo.utc_now())
        self.assertLess(abs(now - datetime.now(timezone.utc)), timedelta(minutes=5))


if __name__ == "__main__":
    unittest.main()
