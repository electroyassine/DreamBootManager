#!/bin/sh
echo "🧭 DreamBootManager Installation..."
echo "📦 Source: https://github.com/electroyassine/DreamBootManager"

PLUGIN_DIR="/usr/lib/enigma2/python/Plugins/Extensions/DreamBootManager"
REPO_URL="https://raw.githubusercontent.com/electroyassine/DreamBootManager/main"

# Nettoyer l'ancienne installation
rm -rf "$PLUGIN_DIR"
mkdir -p "$PLUGIN_DIR"

# Télécharger les fichiers avec vérification
echo "📥 Téléchargement de plugin.py..."
if wget -q -O "$PLUGIN_DIR/plugin.py" "$REPO_URL/plugin.py"; then
    echo "✅ plugin.py téléchargé"
else
    echo "❌ Erreur plugin.py"
    exit 1
fi

echo "📥 Téléchargement de __init__.py..."
if wget -q -O "$PLUGIN_DIR/__init__.py" "$REPO_URL/__init__.py"; then
    echo "✅ __init__.py téléchargé"
else
    echo "❌ Erreur __init__.py"
    exit 1
fi

# Vérifier la taille des fichiers
SIZE_PLUGIN=$(stat -c%s "$PLUGIN_DIR/plugin.py" 2>/dev/null || echo "0")
SIZE_INIT=$(stat -c%s "$PLUGIN_DIR/__init__.py" 2>/dev/null || echo "0")

echo "📊 Taille plugin.py: $SIZE_PLUGIN octets"
echo "📊 Taille __init__.py: $SIZE_INIT octets"

if [ "$SIZE_PLUGIN" -gt 1000 ] && [ "$SIZE_INIT" -gt 100 ]; then
    echo "🎉 DreamBootManager installé avec succès!"
    echo "📍 Dossier: $PLUGIN_DIR"
    echo "🔁 Redémarrez Enigma2 → Menu Plugins → Extensions"
else
    echo "❌ Fichiers corrompus ou incomplets"
    echo "🔍 Contenu du dossier:"
    ls -la "$PLUGIN_DIR/"
fi
