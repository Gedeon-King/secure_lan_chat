# 🚀 Guide de Démarrage Rapide

## Installation Express (2 minutes)

### 1️⃣ Installer les dépendances
```powershell
pip install -r requirements.txt
```

### 2️⃣ Lancer l'application (sur les 2 PC)
```powershell
python app.py
```

### 3️⃣ Ouvrir le navigateur
```
http://127.0.0.1:5000
```

---

## Configuration Typique

### PC 1 - Serveur
1. Mode Serveur
2. Port : 9999
3. ▶️ Démarrer

### PC 2 - Client
1. Mode Client
2. IP : [IP du PC 1]  
   *Trouver l'IP : `ipconfig` sur Windows*
3. Port : 9999
4. 🔗 Se Connecter

---

## ⚠️ ÉTAPE CRITIQUE : Vérification SAS

**Après connexion, COMPARER VOCALEMENT le code affiché :**

```
Fingerprint : XXXX XXXX
```

✅ **Identique** → Sécurisé  
❌ **Différent** → ATTAQUE MITM → Déconnecter

---

## 💬 Chat Sécurisé

Tous les messages sont automatiquement **chiffrés avec AES-256-GCM**.  
Profitez de votre conversation 100% privée ! 🔒

---

## 📚 Documentation Complète

- **[README.md](README.md)** : Vue d'ensemble
- **[docs/USER_MANUAL.md](docs/USER_MANUAL.md)** : Guide complet
- **[docs/SECURITY_ANALYSIS.md](docs/SECURITY_ANALYSIS.md)** : Analyse sécurité

---

**🔐 Sécurité. Simplicité. Aucun compromis.**
