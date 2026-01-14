#!/bin/sh
set -e

# If INIT_DATA is set to a truthy value, run the initialization script.
if [ -n "$INIT_DATA" ]; then
  case "$INIT_DATA" in
    1|true|True|TRUE|yes|Yes)
      echo "INIT_DATA is enabled — initializing database & clearing uploads..."
      python3 /workspace/init_db.py
      rm -rf /data/uploads/*
      ;;
    *)
      echo "INIT_DATA not enabled (value='$INIT_DATA'), skipping DB init & uploads clearing."
      ;;
  esac
fi

# Exec the container CMD (e.g. uvicorn)
exec "$@"
