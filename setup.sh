#!/usr/bin/env bash
set -e

VENV_DIR="Launchpad95_typed/.venv"
PYTHON="${PYTHON:-python3}"

if ! command -v "$PYTHON" >/dev/null 2>&1; then
	echo "Error: $PYTHON not found. Set PYTHON to a valid interpreter." >&2
	exit 1
fi

if [ ! -d "$VENV_DIR" ]; then
	echo "Creating virtual environment in $VENV_DIR..."
	"$PYTHON" -m venv "$VENV_DIR"
fi

echo "Upgrading pip..."
"$VENV_DIR/bin/pip" install --upgrade pip

echo "Installing test dependencies..."
"$VENV_DIR/bin/pip" install pytest future

echo "Setup complete."
echo "Run tests with: $VENV_DIR/bin/python -m pytest Launchpad95_typed/tests/ -q"
