#!/bin/bash
# Wrapper script to run k9s from the project directory

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/k9s" "$@"
