#!/usr/bin/env bash
# ==============================================================================
# Repeatable OASE v0.3.0 Tools Environment Bootstrapper (bootstrap-oase-env.sh)
#
# Records and automates all 4 host-compatibility fixes required on modern Linux
# workstations (GCC 14 / Debian testing / Corporate PyPI mirrors / no-root hosts):
#   1. Python 3.11 virtualenv creation via `uv venv --seed --python 3.11` when
#      `python3 -m venv` fails due to missing system `python3-venv` (`ensurepip`).
#   2. Corporate PyPI mirror (Airlock) soaking tolerance when `grpcio-status==1.84.1`
#      is still in upstream quarantine (`>=1.84.0`).
#   3. Offline KaTeX v0.16.21 installation from the official GitHub release tarball
#      when `npm` is not installed on the host.
#   4. Static `fpocket 4.2.2` compilation under GCC 14 (`-Wno-error=incompatible-pointer-types`
#      for `src/fparams.c:296`), followed by `./install.sh --binaries-only` to
#      verify all 7 scientific binaries and stamp `env.sh` + `ENV_VERSION`.
# ==============================================================================
set -euo pipefail

OASE_SOURCE_REPO="${OASE_SOURCE_REPO:-$HOME/dev/github/GoogleCloudPlatform/LifeSciences/applications/open-agentic-science-engine}"
OASE_TOOLS_HOME="${OASE_TOOLS_HOME:-/tmp/scion-volumes/tools}"
OASE_VENV="${OASE_VENV:-$OASE_TOOLS_HOME/.venv}"
OASE_BIN="${OASE_BIN:-$OASE_TOOLS_HOME/bin}"

echo "==> Bootstrapping OASE Tools Home at: $OASE_TOOLS_HOME"
echo "==> Using OASE Source Repo at:        $OASE_SOURCE_REPO"

if [[ ! -d "$OASE_SOURCE_REPO/tools" ]]; then
  echo "[error] OASE source repository not found at $OASE_SOURCE_REPO/tools" >&2
  exit 1
fi

mkdir -p "$OASE_TOOLS_HOME" "$OASE_BIN" "$OASE_TOOLS_HOME/vendor"

# 1. Create Python 3.11 virtualenv (preferring uv venv when ensurepip is absent)
if [[ ! -x "$OASE_VENV/bin/python" ]]; then
  echo "==> Creating Python 3.11 virtual environment at $OASE_VENV..."
  if command -v uv >/dev/null 2>&1; then
    uv venv --seed --python 3.11 "$OASE_VENV"
  else
    python3 -m venv "$OASE_VENV"
  fi
else
  echo "==> Reusing existing virtual environment at $OASE_VENV"
fi

# 2. Install Python dependencies (with corporate PyPI mirror fallback)
if ! "$OASE_VENV/bin/python" -c "import oase, rdkit, Bio, meeko, gemmi" >/dev/null 2>&1; then
  echo "==> Installing OASE core, hypex, and science Python stacks..."
  TMP_REQ_DIR="$(mktemp -d)"
  for req in requirements.txt requirements-hypex.txt requirements-science.txt; do
    sed -E 's/ --hash=sha256:[0-9a-f]+//g; s/\\$//g; s/grpcio-status==1\.84\.1/grpcio-status>=1.84.0/g' \
      "$OASE_SOURCE_REPO/tools/$req" \
      | grep -vE '^\s*--hash=' > "$TMP_REQ_DIR/$req"
  done
  if command -v uv >/dev/null 2>&1; then
    uv pip install --python "$OASE_VENV/bin/python" \
      -r "$TMP_REQ_DIR/requirements.txt" \
      -r "$TMP_REQ_DIR/requirements-hypex.txt" \
      -r "$TMP_REQ_DIR/requirements-science.txt"
    uv pip install --python "$OASE_VENV/bin/python" --no-deps -e "$OASE_SOURCE_REPO/tools"
  else
    "$OASE_VENV/bin/pip" install \
      -r "$TMP_REQ_DIR/requirements.txt" \
      -r "$TMP_REQ_DIR/requirements-hypex.txt" \
      -r "$TMP_REQ_DIR/requirements-science.txt"
    "$OASE_VENV/bin/pip" install --no-deps -e "$OASE_SOURCE_REPO/tools"
  fi
  rm -rf "$TMP_REQ_DIR"
