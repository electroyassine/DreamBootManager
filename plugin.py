# -*- coding: utf-8 -*-
import os
import re
import glob
import shutil
import tarfile
import hashlib
import zipfile
import urllib.request
import urllib.error
from datetime import datetime
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.Label import Label
from Components.MenuList import MenuList
from Components.ActionMap import ActionMap, HelpableActionMap
from Components.ProgressBar import ProgressBar
from Components.Sources.StaticText import StaticText
from Tools.Directories import fileExists, pathExists
from enigma import eTimer

class DreamBootManagerScreen(Screen):
    skin = """
    <screen position="center,center" size="900,600" title="Dream Boot Manager">
        <widget name="title" position="0,50" size="900,80" font="Regular;36" halign="center" transparent="1" />
        <widget name="menu" position="100,150" size="700,350" itemHeight="70" font="Regular;28" transparent="1" />
        <widget name="status" position="0,520" size="900,50" font="Regular;22" halign="center" transparent="1" />
    </screen>
    """
    
    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        self.setTitle("Dream Boot Manager")
        
        self["title"] = Label("DREAM BOOT MANAGER")
        
        menu_list = [
            "1. Multiboot Selector",
            "2. Multiboot Deletion",
            "3. Flash Recovery Image",
            "4. Backup Recovery Image",
            "5. SD Card Partition"
        ]
        
        self["menu"] = MenuList(menu_list)
        self["status"] = Label("▲▼ Navigation   │   OK: Select   │   INFO: About   │   EXIT: Close")
        
        # Essayer différentes configurations de ActionMap
        self["actions"] = ActionMap(["SetupActions", "ColorActions", "OkCancelActions", "NavigationActions"], 
        {
            "ok": self.ok,
            "cancel": self.close,
            "up": self.up,
            "down": self.down,
            "info": self.show_info,
        }, -1)
        
    def up(self):
        self["menu"].up()
        
    def down(self):
        self["menu"].down()
        
    def ok(self):
        selection = self["menu"].getCurrent()
        if selection:
            if "Multiboot Selector" in selection:
                self.multiboot_selector()
            elif "Multiboot Deletion" in selection:
                self.multiboot_deletion()
            elif "Flash Recovery Image" in selection:
                self.flash_recovery_image()
            elif "Backup Recovery Image" in selection:
                self.backup_recovery_image()
            elif "SD Card Partition" in selection:
                self.sd_card_partition()

    def show_info(self):
        """Affiche les informations sur le plugin"""
        info_text = "Gestionnaire Multiboot Avancé\npour Dreambox ONE & TWO\n\nby ELECTRO YASSINE"
        
        self.session.open(MessageBox, info_text, MessageBox.TYPE_INFO, timeout=10)
    
    def multiboot_selector(self):
        """Affiche la liste des images depuis bootconfig.txt"""
        boot_manager = BootManager()
        images = boot_manager.get_boot_images()
        
        if not images:
            self.session.open(MessageBox, 
                "No boot images found in bootconfig.txt!\n\nCheck /data/bootconfig.txt", 
                MessageBox.TYPE_ERROR)
            return
        
        self.session.openWithCallback(self.on_image_selected, ImageSelectionScreen, images)
    
    def multiboot_deletion(self):
        """Multiboot deletion functionality"""
        boot_manager = BootManager()
        slots = boot_manager.get_multiboot_slots()
        
        if not slots:
            self.session.open(MessageBox, 
                "No multiboot slots found!\n\nCheck if multiboot is properly configured.", 
                MessageBox.TYPE_ERROR)
            return
        
        self.session.openWithCallback(self.on_slot_selected, SlotSelectionScreen, slots, "Delete Slot Image")
    
    def flash_recovery_image(self):
        """Ouvre le Flash Manager ou Software Manager"""
        try:
            # Essayer d'importer FlashManager depuis Screens
            from Screens.FlashManager import FlashManager
            self.session.open(FlashManager)
        except ImportError:
            try:
                # Si échec, ouvrir SoftwareManager
                from Plugins.SystemPlugins.SoftwareManager.plugin import SoftwareManager
                self.session.open(SoftwareManager)
            except ImportError:
                self.session.open(MessageBox,
                    "Please use the Software Manager from plugins menu to flash recovery images.",
                    MessageBox.TYPE_INFO)
    
    def backup_recovery_image(self):
        """Ouvre l'écran de sauvegarde complète"""
        try:
            # Essayer d'importer l'écran de sauvegarde depuis Screens
            from Screens.BackupRestore import BackupScreen
            self.session.open(BackupScreen)
        except ImportError:
            try:
                # Essayer un autre chemin possible
                from Screens.ImageBackup import ImageBackup
                self.session.open(ImageBackup)
            except ImportError:
                try:
                    # Essayer avec SoftwareManager
                    from Plugins.SystemPlugins.SoftwareManager.BackupRestore import ImageBackup
                    self.session.open(ImageBackup)
                except ImportError:
                    self.session.open(MessageBox,
                        "Backup feature not available on this image!\n\nPlease use the built-in backup function from the software manager.",
                        MessageBox.TYPE_INFO)
    
    def on_slot_selected(self, selected_slot):
        """Callback après sélection d'un slot"""
        if selected_slot is None:
            return
            
        if not selected_slot['image_exists']:
            self.session.openWithCallback(self.return_to_deletion_menu, MessageBox,
                "Slot %s is already empty!\n\nNo image to delete." % selected_slot['name'],
                MessageBox.TYPE_INFO)
            return
                
        message = "Are you sure you want to delete the image from:\n\n%s?\n\nPartition: %s" % (selected_slot['name'], selected_slot['partition'])
        self.session.openWithCallback(
            lambda result: self.confirm_deletion(result, selected_slot), 
            MessageBox, message, MessageBox.TYPE_YESNO)
    
    def return_to_deletion_menu(self, result=None):
        """Retourne au menu de suppression"""
        self.multiboot_deletion()
    
    def confirm_deletion(self, result, slot_info):
        """Confirme la suppression d'une image"""
        if result:
            boot_manager = BootManager()
            success, message = boot_manager.delete_slot_image(slot_info)
            if success:
                self.session.openWithCallback(self.return_to_deletion_menu, MessageBox,
                    "✓ Image successfully deleted from:\n%s\n\nPartition: %s" % (slot_info['name'], slot_info['partition']),
                    MessageBox.TYPE_INFO)
            else:
                self.session.openWithCallback(self.return_to_deletion_menu, MessageBox,
                    "✗ Error deleting image from:\n%s\n\n%s" % (slot_info['name'], message),
                    MessageBox.TYPE_ERROR)
        else:
            self.return_to_deletion_menu()
    
    def sd_card_partition(self):
        """SD Card partitioning functionality"""
        message = "This will partition your SD card for multiboot:\n\n" \
                 "• Partition 1: Remaining capacity FAT32 (DREAMCARD)\n" \
                 "• Partition 2: 1.7 GB EXT4 (Slot 5)\n" \
                 "• Partition 3: 1.7 GB EXT4 (Slot 6)\n" \
                 "• Partition 4: 1.7 GB EXT4 (Slot 7)\n" \
                 "• Partition 5: 1.7 GB EXT4 (Slot 8)\n\n" \
                 "All data on the SD card will be lost!\n\nContinue?"
        
        self.session.openWithCallback(
            lambda result: self.confirm_sd_partitioning(result),
            MessageBox, message, MessageBox.TYPE_YESNO)
    
    def confirm_sd_partitioning(self, result):
        """Confirme le partitionnement de la SD card"""
        if result:
            boot_manager = BootManager()
            success, message = boot_manager.partition_sd_card()
            if success:
                self.session.openWithCallback(self.auto_restart_gui, MessageBox,
                    "✓ SD card partitioned successfully!\n\n%s\n\nGUI will restart automatically in 3 seconds." % message,
                    MessageBox.TYPE_INFO, timeout=3)
            else:
                self.session.open(MessageBox,
                    "✗ Error partitioning SD card:\n\n%s" % message,
                    MessageBox.TYPE_ERROR)
    
    def auto_restart_gui(self, result=None):
        """Redémarre automatiquement l'IGU après partitionnement réussi"""
        print("[DreamBootManager] Auto-restarting GUI...")
        from Screens.Standby import TryQuitMainloop
        self.session.open(TryQuitMainloop, 3)
    
    def on_image_selected(self, selected_image):
        """Callback après sélection d'une image"""
        if selected_image:
            boot_manager = BootManager()
            if boot_manager.set_boot_image(selected_image):
                self.session.openWithCallback(self.reboot_confirmation, MessageBox,
                    "✓ '%s' selected successfully!\n\nReboot to start this image?" % selected_image['name'],
                    MessageBox.TYPE_YESNO)
            else:
                self.session.open(MessageBox,
                    "✗ Error selecting '%s'!\n\nCheck file permissions." % selected_image['name'],
                    MessageBox.TYPE_ERROR)
    
    def reboot_confirmation(self, result):
        """Demande confirmation pour redémarrer"""
        if result:
            from Screens.Standby import TryQuitMainloop
            self.session.open(TryQuitMainloop, 2)


