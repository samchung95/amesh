from pathlib import Path

from amesh.dsl import validate_flow_document
from amesh.kestra_compatibility import MappingDisposition, import_kestra_flow

FIXTURE = Path(__file__).parents[2] / "conformance" / "kestra" / "1.3.30" / "kestra-core-flow.yaml"


def test_core_flow_import_is_source_preserving_and_loss_explicit() -> None:
    source = FIXTURE.read_text(encoding="utf-8")

    result = import_kestra_flow(source)

    assert result.valid is True
    assert result.blockers == ()
    assert result.release_claim_allowed is False
    assert "# Kestra 1.3.30 source comment" in result.round_trip_document
    assert result.round_trip_document.index("description:") < result.round_trip_document.index(
        "labels:"
    )
    assert result.candidate_document["concurrency"] == [
        {
            "id": "kestra-flow-concurrency",
            "scope": "FLOW",
            "limit": 2,
            "behavior": "QUEUE",
            "leaseSeconds": 3600,
        }
    ]
    assert result.candidate_document["tasks"][0]["type"] == "core.log"
    assert result.candidate_document["tasks"][0]["message"] == "hello {{ flow.id }}"
    assert result.candidate_document["tasks"][0]["retry"] == {
        "maxAttempts": 3,
        "delaySeconds": 1.0,
        "backoffMultiplier": 2.0,
        "maxIntervalSeconds": 8.0,
        "jitterRatio": 0,
        "conditionErrorPolicy": "FAIL",
    }
    assert validate_flow_document(result.candidate_document).valid is True

    mappings = {item.path: item for item in result.mappings}
    assert mappings["/tasks/0/type"].disposition is MappingDisposition.COMPATIBILITY_ADAPTED
    assert mappings["/triggers/0/cron"].disposition is MappingDisposition.EXACT
    assert mappings["/concurrency"].disposition is MappingDisposition.COMPATIBILITY_ADAPTED
    assert all(patch.source_range is not None for patch in result.patches)
    adapted_paths = {
        item.path
        for item in result.mappings
        if item.disposition is MappingDisposition.COMPATIBILITY_ADAPTED
    }
    assert adapted_paths == {patch.path for patch in result.patches}


def test_unknown_plugin_and_property_block_the_document_without_silent_loss() -> None:
    result = import_kestra_flow(
        """id: blocked
namespace: compatibility
unmapped: true
tasks:
  - id: custom
    type: io.example.plugin.Custom
    payload: keep-me
"""
    )

    assert result.valid is False
    blocker_paths = {item.path for item in result.blockers}
    assert {"/unmapped", "/tasks/0/type", "/tasks/0/payload"} <= blocker_paths
    assert result.candidate_document["tasks"][0]["payload"] == "keep-me"
    assert all(item.source_range is not None for item in result.blockers)
