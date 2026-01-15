# 📖 Manuel d'Utilisation - Secure LAN Chat

## 🎯 Introduction

Bienvenue dans **Secure LAN Chat**, une application de messagerie pair-à-pair sécurisée pour réseau local. Ce système utilise une cryptographie de niveau militaire pour protéger vos conversations.

---

## 🔧 Installation

### Prérequis
- Python 3.8 ou supérieur
- Deux ordinateurs sur le même réseau local (LAN)
- Connexion réseau fonctionnelle

### Étapes d'Installation

#### 1. Installation des Dépendances

```powershell
# Installer les dépendances Python
pip install -r requirements.txt
```

Les bibliothèques installées :
- `cryptography` : Primitives cryptographiques (AES, ECDH, HKDF)
- `flask` : Serveur web pour l'interface utilisateur
- `colorama` : Colorisation des logs (optionnel)

#### 2. Vérification de l'Installation

Exécutez les tests pour vérifier que tout fonctionne :

```powershell
# Test de la couche cryptographique
python tests/test_crypto_manager.py

# Test de la couche réseau
python tests/test_network.py

# Test du protocole complet
python tests/test_protocol.py
```

✅ Si tous les tests affichent `[SUCCESS]`, l'installation est correcte.

---

## 🚀 Démarrage Rapide

### Scénario : Alice et Bob veulent communiquer

#### **Sur l'ordinateur d'Alice (Serveur)**

1. **Lancer l'application :**
   ```powershell
   python app.py
   ```

2. **Ouvrir le navigateur :**
   - Aller à : `http://127.0.0.1:5000`

3. **Démarrer en mode Serveur :**
   - Cliquer sur le bouton **"Mode Serveur"**
   - Laisser le port par défaut (`9999`) ou choisir un autre
   - Cliquer sur **"▶️ Démarrer le Serveur"**

4. **Attendre la connexion :**
   - Le statut affichera : *"En attente de connexion..."*

#### **Sur l'ordinateur de Bob (Client)**

1. **Lancer l'application :**
   ```powershell
   python app.py
   ```

2. **Ouvrir le navigateur :**
   - Aller à : `http://127.0.0.1:5000`

3. **Se connecter en mode Client :**
   - Cliquer sur **"Mode Client"**
   - Entrer l'**adresse IP d'Alice** (exemple : `192.168.1.100`)
     - *Pour trouver l'IP d'Alice, elle peut taper `ipconfig` (Windows) ou `ifconfig` (Linux/Mac)*
   - Entrer le **port** (même que celui du serveur, par défaut `9999`)
   - Cliquer sur **"🔗 Se Connecter"**

---

## 🔐 Vérification de Sécurité (CRITIQUE)

### Étape : Vérification du Fingerprint SAS

Après la connexion, **un code de sécurité s'affiche chez Alice ET Bob** dans un encadré vert.

**Exemple :**
```
SAS Fingerprint : 8920 B436
```

#### ⚠️ ACTION OBLIGATOIRE

1. **Alice et Bob se parlent** (téléphone, vive voix, pas par le chat !) :
   - Alice : *"Je vois le code 8920 B436, et toi ?"*
   - Bob : *"Oui, pareil : 8920 B436"*

2. **Si les codes sont identiques :**
   - ✅ **Sécurité confirmée** : Aucun attaquant n'est présent.
   - Vous pouvez chatter en toute sécurité.