else
  echo "==> Python dependencies already installed in $OASE_VENV"
fi

# 3. Install offline KaTeX v0.16.21 assets (works with or without npm)
KATEX_VERSION="0.16.21"
KATEX_TARBALL_SHA256="c4bbd630fc1aa9bdd9dc1ee0be3bd3ee3ffc6ceab2bf4fc2eeb6bcd4f5f6db6b"
if [[ ! -f "$OASE_TOOLS_HOME/vendor/katex/katex.min.css" ]]; then
  echo "==> Installing offline KaTeX v${KATEX_VERSION} assets..."
  TMP_KATEX="$(mktemp -d)"
  curl -fsSL "https://github.com/KaTeX/KaTeX/releases/download/v${KATEX_VERSION}/katex.tar.gz" \
    -o "$TMP_KATEX/katex.tar.gz"
  echo "${KATEX_TARBALL_SHA256}  $TMP_KATEX/katex.tar.gz" | sha256sum -c -
  tar -xzf "$TMP_KATEX/katex.tar.gz" -C "$TMP_KATEX"
  mkdir -p "$OASE_TOOLS_HOME/vendor/katex/fonts" "$OASE_TOOLS_HOME/npm/node_modules/katex/dist/fonts"
  cp "$TMP_KATEX/katex/katex.min.css" "$OASE_TOOLS_HOME/vendor/katex/katex.min.css"
  cp "$TMP_KATEX/katex/katex.min.js" "$OASE_TOOLS_HOME/vendor/katex/katex.min.js"
  cp "$TMP_KATEX/katex/fonts/"*.woff2 "$OASE_TOOLS_HOME/vendor/katex/fonts/"
  cp -r "$TMP_KATEX/katex/"* "$OASE_TOOLS_HOME/npm/node_modules/katex/dist/"
  printf '{"version": "%s"}\n' "$KATEX_VERSION" > "$OASE_TOOLS_HOME/npm/node_modules/katex/package.json"
  rm -rf "$TMP_KATEX"
else
  echo "==> Offline KaTeX v${KATEX_VERSION} already present"
fi

# 4. Pre-compile static fpocket 4.2.2 with GCC 14 compatibility flag if needed
FPOCKET_VERSION="4.2.2"
FPOCKET_SHA256="6abecb26dd9fb4fb2b2efca1ebdb5dfecceff4cd60ff9b8e11cd381ac33a3d80"
if [[ ! -x "$OASE_BIN/fpocket" ]]; then
  echo "==> Compiling static fpocket ${FPOCKET_VERSION} with GCC 14 pointer-type compatibility..."
  TMP_FP="$(mktemp -d)"
  curl -fsSL "https://github.com/Discngine/fpocket/archive/refs/tags/${FPOCKET_VERSION}.tar.gz" \
    -o "$TMP_FP/fpocket.tar.gz"
  echo "${FPOCKET_SHA256}  $TMP_FP/fpocket.tar.gz" | sha256sum -c -
  tar -xzf "$TMP_FP/fpocket.tar.gz" -C "$TMP_FP"
  make -C "$TMP_FP/fpocket-${FPOCKET_VERSION}" \
    CFLAGS="-W -Wextra -Wwrite-strings -Wstrict-prototypes -Wno-error=incompatible-pointer-types -DM_OS_LINUX -DMNO_MEM_DEBUG -O2 -fstack-protector-strong -D_FORTIFY_SOURCE=2 -std=gnu99 -Iplugins/include -Iplugins/LINUXAMD64/molfile" \
    LFLAGS="-static -lm -Lplugins/LINUXAMD64/molfile" \
    bin/fpocket
  install -m 0755 "$TMP_FP/fpocket-${FPOCKET_VERSION}/bin/fpocket" "$OASE_BIN/fpocket"
  rm -rf "$TMP_FP"
else
  echo "==> Static fpocket binary already installed at $OASE_BIN/fpocket"
fi

# 5. Run official OASE install.sh --binaries-only to install remaining binaries and stamp ENV_VERSION
echo "==> Running OASE install.sh --binaries-only to verify all 7 binaries and stamp env.sh..."
export OASE_TOOLS_HOME OASE_VENV OASE_BIN
cd "$OASE_SOURCE_REPO/tools"
./install.sh --binaries-only

echo "==> Environment bootstrap complete! Source with:"
echo "    source $OASE_TOOLS_HOME/env.sh"
