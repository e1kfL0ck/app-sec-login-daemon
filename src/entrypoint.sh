#!/bin/sh
set -e

# If INIT_DB is set to a truthy value, run the initialization script.
if [ -n "$INIT_DB" ]; then
  case "$INIT_DB" in
    1|true|True|TRUE|yes|Yes)
      echo "INIT_DB is enabled — initializing database..."
      python3 /workspace/init_db.py
      ;;
    *)
      echo "INIT_DB not enabled (value='$INIT_DB'), skipping DB init."
      ;;
  esac
fi

# If CLEAR_UPLOADS is set to a truthy value, clear the data directory.
if [ -n "$CLEAR_UPLOADS" ]; then
  case "$CLEAR_UPLOADS" in
    1|true|True|TRUE|yes|Yes)
      echo "CLEAR_UPLOADS is enabled — clearing data directory..."
      rm -rf /data/uploads/*
      ;;
    *)
      echo "CLEAR_UPLOADS not enabled (value='$CLEAR_UPLOADS'), skipping data clear."
      ;;
  esac
fi

# Exec the container CMD (e.g. uvicorn)
exec "$@"
