#!/bin/sh
set -eu

# File-backed Compose secrets are mounted read-only with permissive metadata by
# Docker Desktop. asyncpg deliberately rejects such a pgpass file, so copy the
# mounted secret into the service's private tmpfs before starting the process.
if [ "${PGPASSFILE:-}" = "/run/secrets/postgres-pgpass" ]; then
    umask 077
    cp /run/secrets/postgres-pgpass /tmp/postgres-pgpass
    chmod 600 /tmp/postgres-pgpass
    export PGPASSFILE=/tmp/postgres-pgpass
fi

exec "$@"
