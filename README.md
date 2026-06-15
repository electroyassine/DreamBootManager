# 🌙 Dream Boot Manager

**Plugin de gestion multiboot avancé pour récepteurs DreamOS (Dreambox ONE & TWO)**

*Développé par [ELECTRO YASSINE](https://github.com/electroyassine)*

---

## 📖 Description

**Dream Boot Manager** est un plugin Enigma2 écrit en Python qui offre une interface graphique intuitive pour gérer le démarrage multiboot sur les récepteurs Dreambox fonctionnant sous DreamOS. Il permet de sélectionner, supprimer et gérer plusieurs images système installées sur les partitions internes eMMC ou sur une carte SD externe.

---

## ✨ Fonctionnalités

| Fonction | Description |
|---|---|
| 🔄 **Multiboot Selector** | Sélectionner l'image de démarrage par défaut parmi les images disponibles |
| 🗑️ **Multiboot Deletion** | Supprimer une image installée dans un slot tout en conservant la partition |
| 🔧 **Flash Recovery Image** | Accès rapide au Flash Manager ou Software Manager intégré |
| 💾 **Backup Recovery Image** | Accès à l'écran de sauvegarde d'image système |
| 💳 **SD Card Partition** | Partitionner automatiquement une carte SD pour le multiboot |

---

## 🖥️ Compatibilité

- **Récepteurs** : Dreambox ONE, Dreambox TWO (et compatibles DreamOS)
- **Système** : DreamOS (basé sur Enigma2)
- **Langage** : Python 3
- **Partitions supportées** :
  - Interne (eMMC) : Slots 1 à 4 — `/dev/mmcblk0p5` à `/dev/mmcblk0p8`
  - Carte SD : Slots 5 à 8 — `/dev/mmcblk1p2` à `/dev/mmcblk1p5`

---

## 📁 Structure du projet

```
DreamBootManager/
├── plugin.py        # Code principal du plugin (écrans, logique de boot)
├── __init__.py      # Fichier d'initialisation du module Python
├── install.sh       # Script d'installation automatique
├── plugin.png       # Icône du plugin (affichée dans le menu Enigma2)
└── README.md        # Documentation
```

---

## ⚙️ Installation

### Méthode 1 — Script automatique (recommandée)

Connectez-vous en SSH à votre récepteur et exécutez :

```bash
wget -O - https://raw.githubusercontent.com/electroyassine/DreamBootManager/main/install.sh | sh
```

### Méthode 2 — Installation manuelle

1. Clonez ou téléchargez le dépôt :
   ```bash
   git clone https://github.com/electroyassine/DreamBootManager.git
   ```
2. Copiez le dossier dans le répertoire des plugins Enigma2 :
   ```bash
   cp -r DreamBootManager /usr/lib/enigma2/python/Plugins/Extensions/DreamBootManager
   ```
3. Redémarrez l'interface graphique :
   ```bash
   killall -9 enigma2
   ```

---

## 🚀 Utilisation

### Accès au plugin

Allez dans **Menu → Plugins → Dream Boot Manager**.

---

### 1. 🔄 Multiboot Selector

Affiche la liste des images boot disponibles lues depuis `/data/bootconfig.txt`.  
Sélectionnez une image et confirmez : le fichier `bootconfig.txt` sera mis à jour (`default=N`) et le fichier `STARTUP` sera réécrit. Un redémarrage est proposé pour appliquer le changement.

---

### 2. 🗑️ Multiboot Deletion

Liste tous les slots multiboot détectés (internes et SD card).  
Pour chaque slot, le plugin monte la partition et lit `/etc/issue` pour afficher le nom de l'image installée.  
La suppression formate entièrement la partition EXT4 (`mkfs.ext4`) tout en la conservant intacte pour une future utilisation.

---

### 3. 🔧 Flash Recovery Image

Tente d'ouvrir dans l'ordre :
- `FlashManager` (natif DreamOS)
- `SoftwareManager` (plugin système)

---

### 4. 💾 Backup Recovery Image

Tente d'ouvrir dans l'ordre :
- `BackupScreen`
- `ImageBackup`
- `SoftwareManager > BackupRestore`

---

### 5. 💳 SD Card Partition

Partitionne automatiquement la carte SD (`/dev/mmcblk1`) avec le schéma suivant :

| Partition | Nom | Format | Taille | Usage |
|---|---|---|---|---|
| `/dev/mmcblk1p1` | DREAMCARD | FAT32 | Espace restant | Stockage fichiers / kernels |
| `/dev/mmcblk1p2` | dreambox-rootfs | EXT4 | ~1,7 Go | Slot 5 |
| `/dev/mmcblk1p3` | dreambox-rootfs | EXT4 | ~1,7 Go | Slot 6 |
| `/dev/mmcblk1p4` | dreambox-rootfs | EXT4 | ~1,7 Go | Slot 7 |
| `/dev/mmcblk1p5` | dreambox-rootfs | EXT4 | ~1,7 Go | Slot 8 |

> ⚠️ **Attention** : Cette opération efface toutes les données présentes sur la carte SD.

Après le partitionnement, les fichiers `STARTUP_1` à `STARTUP_8` sont créés dans `/data/` et le fichier `bootconfig.txt` est vérifié/régénéré automatiquement.

---

## 📝 Fichiers système gérés

### `/data/bootconfig.txt`

Fichier de configuration U-Boot qui liste les images démarrables. Créé automatiquement s'il est absent.

Exemple de structure :
```ini
default=0
timeout=10

[Dreambox Image]
cmd=ext4load mmc 1:5 1080000 /boot/kernel.img;bootm;
arg=${bootargs} root=/dev/mmcblk0p5 rootfstype=ext4 ...

[SDcard Slot 5]
cmd=fatload mmc 0:1 1080000 /kernel2.img;bootm;
arg=${bootargs} root=/dev/mmcblk1p2 rootfstype=ext4 ...
```

### Fichiers `STARTUP_N`

Créés dans `/data/`, ils définissent les paramètres de démarrage pour chaque slot :

```
STARTUP_1 → root=/dev/mmcblk0p5 rootfstype=ext4 kernel=/boot/kernel.img
STARTUP_5 → root=/dev/mmcblk1p2 rootfstype=ext4 kernel=/kernel2.img
...
```

---

## 🔐 Prérequis

- Accès root au récepteur (via SSH ou FTP)
- DreamOS / Enigma2 installé
- Pour la fonction SD Card : carte SD insérée dans le récepteur

---

## 📜 Licence

Ce projet est distribué librement. Toute contribution ou amélioration est la bienvenue via Pull Request.

---

## 👤 Auteur

**ELECTRO YASSINE**  
GitHub : [@electroyassine](https://github.com/electroyassine)

---

## 🤝 Contribution

1. Forkez le dépôt
2. Créez une branche : `git checkout -b feature/ma-fonctionnalite`
3. Commitez vos changements : `git commit -m "Ajout de ma fonctionnalité"`
4. Poussez la branche : `git push origin feature/ma-fonctionnalite`
5. Ouvrez une Pull Request

---

*Dream Boot Manager — Gérez votre multiboot Dreambox simplement et efficacement.*
