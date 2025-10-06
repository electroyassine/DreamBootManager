# -*- coding: utf-8 -*-
from Plugins.Plugin import PluginDescriptor

def main(session, **kwargs):
    try:
        from plugin import DreamBootManager
        session.open(DreamBootManager)
    except Exception as e:
        print(f"[DreamBootManager] Error: {e}")
        from Screens.MessageBox import MessageBox
        session.open(MessageBox, f"DreamBootManager Error: {e}", MessageBox.TYPE_ERROR)

def Plugins(**kwargs):
    return PluginDescriptor(
        name="DreamBootManager",
        description="Boot Manager for Enigma2",
        where=PluginDescriptor.WHERE_PLUGINMENU,
        icon="plugin.png",  # ← Cette ligne doit être présente
        fnc=main
    )
