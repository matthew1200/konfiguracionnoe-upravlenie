#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")/.."
./run.sh --vfs data/nested.json --script scripts/startup_full.txt
