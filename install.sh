#!/bin/sh
echo "🧭 Installation de DreamBootManager..."
echo "📦 Téléchargement depuis GitHub..."

PLUGIN_DIR="/usr/lib/enigma2/python/Plugins/Extensions/DreamBootManager"
REPO_URL="https://raw.githubusercontent.com/electroyassine/DreamBootManager/main"

# Créer le dossier
echo "📁 Création du dossier: $PLUGIN_DIR"
mkdir -p "$PLUGIN_DIR"

# Télécharger les fichiers
echo "📥 Téléchargement des fichiers..."
wget -q -O "$PLUGIN_DIR/__init__.py" "$REPO_URL/__init__.py"
wget -q -O "$PLUGIN_DIR/plugin.py" "$REPO_URL/plugin.py"

# Vérification
if [ -f "$PLUGIN_DIR/plugin.py" ] && [ -f "$PLUGIN_DIR/__init__.py" ]; then
    echo "✅ DreamBootManager installé avec succès!"
    echo "📍 Emplacement: $PLUGIN_DIR"
    echo "🔁 Redémarrez Enigma2 pour activer le plugin"
    echo "💡 Accès: Menu → Plugins → Extensions → DreamBootManager"
else
    echo "❌ Erreur lors de l'installation"
    echo "📋 Fichiers manquants, vérifiez:"
    ls -la "$PLUGIN_DIR/"
fi
