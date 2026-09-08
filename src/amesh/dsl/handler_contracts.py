"""Bind task specifications to runtime-owned configuration models."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from pydantic import TypeAdapter

from .descriptors import HandlerConfigurationContract

_BUILTIN_HANDLER_CONTRACTS: dict[str, HandlerConfigurationContract] = {}
_MODEL_HANDLER_CONTRACTS: dict[str, HandlerConfigurationContract] | None = None


def bind_builtin_handler_contract(
    task_type: str,
    declared_schema: Mapping[str, Any] | None = None,
) -> HandlerConfigurationContract:
    """Handlers derive schemas from their models; executor-owned kinds supply schemas."""
    model_contract = _model_handler_contracts().get(task_type)
    if model_contract is not None:
        if (
            declared_schema is not None
            and dict(declared_schema) != model_contract.model_json_schema()
        ):
            raise ValueError(
                f"task specification schema drifted from handler contract: {task_type}"
            )
        contract = model_contract
    elif declared_schema is not None:
        existing = _BUILTIN_HANDLER_CONTRACTS.get(task_type)
        if existing is not None and existing.model_json_schema() != dict(declared_schema):
            raise ValueError(
                f"task specification schema drifted from handler contract: {task_type}"
            )
        contract = HandlerConfigurationContract(declared_schema)
    else:
        raise LookupError(f"no runtime configuration model exists for {task_type!r}")
    _BUILTIN_HANDLER_CONTRACTS[task_type] = contract.snapshot()
    return contract.snapshot()


def builtin_handler_contract(task_type: str) -> HandlerConfigurationContract:
    try:
        return _BUILTIN_HANDLER_CONTRACTS[task_type]
    except KeyError as exc:
        raise LookupError(f"no built-in handler contract is bound for {task_type!r}") from exc


def _model_handler_contracts() -> dict[str, HandlerConfigurationContract]:
    global _MODEL_HANDLER_CONTRACTS
    if _MODEL_HANDLER_CONTRACTS is not None:
        return _MODEL_HANDLER_CONTRACTS
    from amesh.tasks.configuration import handler_configuration_models
    from amesh.tasks.llm import model_handler_configuration_contracts

    contracts = model_handler_configuration_contracts()
    for task_type, configuration_model in handler_configuration_models().items():
        adapter: TypeAdapter[Any] = TypeAdapter(configuration_model)

        def validate(
            configuration: Mapping[str, Any], *, active_adapter: TypeAdapter[Any] = adapter
        ) -> None:
            active_adapter.validate_python(dict(configuration), by_alias=True, by_name=False)

        schema = adapter.json_schema(by_alias=True)
        schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
        contracts[task_type] = HandlerConfigurationContract(schema, validate)
    _MODEL_HANDLER_CONTRACTS = contracts
    return contracts


__all__ = ["bind_builtin_handler_contract", "builtin_handler_contract"]
