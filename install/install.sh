#!/usr/bin/env bash
# =============================================================================
#  MinecraftDockerCLI - Ubuntu Server Installer
# =============================================================================
#  Installs Python 3.13, Docker Engine, and MinecraftDockerCLI system-wide
#  on Ubuntu-based distributions (Debian, Pop!_OS, Linux Mint, etc.).
#
#  Usage:
#    chmod +x install.sh && sudo ./install.sh
# =============================================================================

set -euo pipefail

# -------------------------------------------
# Color helpers
# -------------------------------------------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info()  { echo -e "${CYAN}[INFO]${NC}  $*"; }
log_ok()    { echo -e "${GREEN}[OK]${NC}    $*"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*"; }

# -------------------------------------------
# Root check
# -------------------------------------------
if [[ $EUID -ne 0 ]]; then
    log_error "This script must be run as root (use sudo)."
    exit 1
fi

# -------------------------------------------
# OS / Arch detection
# -------------------------------------------
OS=""
ARCH="$(uname -m)"
if [[ -f /etc/os-release ]]; then
    . /etc/os-release
    OS="$ID"
    VERSION_ID="${VERSION_ID:-}"
fi

if [[ "$OS" != "ubuntu" && "$OS" != "debian" && "$OS" != "pop" && "$OS" != "linuxmint" && "$OS" != "elementary" ]]; then
    log_warn "This script is designed for Ubuntu-based distributions."
    log_warn "Detected OS: ${OS:-unknown}. Proceeding anyway..."
fi

log_info "Detected OS: ${ID:-unknown} ${VERSION_ID}"
log_info "Architecture: ${ARCH}"

# -------------------------------------------
# Step 1: System package update
# -------------------------------------------
log_info "Updating package lists..."
apt-get update -qq || log_warn "apt update had non-zero exit, continuing..."

# -------------------------------------------
# Step 2: Install Python 3.13 + pip
# -------------------------------------------
PYTHON_BIN=""
PYTHON_VERSION_REQUIRED="3.13"

if command -v python3.13 &>/dev/null; then
    PYTHON_BIN="python3.13"
    log_ok "Python 3.13 already installed at $(command -v python3.13)."
else
    log_info "Installing Python ${PYTHON_VERSION_REQUIRED}..."

    if [[ "$OS" == "ubuntu" ]]; then
        apt-get install -y -qq software-properties-common
        add-apt-repository -y ppa:deadsnakes/ppa
        apt-get update -qq
    fi

    apt-get install -y -qq \
        "python${PYTHON_VERSION_REQUIRED}" \
        "python${PYTHON_VERSION_REQUIRED}-dev" \
        python3-pip

    PYTHON_BIN="python${PYTHON_VERSION_REQUIRED}"

    if ! command -v "$PYTHON_BIN" &>/dev/null; then
        log_error "Python ${PYTHON_VERSION_REQUIRED} installation failed."
        exit 1
    fi
    log_ok "Python ${PYTHON_VERSION_REQUIRED} installed: $(command -v $PYTHON_BIN)"
fi

# Upgrade pip system-wide
log_info "Upgrading pip..."
"$PYTHON_BIN" -m pip install --upgrade pip -qq

# -------------------------------------------
# Step 3: Install Docker Engine + Docker Compose
# -------------------------------------------
if command -v docker &>/dev/null; then
    log_ok "Docker already installed: $(docker --version)"
else
    log_info "Installing Docker Engine..."

    apt-get remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true

    apt-get install -y -qq \
        ca-certificates \
        curl \
        gnupg \
        lsb-release

    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/${OS}/gpg \
        -o /etc/apt/keyrings/docker.asc
    chmod a+r /etc/apt/keyrings/docker.asc

    if [[ -n "$VERSION_ID" ]]; then
        echo \
            "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] \
            https://download.docker.com/linux/${OS} \
            ${VERSION_ID_CODENAME:-$(lsb_release -cs)} stable" \
            | tee /etc/apt/sources.list.d/docker.list > /dev/null
    else
        echo \
            "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] \
            https://download.docker.com/linux/${OS} \
            $(lsb_release -cs) stable" \
            | tee /etc/apt/sources.list.d/docker.list > /dev/null
    fi

    apt-get update -qq

    apt-get install -y -qq \
        docker-ce \
        docker-ce-cli \
        containerd.io \
        docker-buildx-plugin \
        docker-compose-plugin

    log_ok "Docker installed: $(docker --version)"
    log_ok "Docker Compose installed: $(docker compose version)"
fi

if ! systemctl is-active --quiet docker; then
    log_info "Starting Docker service..."
    systemctl enable --now docker
fi
log_ok "Docker service is running."

# -------------------------------------------
# Step 4: Install MinecraftDockerCLI system-wide
# -------------------------------------------
log_info "Installing MinecraftDockerCLI from PyPI..."

"$PYTHON_BIN" -m pip install MinecraftDockerCLI

# -------------------------------------------
# Step 5: Verify installation
# -------------------------------------------
log_info "Verifying installation..."
if command -v MinecraftDockerCLI &>/dev/null; then
    INSTALLED_VERSION=$(MinecraftDockerCLI --version 2>/dev/null || true)
    log_ok "MinecraftDockerCLI ${INSTALLED_VERSION:-} is ready to use."
else
    log_warn "MinecraftDockerCLI command not found in PATH after install."
    log_warn "Try re-logging in or running: hash -r"
fi

# -------------------------------------------
# Post-install message
# -------------------------------------------
echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  MinecraftDockerCLI Installation Complete${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo -e "  Run the CLI:  ${CYAN}MinecraftDockerCLI --help${NC}"
echo ""
echo -e "  ${YELLOW}NOTE:${NC} Make sure your user is in the 'docker' group to run"
echo "  Docker commands without sudo:"
echo -e "    ${CYAN}sudo usermod -aG docker \$USER${NC}"
echo "  Then log out and back in (or restart your session)."
echo ""
echo -e "  To update in the future:"
echo -e "    ${CYAN}sudo pip install --upgrade MinecraftDockerCLI${NC}"
echo ""
