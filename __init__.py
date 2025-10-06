# -*- coding: utf-8 -*-
"""
DreamBootManager - Plugin for Enigma2
"""

from Plugins.Plugin import PluginDescriptor

def main(session, **kwargs):
    """Fonction principale pour lancer le plugin"""
    try:
        # Import ici pour éviter les erreurs au chargement
        from plugin import DreamBootManager
        session.open(DreamBootManager)
    except Exception as e:
        print(f"[DreamBootManager] Erreur: {str(e)}")
        # Message d'erreur pour l'utilisateur
        from Screens.MessageBox import MessageBox
        session.open(MessageBox, f"Erreur DreamBootManager: {str(e)}", MessageBox.TYPE_ERROR)

def Plugins(**kwargs):
    """Déclaration du plugin pour Enigma2"""
    return PluginDescriptor(
        name="DreamBootManager",
        description="Gestionnaire de boot pour Enigma2",
        where=PluginDescriptor.WHERE_PLUGINMENU,
        fnc=main
    )
