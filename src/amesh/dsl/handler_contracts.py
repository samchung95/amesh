"""Handler-side authority for built-in task configuration contracts."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from typing import Any

from .descriptors import HandlerConfigurationContract

_BUILTIN_HANDLER_CONTRACTS: dict[str, HandlerConfigurationContract] = {}
_MODEL_HANDLER_CONTRACTS: dict[str, HandlerConfigurationContract] | None = None

# Runtime-owned identities for non-model built-in handler contracts.  Keeping this
# authority independent from the DSL specification means a changed catalog schema
# cannot silently redefine what a handler accepts during first registration.
_NON_MODEL_HANDLER_SCHEMA_DIGESTS = {
    "agent.handoff": "4907096ca74f60c37b41a6518bcf78cc933e4f951939e55ef8e23787274fafe2",
    "agent.mcp": "59b42f7b60ad5f21d21d5eeadc8f26ba0e308ddf82df80b070fb1505cc5e9f70",
    "agent.mesh": "dd11ec8f5d9ec4f24080a269fd5e6a71c33dc126ff2cd168bc4c67544e8c4e01",
    "agent.route": "3bc9f4ecd3491d32db05d988306b69fa285afb101adff60e7e2d3c6775fdc03e",
    "agent.session": "e037e4772f5eb57560ed82a12e73af6af409797446eddb331b964a7509159a8b",
    "core.approval": "6e161856602bc16020a1ed6a2391da31e7c693d25c7a3b8bd23d0e9b14ef949e",
    "core.assert": "7613739a095091dfbfdda1ed7f14aad4baeca27d0d77a7904a39cf0959ecff44",
    "core.dag": "bb7119af922cb289558c036e69c26eeb5082caf0b923a5b1c2ebe94c7f7c38ef",
    "core.data.csv": "b19bfc9d6743090ff08ff43943889cfa1ae0adc5d1126f1afde44ec489cdc27a",
    "core.data.json": "b19bfc9d6743090ff08ff43943889cfa1ae0adc5d1126f1afde44ec489cdc27a",
    "core.data.text": "9af0a317025fc2a648f8971598a883a7ede6658026b973f24254bd4fad43f5c7",
    "core.data.xml": "b19bfc9d6743090ff08ff43943889cfa1ae0adc5d1126f1afde44ec489cdc27a",
    "core.data.yaml": "b19bfc9d6743090ff08ff43943889cfa1ae0adc5d1126f1afde44ec489cdc27a",
    "core.debug": "b67565aca0de0a4b9d516e4d2c11cae020a7400e04f11136ea51032a4efafa1c",
    "core.document.extract": "10b7644d5182c3f0737bd64518fb769d89a11fed5d1dfce11451696cd608f8cf",
    "core.download": "ac0e37b16b7bca1ba2d9ad4f80d38cf16a6a20ce4c11a39ce43041f734718246",
    "core.fail": "fd3be9c24a13e2b295bb676e4faa304674c3921692879a7b3db76c9a56da3b15",
    "core.files.checksum": "1c034c8a4c0f02d4241fb937e98dc005001f0b21359fd4d6c49289deeec251b2",
    "core.files.compress": "ee53c517c39730aef207936c5aba2bf61bad6044451cbbab95fd8f1a93f05755",
    "core.files.copy": "d97723864e2f7d0f0149a6cb34dca64b8cc8c9d6420d02dd9843b6dcd6d830f9",
    "core.files.delete": "496d6821af41b6feab63564b5aa0bb592a2dfccbdb099fe539cf68957386f791",
    "core.files.extract": "bfbdd75d716d65cd19000663dc630a59546e641b6ca79e0a4a234739f4c3b3d6",
    "core.files.move": "d97723864e2f7d0f0149a6cb34dca64b8cc8c9d6420d02dd9843b6dcd6d830f9",
    "core.foreach": "1df4801c210f72ccf27e6985170ac56ad8017a1a22cebfa8ef1882533b5f4f64",
    "core.http": "68dde4fe085d88dca6f8e90b79f0ab35667bd6bcfa0898821625df249ea66ea7",
    "core.if": "bb7119af922cb289558c036e69c26eeb5082caf0b923a5b1c2ebe94c7f7c38ef",
    "core.log": "9c96a416b5c7d4d7a8c013336ca1e69ebb0e3cd8da918814fef815ec62e56c63",
    "core.notify.email": "1645319471aae813526e31056b2ba1c3a17ff1d94a1d4a0610dfe900d557c3cc",
    "core.notify.webhook": "68dde4fe085d88dca6f8e90b79f0ab35667bd6bcfa0898821625df249ea66ea7",
    "core.parallel": "bb7119af922cb289558c036e69c26eeb5082caf0b923a5b1c2ebe94c7f7c38ef",
    "core.return": "ed7109630ae74da569e2284edfe7b077e81f808189ff1104bc10148c45e89126",
    "core.sequential": "bb7119af922cb289558c036e69c26eeb5082caf0b923a5b1c2ebe94c7f7c38ef",
    "core.shell": "198454e4dc2a8bd395906ef16ae63b432c1aac5dc133f1728a83b36a36d89d62",
    "core.sleep": "36ba256d77549f91ecf1044f9a7df30651508adb282097bd58b52730754da3d3",
    "core.subflow": "b86ee11c5ea5604f3d0e9aa6aece524001e3d45ae0ccd43639cd73b2e44aa29e",
    "core.switch": "40598295c512a27f1472059666315144798fd7feae368ce73a7ce3b47b5fb04b",
    "core.until": "dfda5bb3b572dd46787b2e79bd2fe59218c823e4a8a12783736da8b9e11afb91",
    "core.while": "dfda5bb3b572dd46787b2e79bd2fe59218c823e4a8a12783736da8b9e11afb91",
    "core.workingDirectory": "66d621acd8a15950ef505097c0af1f6a65762bd853ef9d34b75acf9ef753bb97",
    "script.java": "dbd89c5bd716223b0b8c16a5db20ca271e3daf9b274f59fc38d7222f1034d269",
    "script.node": "dbd89c5bd716223b0b8c16a5db20ca271e3daf9b274f59fc38d7222f1034d269",
    "script.powershell": "dbd89c5bd716223b0b8c16a5db20ca271e3daf9b274f59fc38d7222f1034d269",
    "script.python": "dbd89c5bd716223b0b8c16a5db20ca271e3daf9b274f59fc38d7222f1034d269",
    "script.r": "dbd89c5bd716223b0b8c16a5db20ca271e3daf9b274f59fc38d7222f1034d269",
    "script.shell": "dbd89c5bd716223b0b8c16a5db20ca271e3daf9b274f59fc38d7222f1034d269",
}


def bind_builtin_handler_contract(
    task_type: str,
    declared_schema: Mapping[str, Any],
) -> HandlerConfigurationContract:
    """Bind one built-in kind to its runtime contract and return a separate snapshot."""

    model_contracts = _model_handler_contracts()
    contract = _BUILTIN_HANDLER_CONTRACTS.get(task_type)
    model_contract = model_contracts.get(task_type)
    if model_contract is None:
        expected_digest = _NON_MODEL_HANDLER_SCHEMA_DIGESTS.get(task_type)
        if expected_digest is None:
            raise LookupError(f"no runtime configuration contract exists for {task_type!r}")
        actual_digest = _schema_digest(declared_schema)
        if actual_digest != expected_digest:
            raise ValueError(
                "task specification schema drifted from handler contract: "
                f"{task_type} (expected {expected_digest}, got {actual_digest})"
            )
    if contract is None:
        contract = model_contract or HandlerConfigurationContract(declared_schema)
        _BUILTIN_HANDLER_CONTRACTS[task_type] = contract.snapshot()
    return builtin_handler_contract(task_type).snapshot()


def builtin_handler_contract(task_type: str) -> HandlerConfigurationContract:
    try:
        return _BUILTIN_HANDLER_CONTRACTS[task_type]
    except KeyError as exc:
        raise LookupError(f"no built-in handler contract is bound for {task_type!r}") from exc


def _model_handler_contracts() -> dict[str, HandlerConfigurationContract]:
    global _MODEL_HANDLER_CONTRACTS

    if _MODEL_HANDLER_CONTRACTS is not None:
        return _MODEL_HANDLER_CONTRACTS
    from amesh.tasks.llm import model_handler_configuration_contracts

    _MODEL_HANDLER_CONTRACTS = model_handler_configuration_contracts()
    return _MODEL_HANDLER_CONTRACTS


def _schema_digest(schema: Mapping[str, Any]) -> str:
    encoded = json.dumps(
        schema,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


__all__ = ["bind_builtin_handler_contract", "builtin_handler_contract"]
