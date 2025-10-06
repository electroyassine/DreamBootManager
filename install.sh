#!/bin/sh
PLUGIN_DIR="/usr/lib/enigma2/python/Plugins/Extensions/DreamBootManager"
REPO_URL="https://raw.githubusercontent.com/electroyassine/DreamBootManager/main"

mkdir -p "$PLUGIN_DIR"

wget -q -O "$PLUGIN_DIR/plugin.py" "$REPO_URL/plugin.py"
wget -q -O "$PLUGIN_DIR/__init__.py" "$REPO_URL/__init__.py"
wget -q -O "$PLUGIN_DIR/plugin.png" "$REPO_URL/plugin.png"

sleep 2
/etc/init.d/enigma2 restart
