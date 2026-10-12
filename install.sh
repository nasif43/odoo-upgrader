#!/usr/bin/env bash
# ==============================================================================
# Odoo Upgrader - Portable Setup & Agent Skills Installer
# ==============================================================================
# Sets up the Python CLI tool and installs agent skills for:
# - Google Antigravity / Gemini CLI
# - Anthropic Claude Code
# - Cursor IDE
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_SRC="$SCRIPT_DIR/skills"
AGENTS_SKILLS_DIR="$HOME/.agents/skills"
GEMINI_SKILLS_DIR="$HOME/.gemini/antigravity-cli/skills"

echo "=================================================================="
echo "          🚀 Installing Odoo Upgrader & Agent Skills              "
echo "=================================================================="

# 1. Install Python Package
echo ""
if [ -n "$VIRTUAL_ENV" ]; then
    pip install -e "$SCRIPT_DIR"
elif pip install -e "$SCRIPT_DIR" --user --break-system-packages &> /dev/null; then
    echo "  Installed in user environment."
else
    echo "  Creating dedicated virtual environment in $SCRIPT_DIR/.venv..."
    python3 -m venv "$SCRIPT_DIR/.venv"
    "$SCRIPT_DIR/.venv/bin/pip" install -e "$SCRIPT_DIR"
    mkdir -p "$HOME/.local/bin"
    ln -sf "$SCRIPT_DIR/.venv/bin/odoo-upgrader" "$HOME/.local/bin/odoo-upgrader"
    ln -sf "$SCRIPT_DIR/.venv/bin/upgrade-odoo" "$HOME/.local/bin/upgrade-odoo"
    echo "  Symlinked executables to $HOME/.local/bin/"
fi

# 2. Install Skills to ~/.agents/skills (Claude Code, Antigravity, Gemini)
echo ""
echo "[2/3] Installing Agent Skills to $AGENTS_SKILLS_DIR..."
mkdir -p "$AGENTS_SKILLS_DIR"

for skill in "$SKILLS_SRC"/*; do
    if [ -d "$skill" ]; then
        skill_name="$(basename "$skill")"
        rm -rf "$AGENTS_SKILLS_DIR/$skill_name"
        cp -r "$skill" "$AGENTS_SKILLS_DIR/$skill_name"
        echo "  -> Installed skill: /$skill_name"
    fi
done

# Copy strategy doc if present
if [ -f "$SKILLS_SRC/odoo_strategy.md" ]; then
    cp "$SKILLS_SRC/odoo_strategy.md" "$AGENTS_SKILLS_DIR/"
fi

# 3. Optional: Install to Gemini directory if present
if [ -d "$HOME/.gemini" ]; then
    mkdir -p "$GEMINI_SKILLS_DIR" 2>/dev/null || true
    for skill in "$SKILLS_SRC"/*; do
        if [ -d "$skill" ] && [ -d "$GEMINI_SKILLS_DIR" ]; then
            skill_name="$(basename "$skill")"
            rm -rf "$GEMINI_SKILLS_DIR/$skill_name"
            cp -r "$skill" "$GEMINI_SKILLS_DIR/$skill_name" 2>/dev/null || true
        fi
    done
fi

echo ""
echo "[3/3] Verifying installation..."
if command -v odoo-upgrader &> /dev/null; then
    echo "  ✅ 'odoo-upgrader' CLI is installed and available in PATH."
else
    echo "  ℹ️ CLI installed. You can run it via: python3 -m odoo_upgrader.cli"
fi

echo ""
echo "=================================================================="
echo "                     🎉 Setup Complete!                          "
echo "=================================================================="
echo ""
echo "How to use:"
echo "1. In Antigravity / Claude Code / Gemini Chat:"
echo "   Type:  /upgrade-odoo /path/to/your/custom_addons"
echo ""
echo "2. From Terminal CLI:"
echo "   Run:   upgrade-odoo /path/to/addons --target 19"
echo "   With test DB install:"
echo "          upgrade-odoo /path/to/addons --target 19 --test-install --db my_test_db"
echo ""
echo "3. In Cursor IDE:"
echo "   The .cursorrules and .cursor/rules/ are pre-configured to detect Odoo"
echo "   upgrades and apply these exact migration steps automatically."
echo "=================================================================="
