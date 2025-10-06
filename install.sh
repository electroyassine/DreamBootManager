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
    
    # Redémarrage automatique - Méthodes compatibles Enigma2
    echo "🔄 Redémarrage d'Enigma2 dans 3 secondes..."
    sleep 3
    
    echo "🔁 Lancement du redémarrage..."
    
    # Méthode 1: init.d (la plus courante sur Enigma2)
    if [ -f "/etc/init.d/enigma2" ]; then
        echo "📦 Méthode: /etc/init.d/enigma2 restart"
        /etc/init.d/enigma2 restart
        
    # Méthode 2: kill et relance
    elif pidof enigma2 > /dev/null; then
        echo "⚡ Méthode: killall enigma2"
        killall enigma2
        sleep 2
        enigma2 &
        
    # Méthode 3: reboot GUI
    else
        echo "🖥️ Méthode: wget pour redémarrer GUI"
        wget -q -O - "http://127.0.0.1/web/restart" > /dev/null 2>&1
    fi
    
else
    echo "❌ Erreur lors de l'installation"
fi
