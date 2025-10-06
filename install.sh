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
wget -q -O "$PLUGIN_DIR/plugin.png" "$REPO_URL/plugin.png"

# Vérification
if [ -f "$PLUGIN_DIR/plugin.py" ] && [ -f "$PLUGIN_DIR/__init__.py" ]; then
    echo "✅ Fichiers principaux installés"
    
    # Vérifier l'icône
    if [ -f "$PLUGIN_DIR/plugin.png" ]; then
        echo "🖼️ Icône plugin.png installée"
    else
        echo "⚠️ Icône non téléchargée"
    fi
    
    echo "📍 Emplacement: $PLUGIN_DIR"
    
    # Redémarrage automatique
    echo "🔄 Redémarrage d'Enigma2 dans 3 secondes..."
    sleep 3
    
    echo "🔁 Lancement du redémarrage..."
    
    # Méthode de redémarrage
    if [ -f "/etc/init.d/enigma2" ]; then
        /etc/init.d/enigma2 restart
    elif pidof enigma2 > /dev/null; then
        killall enigma2
        sleep 2
        enigma2 &
    fi
    
else
    echo "❌ Erreur lors de l'installation"
fi
