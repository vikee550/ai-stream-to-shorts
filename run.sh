
#!/usr/bin/env bash
set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/.venv"
NVIDIA_LIB_DIR="$VENV_DIR/lib/python3.14/site-packages/nvidia"

export LD_LIBRARY_PATH="$NVIDIA_LIB_DIR/cublas/lib:$NVIDIA_LIB_DIR/cudnn/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export PYTHONPATH="$PROJECT_DIR${PYTHONPATH:+:$PYTHONPATH}"

exec "$VENV_DIR/bin/python" "$@"
