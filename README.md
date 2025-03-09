# Sentinel v3.0

## Table de contenus
- [Description](#description)
- [Fonctionnalités](#fonctionnalités)
- [Installation](#installation)
- [Usage](#usage)
- [Contributions](#contributions)
- [Tests (optionnel)](#tests-optionnel)
- [Licence](#licence)

**Description**  
Sentinel v3.0 est un projet de monitoring et de keylogging éducatif. Il inclut une interface PyQt5 moderne, un module de chiffrement via Fernet (cryptography), et un enregistrement des frappes dans des logs chiffrés.

> **Avertissement** : ce logiciel doit être utilisé **uniquement** dans un cadre légal (tests sur vos propres machines ou celles pour lesquelles vous avez une autorisation explicite). L’auteur décline toute responsabilité en cas d’utilisation abusive ou illégale.

## Fonctionnalités

- Keylogger basé sur [pynput](https://pypi.org/project/pynput/).  
- Interface [PyQt5](https://pypi.org/project/PyQt5/) avec 4 thèmes intégrés (Dark, Light, Blue, Green).  
- Chiffrement et déchiffrement via [Fernet](https://pypi.org/project/cryptography/) (module `cryptography`).  
- Export et suppression des logs.  
- Recherche en temps réel dans les logs chiffrés/déchiffrés.

## Installation

1. **Cloner le dépôt** :
   ```bash
   git clone https://github.com/votre-nom-utilisateur/sentinel-v3.git
   cd sentinel-v3
   
2. **Créer et activer un environnement virtuel (optionnel mais recommandé)** :

    ```bash
    python -m venv .venv
    source .venv/bin/activate   # Sur Linux/Mac
    .venv\Scripts\activate 
   
3. **Installer les dépendances** :
    ```bash
   pip install -r requirements.txt

4. **Lancer l’application** :
   ```bash
   python main.py

## Usage
- Au lancement, l’interface s’ouvre automatiquement.
- Le keylogger démarre (ou non) selon vos paramètres (par défaut, il est actif).
- Vous pouvez mettre en pause, exporter, effacer, etc. via l’interface.
- Les logs sont enregistrés (chiffrés) dans un dossier caché dans votre home (~/.securetype par défaut).
- Les clés de chiffrement sont gérées automatiquement (création si besoin).

## Contributions
Les contributions sont les bienvenues !
Pour proposer une fonctionnalité ou reporter un bug, merci de créer une issue ou de soumettre une pull request.

### Tests (optionnel)
Vous pouvez ajouter des tests unitaires dans un dossier tests/ et les exécuter via :
   ```bash
      pytest
   ```
(Si vous mettez en place pytest ou autre framework de test.)

## Licence

Ce projet est distribué sous licence MIT.
Voir le fichier LICENSE pour plus d’informations.
---
`LICENSE` (MIT)

<details>
<summary>Fichier de licence MIT</summary>

```text
MIT License

Copyright (c) 2025 Angrevier

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the “Software”), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
```
</details>
