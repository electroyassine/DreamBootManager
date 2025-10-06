#!/bin/sh
echo "🧭 DreamBootManager Installation..."
echo "📦 Source: https://github.com/electroyassine/DreamBootManager"

PLUGIN_DIR="/usr/lib/enigma2/python/Plugins/Extensions/DreamBootManager"
REPO_URL="https://raw.githubusercontent.com/electroyassine/DreamBootManager/main"

# Nettoyer l'ancienne installation
rm -rf "$PLUGIN_DIR"
mkdir -p "$PLUGIN_DIR"

# Télécharger les fichiers
echo "📥 Téléchargement des fichiers..."
wget -q -O "$PLUGIN_DIR/plugin.py" "$REPO_URL/plugin.py"
wget -q -O "$PLUGIN_DIR/__init__.py" "$REPO_URL/__init__.py"

# Vérification
if [ -f "$PLUGIN_DIR/plugin.py" ] && [ -f "$PLUGIN_DIR/__init__.py" ]; then
    echo "✅ DreamBootManager installé avec succès!"
    echo "📍 Emplacement: $PLUGIN_DIR"
    
    # Redémarrage automatique
    echo "🔄 Redémarrage d'Enigma2 dans 3 secondes..."
    sleep 3
    echo "🔁 Lancement du redémarrage..."
    systemctl restart enigma2
    
else
    echo "❌ Erreur lors de l'installation"
fi
