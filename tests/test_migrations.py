from __future__ import annotations

from amesh.migrations import migration_body


def test_migration_body_removes_outer_transaction() -> None:
    assert migration_body("BEGIN;\nSELECT 1;\nCOMMIT;\n") == "SELECT 1;"
