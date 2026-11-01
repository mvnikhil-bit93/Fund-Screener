"""Migration entry points require an explicit target, never ambient defaults."""

import psycopg
import pytest

from ledger.db.migrate import bootstrap_roles, downgrade, revision, upgrade

pytestmark = pytest.mark.integration


@pytest.mark.parametrize("operation", [bootstrap_roles, upgrade, downgrade, revision])
def test_missing_database_is_rejected_before_any_connection(monkeypatch, operation):
    def unexpected_connection(*args, **kwargs):
        pytest.fail("A missing explicit database must be rejected before opening a connection.")

    monkeypatch.setattr(psycopg, "connect", unexpected_connection)
    with pytest.raises(ValueError, match="explicit"):
        operation("host=127.0.0.1 user=postgres")