class SlotSelectionScreen(Screen):
    """Écran de sélection des slots multiboot"""
    skin = """
    <screen position="center,center" size="1000,700" title="Select Slot">
        <widget name="title" position="0,50" size="1000,80" font="Regular;32" halign="center" transparent="1" />
        <widget name="menu" position="50,150" size="900,450" itemHeight="60" font="Regular;26" transparent="1" />
        <widget name="status" position="0,620" size="1000,50" font="Regular;22" halign="center" transparent="1" />
    </screen>
    """
    
    def __init__(self, session, slots, title="Select Slot"):
        Screen.__init__(self, session)
        self.slots = slots
        self.setTitle(title)
        
        self["title"] = Label(title.upper())
        
        slot_list = []
        for slot in self.slots:
            if slot['image_exists']:
                # Afficher le nom réel de l'image depuis /etc/issue
                display_text = "%s\n✓ %s\nPartition: %s" % (slot['name'], slot['image_name'], slot['partition'])
            else:
                # Pour les slots vides, afficher simplement "Empty"
                display_text = "%s\n✗ Empty\nPartition: %s" % (slot['name'], slot['partition'])
            slot_list.append(display_text)
        
        self["menu"] = MenuList(slot_list)
        self["status"] = Label("▲▼ Navigation   │   OK: Select   │   EXIT: Back")
        
        self["actions"] = ActionMap(["OkCancelActions", "NavigationActions"], {
            "ok": self.ok,
            "cancel": self.cancel,
            "up": self.up,
            "down": self.down
        }, -1)
    
    def up(self):
        self["menu"].up()
    
    def down(self):
        self["menu"].down()
    
    def ok(self):
        selection = self["menu"].getCurrent()
        if selection:
            index = self["menu"].getSelectionIndex()
            self.close(self.slots[index])
    
    def cancel(self):
        self.close(None)


