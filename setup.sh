#!/usr/bin/env bash
#
# Quick setup for Codey-v4 - adds to PATH
#
# Run this if you've already installed dependencies
# and just need to make codey4 available system-wide.
#

CODEY_V4_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Determine shell config
if [ -n "$BASH_VERSION" ]; then
    SHELL_CONFIG="$HOME/.bashrc"
elif [ -n "$ZSH_VERSION" ]; then
    SHELL_CONFIG="$HOME/.zshrc"
else
    SHELL_CONFIG="$HOME/.bashrc"
fi

# Make scripts executable
chmod +x "$CODEY_V4_DIR/codey4"
chmod +x "$CODEY_V4_DIR/codeyd4"

# Add to PATH if not already there
if ! grep -q "codey-v4" "$SHELL_CONFIG" 2>/dev/null; then
    echo "" >> "$SHELL_CONFIG"
    echo "# Codey-v4" >> "$SHELL_CONFIG"
    echo "export PATH=\"$CODEY_V4_DIR:\$PATH\"" >> "$SHELL_CONFIG"
    echo "Added codey4 to PATH in $SHELL_CONFIG"
else
    echo "codey4 already in PATH"
fi

# Source the config
source "$SHELL_CONFIG"

# Create daemon directory
mkdir -p "$HOME/.codey-v4"

echo ""
echo "Setup complete!"
echo ""
echo "Now you can use Codey-v4:"
echo "  codeyd4 start          # Start the daemon"
echo "  codey4 \"hello\"         # Send a task"
echo "  codey4 status          # Check status"
echo ""
