#!/bin/sh
set -e

# --- 1. Database & Uploads Initialization ---
if [ -n "$INIT_DATA" ]; then
  case "$INIT_DATA" in
    1|true|True|TRUE|yes|Yes)
      echo "INIT_DATA is enabled — clearing uploads and initializing database..."
      # Clear existing uploads
      rm -rf /data/uploads/*
      # Run the DB init script
      python3 /workspace/init_db.py
      ;;
    *)
      echo "INIT_DATA not enabled (value='$INIT_DATA'), skipping DB init."
      ;;
  esac
fi

# --- 2. Debug Image Seeding ---
if [ -n "$DEBUG" ]; then
  case "$DEBUG" in
    1|true|True|TRUE|yes|Yes)
      echo "DEBUG mode is enabled — seeding data repository with initial images."
      mkdir -p /data/uploads/
      # Using -n (no-clobber) or ensuring it runs after INIT_DATA clears the folder
      cp -r /data/example/uploads/3 /data/uploads/
      ;;
    *)
      ;;
  esac
fi

# Exec the container CMD (e.g. uvicorn)
exec "$@"