class ImageSelectionScreen(Screen):
    """Écran de sélection des images multiboot"""
    skin = """
    <screen position="center,center" size="1000,700" title="Select Boot Image">
        <widget name="title" position="0,50" size="1000,80" font="Regular;32" halign="center" transparent="1" />
        <widget name="menu" position="50,150" size="900,450" itemHeight="60" font="Regular;26" transparent="1" />
        <widget name="status" position="0,620" size="1000,50" font="Regular;22" halign="center" transparent="1" />
    </screen>
    """
    
    def __init__(self, session, images, deletion_mode=False):
        Screen.__init__(self, session)
        self.images = images
        self.deletion_mode = deletion_mode
        self.setTitle("Select Boot Image")
        
        self["title"] = Label("SELECT BOOT IMAGE")
        
        image_list = []
        boot_manager = BootManager()
        current_boot = boot_manager.get_current_boot()
        
        for img in self.images:
            status = " ← CURRENT" if img['name'] == current_boot else ""
            display_text = "%s%s" % (img['name'], status)
            image_list.append(display_text)
        
        self["menu"] = MenuList(image_list)
        self["status"] = Label("▲▼ Navigation   │   OK: Select   │   EXIT: Back")
        
        self["actions"] = ActionMap(["OkCancelActions", "NavigationActions"], {
            "ok": self.ok,
            "cancel": self.cancel,
            "up": self.up,
            "down": self.down
        }, -1)
    
    def up(self):
        self["menu"].up()
    
    def down(self):
        self["menu"].down()
    
    def ok(self):
        selection = self["menu"].getCurrent()
        if selection:
            index = self["menu"].getSelectionIndex()
            self.close(self.images[index])
    
    def cancel(self):
        self.close(None)


