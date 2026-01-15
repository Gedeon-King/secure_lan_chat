# 🔐 Analyse de Sécurité - Secure LAN Chat

## 1. Vue d'Ensemble

Ce document présente l'analyse de sécurité complète du système de chat sécurisé pour réseau local (LAN). L'objectif est de démontrer une compréhension approfondie des menaces cryptographiques et de justifier chaque choix de conception.

---

## 2. Modèle de Menace

### 2.1 Hypothèses de Sécurité

**Ce que nous protégeons :**
- ✅ Confidentialité des messages échangés
- ✅ Intégrité des messages (détection de modifications)
- ✅ Authenticité des messages (assurance de l'origine)
- ✅ Forward Secrecy (clés éphémères, pas de compromission du passé)

**Hors périmètre (limitations assumées) :**
- ❌ Déni de service (DoS) volumétrique
- ❌ Compromission physique des machines (keyloggers, RAM freeze)
- ❌ Sécurité de l'OS ou du navigateur
- ❌ Attaques temporelles avancées (timing attacks)

### 2.2 Attaquants Considérés

| Type d'Attaquant | Capacités | Mitigations |
|------------------|-----------|-------------|
| **Passif (Sniffing)** | Capture du trafic réseau | ✅ Chiffrement AES-256-GCM |
| **Actif (MITM)** | Interception et modification | ✅ Fingerprint SAS visuel |
| **Rejeu (Replay)** | Réinjection de paquets anciens | ✅ Nonces uniques (AES-GCM) |
| **Altération** | Modification de messages chiffrés | ✅ Tag d'authentification GCM |

---

## 3. Choix Cryptographiques et Justifications

### 3.1 Échange de Clés : ECDH (Elliptic Curve Diffie-Hellman)

**Algorithme :** ECDH sur courbe SECP384R1  
**Pourquoi ?**
- **Sécurité :** Équivalent à 7680 bits RSA (sécurité à long terme)
- **Efficacité :** Petites clés (96 octets publiques vs 512+ pour RSA)
- **Forward Secrecy :** Clés éphémères générées pour chaque session
  - *Si une clé de session est compromise dans le futur, les sessions passées restent sécurisées.*

**Alternative considérée :** X25519 (Curve25519)
- Plus moderne et rapide, mais SECP384R1 est mieux standardisé (NIST).

### 3.2 Dérivation de Clés : HKDF-SHA256

**Pourquoi HKDF ?**
- **Expansion sécurisée :** Le secret partagé ECDH a une haute entropie mais n'est pas uniformément distribué. HKDF "extrait" et "dérive" une clé cryptographique propre.
- **Contexte binding :** Le paramètre `info` («secure-lan-chat-v1-session») lie la clé à ce protocole spécifique (évite la confusion entre protocoles).

### 3.3 Chiffrement : AES-256-GCM (Galois/Counter Mode)

**AES-256 :** Norme de chiffrement symétrique, sécurité de 256 bits.

**Pourquoi GCM ?**
1. **Chiffrement Authentifié (AEAD) :** GCM fournit à la fois :
   - Confidentialité (chiffrement)
   - Intégrité ET authenticité (tag MAC de 128 bits)
2. **Performance :** Mode parallélisable (rapide sur CPU modernes avec AES-NI)
3. **Nonces uniques :** Utilisation de nonces aléatoires de 12 octets par message.
   - ⚠️ **Critique :** Ne JAMAIS réutiliser un nonce avec la même clé (catastrophique pour GCM).
   - ✅ **Mitigation :** Nonces générés via `os.urandom()` (cryptographiquement sûr).

**Alternative :** ChaCha20-Poly1305
- Excellent choix, mais AES-GCM est mieux supporté matériellement.

---

## 4. Analyse des Attaques et Contre-Mesures

### 4.1 Man-in-the-Middle (MITM)

**Attaque :**  
Un attaquant s'insère entre Alice et Bob lors de l'échange ECDH, intercepte et remplace les clés publiques.

```
Alice  --[PubA]--> Attaquant --[PubAttaquant]--> Bob
Alice <--[PubAttaquant]-- Attaquant <--[PubB]-- Bob
```

Résultat sans protection : Attaquant établit deux canaux séparés et peut lire/modifier tous les messages.

**Contre-mesure : SAS Fingerprint (Short Authentication String)**

1. Après calcul du secret partagé, chaque pair affiche le **hash** de la clé de session (exemple : `8920 B436`).
2. Les utilisateurs **vérifient vocalement** (téléphone, vive voix) que les codes correspondent.
3. Si les codes diffèrent → MITM détecté → fermeture de la connexion.

**Justification :**  
- Simple, sans infrastructure PKI.
- Sécurité repose sur un canal out-of-band (la voix) difficilement interceptable simultanément.
- Méthode utilisée par Signal, Telegram, WhatsApp pour les "Security Codes".

### 4.2 Sniffing Réseau (Écoute Passive)

**Attaque :**  
L'attaquant capture le trafic avec Wireshark/tcpdump.

**Contre-mesure :**  
✅ **Tout le trafic est chiffré avec AES-256-GCM.**  
Sans la clé de session (qui n'est jamais transmise), l'attaquant ne voit que du bruit aléatoire.

**Vérifiable :**  
En inspectant le trafic avec Wireshark, on ne voit que des octets aléatoires (aucun texte clair).

### 4.3 Rejeu de Messages (Replay Attack)

**Attaque :**  
L'attaquant capture un message chiffré M et le renvoie plus tard.

**Contre-mesure :**  
✅ **Nonces uniques dans AES-GCM.**  
Chaque message a un nonce différent (12 octets aléatoires). Même si le message est identique, le ciphertext sera complètement différent.

**Limitation actuelle :**  
Le protocole n'implémente pas de compteur de séquence strict. Un message capturé *pourrait* être rejoué si l'attaquant agit immédiatement.

**Amélioration future :**  
Ajouter un compteur monotone dans les données associées (AAD) ou payload, avec rejet des numéros de séquence dupliqués.

### 4.4 Altération de Messages (Tampering)

**Attaque :**  
L'attaquant modifie 1 bit dans un ciphertext.

**Contre-mesure :**  
✅ **Tag d'authentification GCM (128 bits).**  
Toute modification du ciphertext invalide le tag. Le déchiffrement lève une exception `InvalidTag` et le message est **rejeté**.

**Test inclus :**  
Le test `test_crypto_manager.py` simule une altération et vérifie que le message est rejeté.

### 4.5 Usurpation d'Identité

**Scénario :**  
Un attaquant prétend être Bob.

**Contre-mesure :**  
✅ **Vérification SAS.**  
L'attaquant ne peut pas forger le même fingerprint sans connaître le secret partagé (qui dépend de la clé privée de Bob).

---

## 5. Propriétés de Sécurité Garanties

| Propriété | Garantie | Mécanisme |
|-----------|----------|-----------|
| **Confidentialité** | ✅ Fort | AES-256 (non cassable par attaque exhaustive) |
| **Intégrité** | ✅ Fort | GCM Tag (128 bits) |
| **Authenticité** | ✅ Conditionnel | SAS vérifié manuellement |
| **Forward Secrecy** | ✅ Fort | Clés ECDH éphémères (en mémoire uniquement) |
| **Non-répudiation** | ❌ Aucune | Chiffrement symétrique (les deux pairs partagent la clé) |

---

## 6. Hypothèses de Confiance

1. **Python `secrets` / `os.urandom()` :** Source de nombres aléatoires cryptographiquement sûre.
2. **Bibliothèque `cryptography` :** Implémentation correcte des primitives (audité, largement utilisé).
3. **Canal out-of-band :** Les utilisateurs peuvent communiquer vocalement pour vérifier le SAS (hors portée de l'attaquant réseau).
4. **Pas de malware :** Les machines ne sont pas compromises (pas de keylogger, pas d'accès mémoire).

---

## 7. Améliorations Futures (Optionnelles)

### 7.1 Protection Rejeu Stricte
- Implémenter un compteur de message monotone.
- Rejeter les messages avec des numéros de séquence invalides.

### 7.2 Rotation de Clés
- Ré-exécuter ECDH périodiquement (exemple : toutes les 1000 messages ou 1 heure).
- Améliore le Forward Secrecy à granularité fine.

### 7.3 Authentification Renforcée (PAKE)
- Utiliser un mot de passe partagé avec PAKE (Password-Authenticated Key Exchange).
- Exemple : SPAKE2, Opaque.

### 7.4 Protection des Métadonnées
- Padding des messages à taille fixe (évite l'analyse de trafic).
- Fréquence d'envoi constante (dummy messages).

---

## 8. Conclusion

Le système **Secure LAN Chat** implémente un **protocole cryptographique robuste** adapté à un environnement LAN.

**Points forts :**
- ✅ Confidentialité maximale (AES-256-GCM)
- ✅ Forward Secrecy (ECDH éphémère)
- ✅ Intégrité vérifiable (GCM Tag)
- ✅ Protection MITM pragmatique (SAS)

**Contexte académique :**  
Ce projet démontre une compréhension solide de la cryptographie moderne appliquée, avec des choix justifiés et une architecture claire. Il est prêt pour une démonstration et une défense dans le cadre d'un cursus cybersécurité.

---

**Auteur :** Projet Académique Cybersécurité  
**Date :** Janvier 2026  
**Version :** 1.0
