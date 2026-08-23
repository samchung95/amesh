from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import yaml

from amesh.operator.model import API_GROUP, API_VERSION, RESOURCE_DESCRIPTORS

ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT / "charts" / "amesh" / "crds" / "platform.amesh.io_resources.yaml"


def _string(*, description: str, maximum: int = 255) -> dict[str, object]:
    return {"type": "string", "description": description, "minLength": 1, "maxLength": maximum}


def _spec(kind: str, namespaced: bool, payload_mode: str) -> dict[str, object]:
    properties: dict[str, object] = {
        "tenant": _string(
            description="AMESH tenant selected from the operator target allowlist.", maximum=128
        ),
        "key": _string(description="AMESH resource key. Defaults to metadata.name.", maximum=1024),
        "deletionPolicy": {
            "type": "string",
            "description": "Delete removes supported remote resources; Retain releases only the finalizer.",
            "enum": ["Retain", "Delete"],
            "default": "Retain",
        },
    }
    required = ["tenant"]
    if namespaced:
        properties["namespace"] = _string(
            description="AMESH namespace, distinct from the Kubernetes namespace.", maximum=255
        )
        if kind != "AmeshNamespace":
            required.append("namespace")
    if payload_mode == "file":
        properties["content"] = {
            "type": "string",
            "description": "UTF-8 file content sent to the AMESH namespace-file API.",
            "maxLength": 2_097_152,
        }
        properties["contentType"] = _string(
            description="Optional media type for file content.", maximum=255
        )
        required.append("content")
    else:
        properties["document"] = {
            "type": "object",
            "description": "Desired AMESH API document. Server-managed fields belong in status, not spec.",
            "x-kubernetes-preserve-unknown-fields": True,
        }
        required.append("document")
    return {
        "type": "object",
        "required": required,
        "properties": properties,
    }


def _status() -> dict[str, object]:
    return {
        "type": "object",
        "properties": {
            "observedGeneration": {"type": "integer", "format": "int64", "minimum": 0},
            "remoteId": {"type": "string"},
            "remoteRevision": {"type": "string"},
            "appliedDigest": {"type": "string", "pattern": "^sha256:[0-9a-f]{64}$"},
            "remoteDigest": {"type": "string", "pattern": "^sha256:[0-9a-f]{64}$"},
            "failureCount": {"type": "integer", "format": "int32", "minimum": 0},
            "retryAfter": {"type": "string", "format": "date-time"},
            "conditions": {
                "type": "array",
                "x-kubernetes-list-type": "map",
                "x-kubernetes-list-map-keys": ["type"],
                "items": {
                    "type": "object",
                    "required": ["type", "status", "reason", "message", "lastTransitionTime"],
                    "properties": {
                        "type": _string(description="Condition type.", maximum=64),
                        "status": {"type": "string", "enum": ["True", "False", "Unknown"]},
                        "reason": _string(
                            description="Stable machine-readable reason.", maximum=128
                        ),
                        "message": {"type": "string", "maxLength": 1_024},
                        "observedGeneration": {"type": "integer", "format": "int64", "minimum": 0},
                        "lastTransitionTime": {"type": "string", "format": "date-time"},
                    },
                },
            },
        },
    }


def _crd(kind: str, plural: str, namespaced: bool, payload_mode: str) -> dict[str, object]:
    singular = plural.removeprefix("amesh")
    return {
        "apiVersion": "apiextensions.k8s.io/v1",
        "kind": "CustomResourceDefinition",
        "metadata": {
            "name": f"{plural}.{API_GROUP}",
            "labels": {"app.kubernetes.io/name": "amesh-operator"},
            "annotations": {"platform.amesh.io/schema-version": API_VERSION},
        },
        "spec": {
            "group": API_GROUP,
            "scope": "Namespaced",
            "names": {
                "kind": kind,
                "listKind": f"{kind}List",
                "plural": plural,
                "singular": singular,
                "categories": ["amesh"],
            },
            "versions": [
                {
                    "name": API_VERSION,
                    "served": True,
                    "storage": True,
                    "subresources": {"status": {}},
                    "additionalPrinterColumns": [
                        {"name": "Tenant", "type": "string", "jsonPath": ".spec.tenant"},
                        {
                            "name": "Ready",
                            "type": "string",
                            "jsonPath": '.status.conditions[?(@.type=="Ready")].status',
                        },
                        {"name": "Age", "type": "date", "jsonPath": ".metadata.creationTimestamp"},
                    ],
                    "schema": {
                        "openAPIV3Schema": {
                            "type": "object",
                            "required": ["spec"],
                            "properties": {
                                "spec": _spec(kind, namespaced, payload_mode),
                                "status": deepcopy(_status()),
                            },
                        }
                    },
                }
            ],
        },
    }


def main() -> None:
    documents = [
        _crd(descriptor.kind, descriptor.plural, descriptor.namespaced, descriptor.payload_mode)
        for descriptor in RESOURCE_DESCRIPTORS
    ]
    DESTINATION.parent.mkdir(parents=True, exist_ok=True)
    rendered = "# Generated by scripts/generate_operator_crds.py; do not edit by hand.\n"
    rendered += yaml.safe_dump_all(documents, sort_keys=False, explicit_start=True)
    DESTINATION.write_text(rendered, encoding="utf-8")
    print(f"Generated {len(documents)} operator CRDs at {DESTINATION.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