class BootManager:
    """Gestionnaire de boot pour lire/écrire bootconfig.txt"""
    
    def __init__(self):
        self.bootconfig_path = "/data/bootconfig.txt"
        if not fileExists(self.bootconfig_path):
            self.bootconfig_path = "/boot/bootconfig.txt"
        self.ensure_bootconfig()
        self.create_all_startup_files()
    
    def ensure_bootconfig(self):
        """S'assure que bootconfig.txt existe avec la configuration U-Boot correcte"""
        if not fileExists(self.bootconfig_path):
            print("[BootManager] Creating bootconfig.txt with U-Boot configuration...")
            self.create_default_bootconfig()
    
    def create_default_bootconfig(self):
        """Crée le fichier bootconfig.txt par défaut avec la configuration U-Boot mise à jour"""
        bootconfig_content = """default=0
details=0
timeout=10
fb_pos=100,400
fb_size=1080,300

[Dreambox Image]
cmd=ext4load mmc 1:5 1080000 /boot/kernel.img;bootm;
arg=${bootargs} root=/dev/mmcblk0p5 rootfstype=ext4 kernel=/boot/kernel.img logo=osd0,loaded,0x7f800000 vout=1080p50hz,enable hdmimode=1080p50hz fb_width=1280 fb_height=720 panel_type=lcd_4

[Dreambox Image 1]
cmd=ext4load mmc 1:6 1080000 /boot/kernel.img;bootm;
arg=${bootargs} root=/dev/mmcblk0p6 rootfstype=ext4 kernel=/boot/kernel.img logo=osd0,loaded,0x7f800000 vout=1080p50hz,enable hdmimode=1080p50hz fb_width=1280 fb_height=720 panel_type=lcd_4

[Dreambox Image 2]
cmd=ext4load mmc 1:7 1080000 /boot/kernel.img;bootm;
arg=${bootargs} root=/dev/mmcblk0p7 rootfstype=ext4 kernel=/boot/kernel.img logo=osd0,loaded,0x7f800000 vout=1080p50hz,enable hdmimode=1080p50hz fb_width=1280 fb_height=720 panel_type=lcd_4

[Dreambox Image 3]
cmd=ext4load mmc 1:8 1080000 /boot/kernel.img;bootm;
arg=${bootargs} root=/dev/mmcblk0p8 rootfstype=ext4 kernel=/boot/kernel.img logo=osd0,loaded,0x7f800000 vout=1080p50hz,enable hdmimode=1080p50hz fb_width=1280 fb_height=720 panel_type=lcd_4

[SDcard Slot 5]
cmd=fatload mmc 0:1 1080000 /kernel2.img;bootm;
arg=${bootargs} root=/dev/mmcblk1p2 rootfstype=ext4 kernel=/kernel2.img logo=osd0,loaded,0x7f800000 vout=1080p50hz,enable hdmimode=1080p50hz fb_width=1280 fb_height=720 panel_type=lcd_4

[SDcard Slot 6]
cmd=fatload mmc 0:1 1080000 /kernel3.img;bootm;
arg=${bootargs} root=/dev/mmcblk1p3 rootfstype=ext4 kernel=/kernel3.img logo=osd0,loaded,0x7f800000 vout=1080p50hz,enable hdmimode=1080p50hz fb_width=1280 fb_height=720 panel_type=lcd_4

[SDcard Slot 7]
cmd=fatload mmc 0:1 1080000 /kernel4.img;bootm;
arg=${bootargs} root=/dev/mmcblk1p4 rootfstype=ext4 kernel=/kernel4.img logo=osd0,loaded,0x7f800000 vout=1080p50hz,enable hdmimode=1080p50hz fb_width=1280 fb_height=720 panel_type=lcd_4

[SDcard Slot 8]
cmd=fatload mmc 0:1 1080000 /kernel5.img;bootm;
arg=${bootargs} root=/dev/mmcblk1p5 rootfstype=ext4 kernel=/kernel5.img logo=osd0,loaded,0x7f800000 vout=1080p50hz,enable hdmimode=1080p50hz fb_width=1280 fb_height=720 panel_type=lcd_4
"""
        try:
            with open(self.bootconfig_path, 'w') as f:
                f.write(bootconfig_content)
            print("[BootManager] ✓ Default bootconfig.txt created successfully")
            return True
        except Exception as e:
            print("[BootManager] ✗ Error creating bootconfig.txt:", str(e))
            return False
    
    def create_all_startup_files(self):
        """Crée tous les fichiers STARTUP pour les slots MMC et SD Card"""
        try:
            mmc_startup_contents = {
                'STARTUP_1': 'root=/dev/mmcblk0p5 rootfstype=ext4 kernel=/boot/kernel.img\n',
                'STARTUP_2': 'root=/dev/mmcblk0p6 rootfstype=ext4 kernel=/boot/kernel.img\n',
                'STARTUP_3': 'root=/dev/mmcblk0p7 rootfstype=ext4 kernel=/boot/kernel.img\n',
                'STARTUP_4': 'root=/dev/mmcblk0p8 rootfstype=ext4 kernel=/boot/kernel.img\n'
            }
            
            sd_startup_contents = {
                'STARTUP_5': 'root=/dev/mmcblk1p2 rootfstype=ext4 kernel=/kernel2.img\n',
                'STARTUP_6': 'root=/dev/mmcblk1p3 rootfstype=ext4 kernel=/kernel3.img\n',
                'STARTUP_7': 'root=/dev/mmcblk1p4 rootfstype=ext4 kernel=/kernel4.img\n',
                'STARTUP_8': 'root=/dev/mmcblk1p5 rootfstype=ext4 kernel=/kernel5.img\n'
            }
            
            all_startup_contents = {**mmc_startup_contents, **sd_startup_contents}
            
            for startup_file, content in all_startup_contents.items():
                try:
                    file_path = "/data/" + startup_file
                    with open(file_path, 'w') as f:
                        f.write(content)
                    os.chmod(file_path, 0o755)
                    print("[BootManager] Created %s in /data/" % startup_file)
                except Exception as e:
                    print("[BootManager] Error creating %s: %s" % (startup_file, str(e)))
            
            print("[BootManager] ✓ All STARTUP files created successfully in /data/")
            return True
            
        except Exception as e:
            print("[BootManager] Error creating STARTUP files:", str(e))
            return False
    
    def get_multiboot_slots(self):
        """Récupère la liste des slots multiboot avec nom d'image"""
        slots = []
        
        internal_slots = [
            {'name': 'Slot 1 (Multiboot 1)', 'partition': '/dev/mmcblk0p5', 'mount_point': '/media/mmcblk0p5', 'startup_file': 'STARTUP_1'},
            {'name': 'Slot 2 (Multiboot 2)', 'partition': '/dev/mmcblk0p6', 'mount_point': '/media/mmcblk0p6', 'startup_file': 'STARTUP_2'},
            {'name': 'Slot 3 (Multiboot 3)', 'partition': '/dev/mmcblk0p7', 'mount_point': '/media/mmcblk0p7', 'startup_file': 'STARTUP_3'},
            {'name': 'Slot 4 (Multiboot 4)', 'partition': '/dev/mmcblk0p8', 'mount_point': '/media/mmcblk0p8', 'startup_file': 'STARTUP_4'},
        ]
        
        sd_slots = [
            {'name': 'SDcard Slot 5', 'partition': '/dev/mmcblk1p2', 'mount_point': '/media/mmcblk1p2', 'startup_file': 'STARTUP_5'},
            {'name': 'SDcard Slot 6', 'partition': '/dev/mmcblk1p3', 'mount_point': '/media/mmcblk1p3', 'startup_file': 'STARTUP_6'},
            {'name': 'SDcard Slot 7', 'partition': '/dev/mmcblk1p4', 'mount_point': '/media/mmcblk1p4', 'startup_file': 'STARTUP_7'},
            {'name': 'SDcard Slot 8', 'partition': '/dev/mmcblk1p5', 'mount_point': '/media/mmcblk1p5', 'startup_file': 'STARTUP_8'},
        ]
        
        for slot in internal_slots:
            if self.check_partition_exists(slot['partition']):
                image_exists, image_name = self.check_slot_has_image(slot)
                slot['image_exists'] = image_exists
                slot['image_name'] = image_name
                slots.append(slot)
        
        for slot in sd_slots:
            if self.check_partition_exists(slot['partition']):
                image_exists, image_name = self.check_slot_has_image(slot)
                slot['image_exists'] = image_exists
                slot['image_name'] = image_name
                slots.append(slot)
        
        return slots
    
    def get_sd_card_size(self):
        """Récupère la taille totale de la SD card en Mo"""
        try:
            cmd = "fdisk -l /dev/mmcblk1 | grep 'Disk /dev/mmcblk1' | awk '{print $3}'"
            size_gb = float(os.popen(cmd).read().strip())
            size_mb = int(size_gb * 1024)
            return size_mb
        except:
            return 8192
    
    def partition_sd_card(self):
        """Partitionne la SD card avec les partitions spécifiées"""
        try:
            print("[BootManager] Starting SD card partitioning...")
            
            if not self.check_partition_exists("/dev/mmcblk1"):
                return False, "SD card not found at /dev/mmcblk1"
            
            sd_size_mb = self.get_sd_card_size()
            print("[BootManager] SD card size:", sd_size_mb, "MB")
            
            fat32_size_mb = sd_size_mb - (4 * 1740)
            ext4_size_mb = 1740
            
            print("[BootManager] FAT32 partition size:", fat32_size_mb, "MB")
            print("[BootManager] EXT4 partition size:", ext4_size_mb, "MB")
            
            for n in range(1, 6):
                partition = "/dev/mmcblk1p%d" % n
                umount_cmd = "umount -lf %s > /dev/null 2>&1" % partition
                os.system(umount_cmd)
            
            sgdisk_cmd = "sgdisk -z /dev/mmcblk1"
            result = os.system(sgdisk_cmd)
            if result != 0:
                return False, "Failed to clean partition table"
            
            parted_cmd = "parted --script /dev/mmcblk1 mklabel gpt"
            result = os.system(parted_cmd)
            if result != 0:
                return False, "Failed to create GPT partition table"
            
            start = 1
            end_fat32 = start + fat32_size_mb
            parted_cmd = "parted --script /dev/mmcblk1 mkpart DREAMCARD fat16 %dMB %dMB" % (start, end_fat32)
            result = os.system(parted_cmd)
            if result != 0:
                return False, "Failed to create partition 1 (FAT32)"
            
            for i in range(4):
                part_num = i + 2
                start_ext4 = end_fat32 if i == 0 else end_fat32 + (i * ext4_size_mb)
                end_ext4 = start_ext4 + ext4_size_mb
                
                parted_cmd = "parted --script /dev/mmcblk1 mkpart dreambox-rootfs ext4 %dMB %dMB" % (start_ext4, end_ext4)
                result = os.system(parted_cmd)
                if result != 0:
                    return False, "Failed to create partition %d (EXT4)" % part_num
            
            os.system("partprobe /dev/mmcblk1")
            os.system("sleep 2")
            
            print("[BootManager] Formatting partitions...")
            
            mkfs_cmd = "mkfs.fat -F 32 -n DREAMCARD /dev/mmcblk1p1"
            result = os.system(mkfs_cmd)
            if result != 0:
                return False, "Failed to format partition 1 (FAT32)"
            
            for n in range(2, 6):
                partition = "/dev/mmcblk1p%d" % n
                mkfs_cmd = "mkfs.ext4 -F %s" % partition
                result = os.system(mkfs_cmd)
                if result != 0:
                    return False, "Failed to format partition %d (EXT4)" % n
            
            print("[BootManager] Creating all STARTUP files in /data/...")
            startup_success = self.create_all_startup_files()
            if not startup_success:
                return False, "Failed to create STARTUP files"
            
            print("[BootManager] Ensuring bootconfig.txt is updated...")
            config_success = self.ensure_bootconfig_updated()
            if not config_success:
                return False, "Failed to update bootconfig.txt"
            
            return True, "SD card partitioned successfully:\n- FAT32: %d MB\n- 4x EXT4: %d MB each\n- All STARTUP files created in /data/\n- Bootconfig.txt updated" % (fat32_size_mb, ext4_size_mb)
            
        except Exception as e:
            return False, "Error during SD card partitioning: %s" % str(e)
    
    def ensure_bootconfig_updated(self):
        """S'assure que bootconfig.txt contient la configuration U-Boot correcte"""
        try:
            if fileExists(self.bootconfig_path):
                with open(self.bootconfig_path, 'r') as f:
                    content = f.read()
                
                required_entries = [
                    '[Dreambox Image]',
                    '[Dreambox Image 1]', 
                    '[Dreambox Image 2]',
                    '[Dreambox Image 3]',
                    '[SDcard Slot 5]',
                    '[SDcard Slot 6]',
                    '[SDcard Slot 7]',
                    '[SDcard Slot 8]'
                ]
                
                missing_entries = [entry for entry in required_entries if entry not in content]
                
                if missing_entries:
                    print("[BootManager] Missing entries in bootconfig, recreating...")
                    return self.create_default_bootconfig()
                else:
                    print("[BootManager] ✓ Bootconfig.txt already contains required entries")
                    return True
            else:
                print("[BootManager] Bootconfig.txt not found, creating...")
                return self.create_default_bootconfig()
                
        except Exception as e:
            print("[BootManager] Error checking bootconfig:", str(e))
            return self.create_default_bootconfig()
    
    def check_partition_exists(self, partition):
        """Vérifie si la partition existe"""
        return fileExists(partition) or os.path.exists(partition)
    
    def check_slot_has_image(self, slot):
        """Vérifie si une image est installée dans le slot et retourne son nom depuis /etc/issue"""
        try:
            if not os.path.exists(slot['mount_point']):
                os.makedirs(slot['mount_point'], exist_ok=True)
            
            mount_cmd = "mount %s %s 2>/dev/null" % (slot['partition'], slot['mount_point'])
            mount_result = os.system(mount_cmd)
            
            if mount_result != 0:
                return False, "Empty"
            
            image_exists = False
            image_name = "Empty"
            
            try:
                # Vérifier si la partition contient des fichiers (autre que lost+found)
                items = os.listdir(slot['mount_point'])
                valid_items = [item for item in items if item not in ['.', '..', 'lost+found']]
                image_exists = len(valid_items) > 0
                
                if image_exists:
                    # Lire /etc/issue pour obtenir le nom de l'image
                    issue_file = os.path.join(slot['mount_point'], 'etc', 'issue')
                    if os.path.exists(issue_file):
                        try:
                            with open(issue_file, 'r') as f:
                                content = f.read()
                            lines = content.split('\n')
                            if lines:
                                image_name = lines[0].strip()
                                # Nettoyer le nom
                                image_name = image_name.replace('Welcome to', '').replace('\\n', '').replace('\\l', '').strip()
                                if not image_name:
                                    image_name = "Unknown Image"
                        except:
                            image_name = "Unknown Image"
                    else:
                        # Si pas de /etc/issue, vérifier la présence de fichiers système
                        system_dirs = ['bin', 'sbin', 'usr', 'etc', 'lib']
                        has_system = any(os.path.exists(os.path.join(slot['mount_point'], d)) for d in system_dirs)
                        image_name = "Unknown System" if has_system else "Empty"
                else:
                    image_name = "Empty"
                    
            finally:
                self.force_unmount(slot['mount_point'])
            
            return image_exists, image_name
            
        except Exception as e:
            print("[BootManager] Error checking slot image:", str(e))
            return False, "Empty"
    
    def force_unmount(self, mount_point):
        """Force le démontage d'un point de montage"""
        try:
            if os.path.ismount(mount_point):
                umount_cmd = "umount %s 2>/dev/null" % mount_point
                os.system(umount_cmd)
                
                check_cmd = "mountpoint -q %s && umount -f %s 2>/dev/null" % (mount_point, mount_point)
                os.system(check_cmd)
                
                lazy_cmd = "umount -l %s 2>/dev/null" % mount_point
                os.system(lazy_cmd)
        except:
            pass
    
    def delete_slot_image(self, slot_info):
        """Nettoie et supprime l'image installée dans un slot sans supprimer la partition"""
        try:
            print("[BootManager] Deleting image from slot:", slot_info['name'])
            print("[BootManager] Partition:", slot_info['partition'])
            
            # Monter la partition
            if not os.path.exists(slot_info['mount_point']):
                os.makedirs(slot_info['mount_point'], exist_ok=True)
            
            mount_cmd = f"mount {slot_info['partition']} {slot_info['mount_point']} 2>/dev/null"
            if os.system(mount_cmd) != 0:
                return False, "Impossible de monter la partition"
            
            try:
                # Nettoyer complètement la partition (supprimer tous les fichiers et dossiers)
                for item in os.listdir(slot_info['mount_point']):
                    if item != 'lost+found':
                        item_path = os.path.join(slot_info['mount_point'], item)
                        try:
                            if os.path.isdir(item_path):
                                shutil.rmtree(item_path, ignore_errors=True)
                            else:
                                os.remove(item_path)
                        except Exception as e:
                            print(f"Warning: Cannot remove {item_path}: {e}")
                
                # Synchroniser
                os.system("sync")
                
                # Reformater la partition pour s'assurer qu'elle est complètement vide
                print("[BootManager] Reformatting partition to ensure clean state...")
                mkfs_cmd = f"mkfs.ext4 -F {slot_info['partition']} 2>/dev/null"
                reformat_result = os.system(mkfs_cmd)
                
                if reformat_result == 0:
                    print("[BootManager] ✓ Partition reformatted successfully")
                else:
                    print("[BootManager] ⚠ Could not reformat partition, but files were deleted")
                
                return True, "Image supprimée avec succès, slot maintenant vide"
                
            finally:
                # Toujours démonter
                self.force_unmount(slot_info['mount_point'])
            
        except Exception as e:
            error_msg = "Error during deletion: %s" % str(e)
            print("[BootManager]", error_msg)
            return False, error_msg
    
    def get_boot_images(self):
        """Extrait les images disponibles depuis bootconfig.txt"""
        images = []
        
        self.ensure_bootconfig()
        
        if not fileExists(self.bootconfig_path):
            print("[BootManager] Bootconfig not found:", self.bootconfig_path)
            return images
        
        try:
            with open(self.bootconfig_path, 'r') as f:
                content = f.read()
            
            pattern = r'\[([^\]]+)\]\s*\ncmd=([^\n]+)\s*\narg=([^\n]+)'
            matches = re.findall(pattern, content)
            
            for i, (name, cmd, arg) in enumerate(matches):
                images.append({
                    'name': name.strip(),
                    'cmd': cmd.strip(),
                    'arg': arg.strip(),
                    'index': i,
                    'source': 'bootconfig'
                })
            
            print("[BootManager] Found %d boot images in bootconfig" % len(images))
            
        except Exception as e:
            print("[BootManager] Error reading bootconfig:", str(e))
        
        return images
    
    def get_current_boot(self):
        """Détermine l'image de boot actuelle via le fichier STARTUP ou bootconfig"""
        try:
            startup_files = [
                "/boot/STARTUP",
                "/data/STARTUP", 
                "/tmp/STARTUP"
            ]
            
            for startup_file in startup_files:
                if fileExists(startup_file):
                    try:
                        with open(startup_file, 'r') as f:
                            content = f.read()
                        
                        for line in content.split('\n'):
                            if line and not line.startswith('#'):
                                images = self.get_boot_images()
                                for img in images:
                                    if img['cmd'] in line:
                                        return img['name']
                        break
                    except:
                        continue
            
            if fileExists(self.bootconfig_path):
                with open(self.bootconfig_path, 'r') as f:
                    content = f.read()
                
                default_match = re.search(r'default=(\d+)', content)
                if default_match:
                    default_index = int(default_match.group(1))
                    images = self.get_boot_images()
                    if 0 <= default_index < len(images):
                        return images[default_index]['name']
            
            return "Unknown"
            
        except Exception as e:
            print("[BootManager] Error detecting current boot:", str(e))
            return "Unknown"
    
    def set_boot_image(self, image_info):
        """Définit l'image de boot par défaut en modifiant bootconfig.txt et STARTUP"""
        try:
            print("[BootManager] Setting boot image:", image_info['name'])
            print("[BootManager] Command:", image_info['cmd'])
            
            success = self.set_boot_via_bootconfig(image_info)
            startup_success = self.set_boot_via_startup(image_info)
            
            return success or startup_success
                
        except Exception as e:
            print("[BootManager] Error setting boot image:", str(e))
        
        return False
    
    def set_boot_via_bootconfig(self, image_info):
        """Définit l'image de boot via bootconfig.txt"""
        try:
            if fileExists(self.bootconfig_path):
                with open(self.bootconfig_path, 'r') as f:
                    content = f.read()
                
                new_content = re.sub(r'default=\d+', 'default=%d' % image_info['index'], content)
                
                if 'default=' not in new_content:
                    new_content = 'default=%d\n%s' % (image_info['index'], new_content)
                
                with open(self.bootconfig_path, 'w') as f:
                    f.write(new_content)
                
                print("[BootManager] ✓ Bootconfig updated with default=%d" % image_info['index'])
                return True
        except Exception as e:
            print("[BootManager] Error updating bootconfig:", str(e))
        
        return False
    
    def set_boot_via_startup(self, image_info):
        """Définit l'image de boot via le fichier STARTUP"""
        try:
            uboot_cmd = "%s %s" % (image_info['cmd'], image_info['arg'])
            
            startup_files = [
                "/boot/STARTUP",
                "/data/STARTUP",
                "/tmp/STARTUP"
            ]
            
            for startup_file in startup_files:
                try:
                    with open(startup_file, 'w') as f:
                        f.write(uboot_cmd)
                    print("[BootManager] ✓ %s updated" % startup_file)
                    return True
                except:
                    continue
        except Exception as e:
            print("[BootManager] Error updating STARTUP files:", str(e))
        
        return False


def main(session, **kwargs):
    session.open(DreamBootManagerScreen)


def Plugins(**kwargs):
    return PluginDescriptor(
        name="Dream Boot Manager",
        description="Multiboot Manager for DreamOS - by ELECTRO YASSINE",
        where=PluginDescriptor.WHERE_PLUGINMENU,
        icon="plugin.png",
        fnc=main
    )
