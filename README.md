# 🔐 Secure LAN Chat

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Cryptography](https://img.shields.io/badge/Crypto-AES--256--GCM-green.svg)](https://cryptography.io/)
[![License](https://img.shields.io/badge/License-Academic-orange.svg)](LICENSE)

> **Application de Chat Sécurisé Pair-à-Pair pour Réseau Local**  
> Projet Académique de Cybersécurité - Cryptographie Appliquée

## 🎯 Présentation

**Secure LAN Chat** est une application de messagerie instantanée chiffrée de bout en bout (E2E), conçue pour démontrer l'implémentation pratique de primitives cryptographiques modernes dans un contexte réseau.

### Caractéristiques Principales

- 🔐 **Chiffrement E2E** : AES-256-GCM (Authenticated Encryption)
- 🔑 **Échange de Clés Sécurisé** : ECDH sur courbe elliptique SECP384R1
- 🧬 **Dérivation de Clés** : HKDF-SHA256
- ✅ **Protection MITM** : Fingerprint SAS (Short Authentication String)
- 🚀 **Interface Moderne** : Application web avec design dark-mode premium
- ⚡ **Temps Réel** : Mise à jour instantanée via Server-Sent Events (SSE)

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────┐
│         Interface Web (Flask + SSE)          │
│         templates/ + static/                 │
└──────────────────┬───────────────────────────┘
                   │
┌──────────────────▼───────────────────────────┐
│      Protocole Sécurisé (SecureMessenger)    │
│      src/protocol/secure_protocol.py         │
│  • Handshake ECDH                            │
│  • State Machine (IDLE → HANDSHAKING → SECURE)│
│  • Message Routing                           │
└──────────┬───────────────────┬───────────────┘
           │                   │
┌──────────▼──────────┐ ┌──────▼──────────────┐
│  Couche Crypto      │ │  Couche Réseau      │
│  CryptoManager      │ │  NetworkManager     │
│  • ECDH KeyGen      │ │  • TCP Sockets      │
│  • HKDF Derivation  │ │  • Length Framing   │
│  • AES-GCM Enc/Dec  │ │  • Threaded RX      │
└─────────────────────┘ └─────────────────────┘
```

---

## 🚀 Installation & Utilisation

### 1. Prérequis

- Python 3.8+
- Deux ordinateurs sur le même réseau local

### 2. Installation

```powershell
# Cloner le projet (ou extraire l'archive)
cd secure_lan_chat

# Installer les dépendances
pip install -r requirements.txt
```

### 3. Lancer l'Application

**Sur les DEUX ordinateurs :**

```powershell
python app.py
```

Puis ouvrir dans le navigateur : `http://127.0.0.1:5000`

### 4. Configuration de la Connexion

#### **Ordinateur 1 (Serveur)** :
1. Choisir "Mode Serveur"
2. Démarrer sur le port 9999 (par défaut)
3. Noter votre adresse IP locale (`ipconfig` sur Windows)

#### **Ordinateur 2 (Client)** :
1. Choisir "Mode Client"
2. Entrer l'IP du serveur (ex: `192.168.1.100`)
3. Se connecter

### 5. ⚠️ Vérification Sécurité (CRITIQUE)

Après connexion, un **code SAS** s'affiche chez les deux utilisateurs :

```
Fingerprint : 8920 B436
```

**OBLIGATION :** Vérifier vocalement (téléphone/vive voix) que les codes sont identiques.
- ✅ Codes identiques → Connexion sécurisée
- ❌ Codes différents → **ATTAQUE MITM** → Déconnecter

### 6. Chatter

Les messages sont automatiquement chiffrés avec AES-256-GCM. Profitez d'une conversation 100% confidentielle ! 🔒

---

## 📁 Structure du Projet

```
secure_lan_chat/
│
├── app.py                      # Serveur Flask (point d'entrée)
├── requirements.txt            # Dépendances Python
│
├── src/
│   ├── crypto/
│   │   └── crypto_manager.py  # Gestion ECDH + AES-GCM + HKDF
│   ├── network/
│   │   └── network_layer.py   # Sockets TCP + Framing
│   └── protocol/
│       └── secure_protocol.py # Orchestration Handshake + Transport
│
├── templates/
│   └── index.html             # Interface utilisateur
│
├── static/
│   ├── style.css              # Design dark-mode premium
│   └── app.js                 # Logique client (SSE)
│
├── tests/
│   ├── test_crypto_manager.py # Test crypto primitives
│   ├── test_network.py        # Test couche réseau
│   └── test_protocol.py       # Test protocole complet
│
└── docs/
    ├── SECURITY_ANALYSIS.md   # Analyse de sécurité détaillée
    └── USER_MANUAL.md         # Manuel utilisateur complet
```

---

## 🔒 Sécurité

### Garanties Cryptographiques

| Propriété | Algorithme | Niveau de Sécurité |
|-----------|------------|-------------------|
| **Confidentialité** | AES-256-GCM | 256 bits (incassable) |
| **Intégrité** | GCM Tag (128 bits) | Détection garantie |
| **Échange de Clés** | ECDH SECP384R1 | ≈ 192 bits (≈ 7680 bits RSA) |
| **Forward Secrecy** | Clés éphémères | ✅ Sessions passées protégées |
| **Protection MITM** | SAS Fingerprint | ✅ Vérification manuelle |

### Menaces Couvertes

- ✅ **Sniffing réseau** (Wireshark) → Tout est chiffré
- ✅ **MITM** → SAS Fingerprint
- ✅ **Altération de messages** → Tag GCM invalide le message
- ✅ **Rejeu partiel** → Nonces uniques (GCM)

**Pour l'analyse complète :** Voir [`docs/SECURITY_ANALYSIS.md`](docs/SECURITY_ANALYSIS.md)

---

## 🧪 Tests

Le projet inclut des tests unitaires pour chaque couche :

```powershell
# Test de la couche cryptographique
python tests/test_crypto_manager.py

# Test de la couche réseau
python tests/test_network.py

# Test du protocole sécurisé complet
python tests/test_protocol.py
```

---

## 🎓 Contexte Académique

Ce projet a été développé dans le cadre d'un cursus de **Cybersécurité** avec pour objectifs :

1. **Implémenter** (pas juste utiliser) des primitives cryptographiques
2. **Comprendre** les attaques réseau (MITM, Replay, Tampering)
3. **Justifier** chaque choix technique et cryptographique
4. **Documenter** l'analyse de sécurité et les menaces
5. **Démontrer** une architecture logicielle propre (séparation des couches)

---

## 📚 Documentation

- **[Guide Explicatif Illustré](docs/GUIDE_EXPLICATIF.md)** : Diagrammes et explications pédagogiques
- **[Guide de Démonstration](docs/DEMO_GUIDE.md)** : Scénario pour présentation académique
- **[Manuel Utilisateur](docs/USER_MANUAL.md)** : Guide complet d'installation et d'utilisation
- **[Analyse de Sécurité](docs/SECURITY_ANALYSIS.md)** : Modèle de menace, cryptographie, justifications
- **[Plan d'Implémentation](../brain/.../implementation_plan.md)** : Architecture détaillée

---

## 🛠️ Technologies Utilisées

- **Python 3.8+** : Langage principal
- **Flask** : Framework web
- **cryptography** : Bibliothèque cryptographique (PyCA)
- **HTML5/CSS3/JavaScript** : Interface utilisateur moderne
- **Server-Sent Events (SSE)** : Mise à jour temps réel

---

## ⚠️ Limitations & Améliorations Futures

### Limitations Actuelles
- ❌ Support de 2 utilisateurs uniquement (P2P)
- ❌ Pas de persistance des messages (mémoire volatile)
- ❌ Réseau local uniquement (pas de NAT traversal)

### Améliorations Possibles
- ➕ Protection rejeu stricte (compteur de séquence)
- ➕ Rotation de clés automatique
- ➕ Support multi-utilisateurs (serveur central)
- ➕ Authentification renforcée (PAKE)
- ➕ Protection des métadonnées (padding, timing)

---

## 👨‍💻 Auteur

**Projet Académique Cybersécurité**  
Développé avec ❤️ et 🔐  
Janvier 2026

---

## 📜 Licence

Ce projet est développé à des **fins académiques et pédagogiques** uniquement.

---

## 🙏 Remerciements

- **PyCA Cryptography** : Primitives cryptographiques robustes
- **Flask Team** : Framework web élégant
- **NIST** : Standardisation des courbes elliptiques

---

**🔐 Chat Sécurisé. Communication Privée. Zéro Compromis.**
