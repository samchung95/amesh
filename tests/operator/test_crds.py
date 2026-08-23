from __future__ import annotations

from pathlib import Path

import yaml

from amesh.operator.model import API_GROUP, API_VERSION, RESOURCE_DESCRIPTORS

ROOT = Path(__file__).resolve().parents[2]
CRDS = ROOT / "charts" / "amesh" / "crds" / "platform.amesh.io_resources.yaml"


def test_crds_cover_every_operator_descriptor_with_status_subresource() -> None:
    documents = tuple(yaml.safe_load_all(CRDS.read_text(encoding="utf-8")))
    assert len(documents) == len(RESOURCE_DESCRIPTORS) == 9
    by_kind = {document["spec"]["names"]["kind"]: document for document in documents}
    assert set(by_kind) == {descriptor.kind for descriptor in RESOURCE_DESCRIPTORS}
    for descriptor in RESOURCE_DESCRIPTORS:
        document = by_kind[descriptor.kind]
        assert document["metadata"]["name"] == f"{descriptor.plural}.{API_GROUP}"
        version = document["spec"]["versions"][0]
        assert version["name"] == API_VERSION
        assert version["served"] is True
        assert version["storage"] is True
        assert version["subresources"] == {"status": {}}
        status = version["schema"]["openAPIV3Schema"]["properties"]["status"]
        assert "observedGeneration" in status["properties"]
        assert "conditions" in status["properties"]


def test_crds_keep_file_content_typed_and_server_credentials_out_of_schema() -> None:
    documents = tuple(yaml.safe_load_all(CRDS.read_text(encoding="utf-8")))
    rendered = CRDS.read_text(encoding="utf-8")
    file_crd = next(item for item in documents if item["spec"]["names"]["kind"] == "AmeshFile")
    properties = file_crd["spec"]["versions"][0]["schema"]["openAPIV3Schema"]["properties"]["spec"][
        "properties"
    ]
    assert properties["content"]["type"] == "string"
    assert "credential" not in rendered.casefold()
    assert "execution" not in {item["spec"]["names"]["singular"] for item in documents}
