from __future__ import annotations

import pytest

from amesh.domain import (
    BlueprintCatalogSource,
    BlueprintInstantiationRequest,
    get_blueprint,
    instantiate_blueprint,
    list_blueprints,
)
from amesh.dsl import validate_flow_document


def test_catalog_exposes_versioned_searchable_sources_with_provenance() -> None:
    blueprints = list_blueprints()

    assert {item.source for item in blueprints} == set(BlueprintCatalogSource)
    assert all(item.version == "1.0.0" for item in blueprints)
    assert all(item.documentation and item.license for item in blueprints)
    assert all(item.provenance.digest.startswith("sha256:") for item in blueprints)
    assert [item.blueprint_id for item in list_blueprints(query="foreach")] == [
        "community-batch"
    ]
    assert all(
        item.source is BlueprintCatalogSource.ORGANIZATION
        for item in list_blueprints(source=BlueprintCatalogSource.ORGANIZATION)
    )


@pytest.mark.parametrize("blueprint_id", ["hello-world", "organization-readiness", "community-batch"])
def test_each_blueprint_instantiates_as_a_valid_unsaved_flow(blueprint_id: str) -> None:
    blueprint = get_blueprint(blueprint_id, "1.0.0")
    document = instantiate_blueprint(
        blueprint,
        BlueprintInstantiationRequest(
            parameters={"namespace": "tests.blueprints", "flow_id": f"draft_{blueprint_id}"}
        ),
    )

    assert document["namespace"] == "tests.blueprints"
    assert document["id"] == f"draft_{blueprint_id}"
    assert validate_flow_document(document).valid is True


def test_instantiation_rejects_undeclared_parameters() -> None:
    with pytest.raises(ValueError, match="unknown blueprint parameters"):
        instantiate_blueprint(
            get_blueprint("hello-world", "1.0.0"),
            BlueprintInstantiationRequest(parameters={"unexpected": "value"}),
        )
