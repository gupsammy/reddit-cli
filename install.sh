#!/usr/bin/env bash
set -euo pipefail

REPO="gupsammy/reddit-cli"
INSTALL_DIR="${HOME}/.local/bin"
BINARY_NAME="reddit-cli"

# ── platform detection ────────────────────────────────────────────────────────

OS="$(uname -s)"
ARCH="$(uname -m)"

case "${OS}" in
  Darwin) PLATFORM="darwin" ;;
  Linux)  PLATFORM="linux"  ;;
  *)
    echo "Error: unsupported operating system '${OS}'." >&2
    echo "reddit-cli binaries are available for macOS (arm64, x86_64) and Linux (x86_64)." >&2
    exit 1
    ;;
esac

case "${ARCH}" in
  arm64)           NORM_ARCH="arm64"  ;;
  x86_64 | amd64) NORM_ARCH="x86_64" ;;
  *)
    echo "Error: unsupported architecture '${ARCH}'." >&2
    echo "reddit-cli binaries are available for arm64 and x86_64." >&2
    exit 1
    ;;
esac

if [[ "${PLATFORM}" == "linux" && "${NORM_ARCH}" == "arm64" ]]; then
  echo "Error: Linux arm64 is not yet supported as a pre-built binary." >&2
  echo "Install via pip instead:" >&2
  echo "  pip install git+https://github.com/${REPO}.git" >&2
  exit 1
fi

ASSET_NAME="${BINARY_NAME}-${PLATFORM}-${NORM_ARCH}"
DOWNLOAD_URL="https://github.com/${REPO}/releases/latest/download/${ASSET_NAME}"

# ── download ──────────────────────────────────────────────────────────────────

echo "Detected: ${PLATFORM}/${NORM_ARCH}"
echo "Downloading ${ASSET_NAME} ..."

mkdir -p "${INSTALL_DIR}"
TMP_FILE="$(mktemp)"
trap 'rm -f "${TMP_FILE}"' EXIT

if command -v curl &>/dev/null; then
  curl -fsSL --progress-bar "${DOWNLOAD_URL}" -o "${TMP_FILE}"
elif command -v wget &>/dev/null; then
  wget -q --show-progress "${DOWNLOAD_URL}" -O "${TMP_FILE}"
else
  echo "Error: neither curl nor wget found. Install either and retry." >&2
  exit 1
fi

chmod +x "${TMP_FILE}"
mv "${TMP_FILE}" "${INSTALL_DIR}/${BINARY_NAME}"

echo ""
echo "Installed: ${INSTALL_DIR}/${BINARY_NAME}"

# ── gatekeeper notice (macOS only) ───────────────────────────────────────────

if [[ "${PLATFORM}" == "darwin" ]]; then
  echo ""
  echo "macOS Gatekeeper notice:"
  echo "  This binary is unsigned. macOS may block it on first run."
  echo "  To allow it, run:"
  echo ""
  echo "    xattr -d com.apple.quarantine ${INSTALL_DIR}/${BINARY_NAME}"
  echo ""
  echo "  Or: System Settings → Privacy & Security → Allow Anyway"
fi

# ── PATH check ────────────────────────────────────────────────────────────────

if [[ ":${PATH}:" != *":${INSTALL_DIR}:"* ]]; then
  echo ""
  echo "Note: ${INSTALL_DIR} is not in your PATH."
  echo "Add it to your shell config:"
  echo ""
  echo "  # zsh (~/.zshrc)"
  echo "  export PATH=\"\${HOME}/.local/bin:\${PATH}\""
  echo ""
  echo "  # bash (~/.bashrc or ~/.bash_profile)"
  echo "  export PATH=\"\${HOME}/.local/bin:\${PATH}\""
  echo ""
  echo "Then reload: source ~/.zshrc  (or open a new terminal)"
fi

echo ""
echo "Run 'reddit-cli auth' to verify your Reddit credentials."
