"""Reusable application-composition primitives.

The entry points remain responsible for selecting their concrete repositories and
runtime services.  This package owns only the small, shared wiring seams that are
safe to exercise with test doubles.
"""

from .authentication import AuthenticationSettings, build_authentication_service
from .execution_launch import (
    ExecutionDriver,
    ExecutionLaunchConflict,
    ExecutionLaunchRepository,
    ExecutionLaunchResult,
    ExecutionLaunchService,
)
from .executor import LAUNCH_RECOVER_RUNNING_TYPES, RECOVER_RUNNING_TYPES, build_executor_factory
from .handlers import (
    HandlerComposition,
    HandlerFactories,
    HandlerFactoryBundle,
    RuntimeCompositionError,
    build_handler_registry,
)
from .http_policy import HttpPolicySettings, build_http_task_policy
from .runners import (
    RunnerBundle,
    RunnerFactories,
    RunnerSelection,
    build_runner_bundle,
    select_runner_ids,
)
from .runtime import ExecutionRuntime, ExecutionRuntimeSettings, build_execution_runtime

__all__ = [
    "LAUNCH_RECOVER_RUNNING_TYPES",
    "RECOVER_RUNNING_TYPES",
    "AuthenticationSettings",
    "ExecutionDriver",
    "ExecutionLaunchConflict",
    "ExecutionLaunchRepository",
    "ExecutionLaunchResult",
    "ExecutionLaunchService",
    "ExecutionRuntime",
    "ExecutionRuntimeSettings",
    "HandlerComposition",
    "HandlerFactories",
    "HandlerFactoryBundle",
    "HttpPolicySettings",
    "RunnerBundle",
    "RunnerFactories",
    "RunnerSelection",
    "RuntimeCompositionError",
    "build_authentication_service",
    "build_execution_runtime",
    "build_executor_factory",
    "build_handler_registry",
    "build_http_task_policy",
    "build_runner_bundle",
    "select_runner_ids",
]
