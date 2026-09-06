#!/bin/bash

set -euo pipefail

if python3 -c "import sys; raise SystemExit(sys.version_info < (3, 8))" >/dev/null 2>&1; then
	python3 source_health.py "$@"
elif python -c "import sys; raise SystemExit(sys.version_info < (3, 8))" >/dev/null 2>&1; then
	python source_health.py "$@"
elif py -3 -c "import sys; raise SystemExit(sys.version_info < (3, 8))" >/dev/null 2>&1; then
	py -3 source_health.py "$@"
else
	echo "Python 3.8 or newer is required to run source_health.py." >&2
	exit 127
fi