3. **Si les codes diffèrent :**
   - ❌ **ATTAQUE DÉTECTÉE (Man-in-the-Middle)**
   - **NE PAS utiliser le chat**
   - Déconnecter immédiatement
   - Vérifier le réseau (routeur compromis ? faux point d'accès ?)

---

## 💬 Utilisation du Chat

### Envoyer un Message

1. Taper le message dans la zone de texte en bas.
2. Appuyer sur **Entrée** ou cliquer sur **"📤 Envoyer"**.
3. Le message apparaît en **bleu** (messages envoyés) à droite.

### Recevoir un Message

- Les messages du pair s'affichent en **gris** à gauche, en temps réel.

### Déconnexion

- Cliquer sur le bouton **"❌ Déconnecter"** en bas.
- L'application revient à l'écran de connexion.

---

## 🛠️ Dépannage

### Problème : "Erreur de connexion"

**Causes possibles :**
- Les deux PC ne sont pas sur le même réseau.
- Le firewall bloque le port.
- L'adresse IP est incorrecte.

**Solutions :**
1. Vérifier que les deux PC sont sur le même Wi-Fi / réseau local.
2. Désactiver temporairement le firewall ou autoriser Python.
3. Vérifier l'IP avec `ipconfig` (Windows) ou `ip a` (Linux).

### Problème : "Pas de session sécurisée"

- Le handshake n'est pas terminé.
- Attendre quelques secondes que le statut passe à **"CANAL SÉCURISÉ ÉTABLI"**.

### Problème : "Échec de l'intégrité du message"

- Le message a été altéré ou corrompu.
- **Cela peut indiquer une attaque !**
- Vérifier le réseau et déconnecter si le problème persiste.

---

## 🔬 Architecture Technique (Résumé)

```
┌─────────────────────────────────────────┐
│    Interface Web (Flask + HTML/CSS)    │
├─────────────────────────────────────────┤
│  Protocole Sécurisé (SecureMessenger)   │
│  - Handshake ECDH                       │
│  - Transport Chiffré AES-GCM            │
├─────────────────────────────────────────┤
│      Couche Crypto (CryptoManager)      │
│  - ECDH (SECP384R1)                     │
│  - HKDF-SHA256                          │
│  - AES-256-GCM                          │
├─────────────────────────────────────────┤
│      Couche Réseau (NetworkManager)     │
│  - Sockets TCP                          │
│  - Framing (Length-Prefixed)            │
└─────────────────────────────────────────┘
```

---

## 📊 Informations Techniques Avancées

### Cryptographie Utilisée

| Composant | Algorithme | Sécurité |
|-----------|------------|----------|
| Échange de clés | ECDH SECP384R1 | ≈ 192 bits |
| Dérivation | HKDF-SHA256 | 256 bits |
| Chiffrement | AES-256-GCM | 256 bits |
| Intégrité | GCM Tag | 128 bits |

### Garanties de Sécurité

- ✅ **Confidentialité** : Aucun message en clair sur le réseau
- ✅ **Intégrité** : Toute modification détectée et rejetée
- ✅ **Authenticité** : Vérification SAS empêche MITM
- ✅ **Forward Secrecy** : Clés éphémères (sessions passées sécurisées même si clé future compromise)

---

## ❓ FAQ

**Q : Puis-je utiliser ce système sur Internet ?**  
R : Non, ce système est conçu pour un réseau local uniquement. Pour Internet, il faudrait ajouter NAT traversal, certificats TLS, etc.

**Q : Les messages sont-ils sauvegardés ?**  
R : Non, tous les messages sont en mémoire uniquement. À la déconnexion, ils sont perdus (design "éphémère").

**Q : Que se passe-t-il si j'oublie de vérifier le SAS ?**  
R : Vous êtes vulnérable à une attaque MITM. **Toujours vérifier le SAS avant de partager des informations sensibles.**

**Q : Peut-on ajouter plus de 2 personnes ?**  
R : La version actuelle supporte uniquement 2 pairs (P2P). Un système multi-utilisateurs nécessiterait un serveur central et une gestion de groupes.

---

## 📞 Support

Pour tout problème ou question académique, consulter :
- `docs/SECURITY_ANALYSIS.md` : Analyse approfondie de la sécurité
- `implementation_plan.md` : Détails techniques de l'architecture

---

**Bon chat sécurisé ! 🔐**
