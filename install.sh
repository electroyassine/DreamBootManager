#!/bin/sh
PLUGIN_DIR="/usr/lib/enigma2/python/Plugins/Extensions/DreamBootManager"
REPO_URL="https://raw.githubusercontent.com/electroyassine/DreamBootManager/main"

# Création du dossier
mkdir -p "$PLUGIN_DIR"

# Téléchargement silencieux des fichiers
wget -q -O "$PLUGIN_DIR/plugin.py" "$REPO_URL/plugin.py"
wget -q -O "$PLUGIN_DIR/__init__.py" "$REPO_URL/__init__.py" 
wget -q -O "$PLUGIN_DIR/plugin.png" "$REPO_URL/plugin.png"

# Redémarrage GUI
sleep 2
[ -f "/etc/init.d/enigma2" ] && /etc/init.d/enigma2 restart
