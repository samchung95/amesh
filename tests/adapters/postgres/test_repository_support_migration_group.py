from __future__ import annotations

from inspect import Parameter, signature

import pytest

from amesh.adapters.postgres.agent_memory import PostgresAgentMemoryRepository
from amesh.adapters.postgres.agent_primitives import PostgresAgentPrimitiveRepository
from amesh.adapters.postgres.agent_resources import PostgresAgentResourceRepository
from amesh.adapters.postgres.authentication_repository import PostgresAuthenticationRepository
from amesh.adapters.postgres.authorization_repository import PostgresAuthorizationRepository
from amesh.adapters.postgres.credential_repository import PostgresCredentialRepository
from amesh.adapters.postgres.federation_repository import PostgresFederationRepository
from amesh.adapters.postgres.repository_support import PostgresRepositoryBase


@pytest.mark.parametrize(
    ("repository_type", "parameter_names"),
    (
        (PostgresAgentMemoryRepository, ("self", "engine")),
        (PostgresAgentPrimitiveRepository, ("self", "engine")),
        (PostgresAgentResourceRepository, ("self", "engine")),
        (PostgresAuthenticationRepository, ("self", "engine")),
        (PostgresAuthorizationRepository, ("self", "engine")),
        (PostgresCredentialRepository, ("self", "engine")),
        (PostgresFederationRepository, ("self", "engine", "token_pepper")),
    ),
)
def test_migrated_repositories_inherit_support_without_constructor_drift(
    repository_type: type[PostgresRepositoryBase],
    parameter_names: tuple[str, ...],
) -> None:
    parameters = signature(repository_type.__init__).parameters

    assert issubclass(repository_type, PostgresRepositoryBase)
    assert tuple(parameters) == parameter_names
    assert parameters["engine"].kind is Parameter.POSITIONAL_OR_KEYWORD
    if "token_pepper" in parameters:
        assert parameters["token_pepper"].kind is Parameter.KEYWORD_ONLY
