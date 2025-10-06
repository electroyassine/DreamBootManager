#!/bin/sh
# Fichier: install.sh - À ajouter dans votre repo GitHub

echo "🧭 DreamBootManager Installer"
echo "📥 Téléchargement depuis GitHub..."

PLUGIN_DIR="/usr/lib/enigma2/python/Plugins/Extensions/DreamBootManager"
mkdir -p "$PLUGIN_DIR"

wget -q -O "$PLUGIN_DIR/plugin.py" \
  "https://raw.githubusercontent.com/electroyassine/DreamBootManager/main/plugin.py"

wget -q -O "$PLUGIN_DIR/__init__.py" \
  "https://raw.githubusercontent.com/electroyassine/DreamBootManager/main/__init__.py"

echo "✅ Installation terminée! Redémarrez Enigma2."