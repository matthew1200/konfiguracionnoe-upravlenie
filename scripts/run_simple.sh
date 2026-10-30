#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")/.."
./run.sh --vfs data/simple.json --script scripts/stage3.txt
