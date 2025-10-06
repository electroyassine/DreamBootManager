# -*- coding: utf-8 -*-
"""
DreamBootManager - Plugin for Enigma2
Gestionnaire de boot pour les receivers Enigma2
"""

from __init__ import _
from Plugins.Plugin import PluginDescriptor

# Importation du plugin principal
from plugin import DreamBootManager

# Configuration du plugin
PLUGIN_NAME = "DreamBootManager"
PLUGIN_DESCRIPTION = "Gestionnaire de boot pour Enigma2"
PLUGIN_VERSION = "1.0"
PLUGIN_AUTHOR = "electroyassine"

def main(session, **kwargs):
    """
    Fonction principale pour lancer le plugin
    """
    try:
        # Créer et afficher l'interface principale
        session.open(DreamBootManager)
    except Exception as e:
        print(f"[{PLUGIN_NAME}] Erreur lors du lancement: {str(e)}")
        from Screens.MessageBox import MessageBox
        session.open(MessageBox, f"Erreur DreamBootManager: {str(e)}", MessageBox.TYPE_ERROR)

def Plugins(**kwargs):
    """
    Déclaration du plugin pour Enigma2
    """
    try:
        # Icône du plugin (optionnelle)
        icon_file = "plugin.png"
        
        # Descripteur du plugin pour le menu Extensions
        plugin_descriptor = PluginDescriptor(
            name=PLUGIN_NAME,
            description=PLUGIN_DESCRIPTION,
            where=PluginDescriptor.WHERE_PLUGINMENU,
            icon=icon_file,
            fnc=main
        )
        
        return [plugin_descriptor]
        
    except Exception as e:
        print(f"[{PLUGIN_NAME}] Erreur dans Plugins(): {str(e)}")
        # Retourner un descripteur minimal en cas d'erreur
        return [PluginDescriptor(
            name=PLUGIN_NAME,
            description=PLUGIN_DESCRIPTION,
            where=PluginDescriptor.WHERE_PLUGINMENU,
            fnc=main
        )]

# Informations de version
def getPluginInfo():
    """
    Retourne les informations du plugin
    """
    return {
        'name': PLUGIN_NAME,
        'description': PLUGIN_DESCRIPTION,
        'version': PLUGIN_VERSION,
        'author': PLUGIN_AUTHOR
    }

# Initialisation
print(f"[{PLUGIN_NAME}] Plugin initialisé - Version {PLUGIN_VERSION}")