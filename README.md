🌐 _Translate me from French
with [Google](https://github-com.translate.goog/alexandrehuat/who-wants-to-be-a-millionaire/tree/main?_x_tr_sl=fr&_x_tr_tl=de&_x_tr_hl=fr&_x_tr_pto=wapp)!_

# Un _Qui veut gagner des millions ?_ personnalisé en Python pour jouer entre amis

<img src="https://www.programme-tv.net/imgre/fit/http.3A.2F.2Fprd2-bone-image.2Es3-website-eu-west-1.2Eamazonaws.2Ecom.2FTEL.2Enews.2F2018.2F01.2F11.2F2b2ee87e-96a0-4a8a-9644-7b8e02f531a8.2Ejpeg/900x506/quality/70/jean-pierre-foucault-va-a-son-tour-tenter-de-gagner-des-millions.jpg" style="max-height: 360px; border: 1px solid skyblue; border-radius: 1em">

Incarnez Jean-Pierre Foucault et invitez vos amis ou collègues à tenter de devenir millionaire grâce à ce jeu en
présentiel ou distanciel !
Ce programme est une reconstruction de la légendaire émission [_Qui veut gagner des
millions ?_](https://youtu.be/67fDyIkcDz4), développé en Python par Alexandre Huat sous
licence [Creative Commons Attribution – Utilisation Non-Commerciale – Partage dans les Mêmes Conditions (CC BY-NC-SA) 4.0 International](https://creativecommons.org/licenses/by-nc-sa/4.0/?ref=chooser-v1).

Lisez ce fichier pour installer et utiliser ce jeu correctement.

⚠️ _Ce programme utilise l'interface native Tkinter testée sous [macOS Sequoia](https://www.apple.com/fr/macos/macos-sequoia/).
Sa portabilité graphique n'est pas garantie._

## Installation

1. Installez [Python 3.12](https://www.python.org/downloads/).
2. Clonez le dépôt et ouvrez un terminal à sa racine.
3. Créez un environnement virtuel.
4. Activez-le.
5. Installez les dépendances.

Commandes Shell sous UNIX :
```shell
# 3. Création d'un environnement virtuel
python3.12 -m pip install -U pip setuptools wheel venv
mkdir -p ~/.virtualenvs
python3.12 -m venv ~/.virtualenvs/millionaire
# 4. Activation de l'environnement
source ~/.virtualenvs/millionaire/bin/activate
# 5. Installation des dépendances
python -m pip install -U pip setuptools wheel
pip install -r requirements.txt
```

## Données de jeu

Installez ces données avant de lancer le jeu.

### Musique

Pour jouer avec les animations sonores, téléchargez une première fois les fichiers sons.

1. Installez [YT-DLP](https://github.com/yt-dlp/yt-dlp).
2. Installez [FFmpeg](https://www.ffmpeg.org/).
3. Depuis la racine du dépôt, exécutez le script de téléchargement `download_soundtrack`. Commandes Shell sous UNIX :
```shell
python -m download_soundtrack
```

Vous pouvez aussi procéder manuellement et utiliser vos sons en modifiant directement le répertoire `data/sound`.
Pour plus de détails, consultez le script de téléchargement et le fichier `resources/tracklist.tsv`.

### Questions

Ce jeu ne fournit que quelques questions en guise de test dans le fichier `data/questions.tsv`.
Pour jouer, remplissez ce fichier avec vos propres questions.
C'est un _Qui veut gagner des millions ?_ personnalisé !

#### Format

Le fichier est au format TSV (colonnes séparées par des tabulations, texte long entre double-quote « " »).

Entrez du texte encodé en UTF-8 pour un bon affichage des caractères alphabétiques en jeu.

#### Structure

Indiquez une question par ligne.
N'entrez aucune ligne d'en-tête.

En colonne, indiquez de gauche à droite :

1. La question
2. La bonne réponse
3. Une 1ère mauvaise réponse
4. Une 2ème mauvaise réponse
5. Une 3ème mauvaise réponse
6. Le niveau de difficulté (un nombre), lié aux paliers du jeu :
  * 0 : trivial (et humoristique), sans incidence sur les gains ;
  * 1 : facile ;
  * 2 : médian ;
  * 3 : difficile ;
  * 4 : extrême, pour la phase de qualifications.

Les colonnes suivantes sont optionnelles :
8. L'auteur de la question
9. Une note : pour comprendre le contexte ou la réponse.
10. La date de dernière publication de la question

## Utilisation

⚠️ _Lisez toute cette section pour bien préparer le jeu avant lancement._

Le jeu possède trois interfaces :
* le **terminal d'animation**, qui permet à l'animateur de contrôler le jeu ;
* l'**écran public**, à montrer aux joueurs sur un second écran ou en partage d'écran en visioconférence ;
* une **interface sonore**, gérée en arrière-plan. Montez le son !

Pour quitter le jeu, utilisez de préférence le bouton <kbd>Quitter</kbd> du terminal d'animation.

### Qualification

La phase de qualification permet de choisir et lancer une question de rapidité.

En cliquant une première fois sur <kbd>Publier</kbd>, la question est soumise aux joueurs et lue par l'animateur.

En cliquant une seconde fois, toutes les réponses possibles sont montrées aux joueurs.
Les joueurs les lisent en silence et font leur choix le plus vite possible.
Un système à main levé ou avec une application de sondage en ligne est possible.

Le joueur le plus rapide à fournir la bonne réponse gagne !
Il est qualifié pour une nouvelle partie.

### Nouvelle partie

C'est le mode de jeu principal.
L'animateur accompagne un ou deux joueurs (un principal et un accompagnant) le plus loin possible vers le million.
Seul le joueur principal voit ses réponses et actions enregistrées par l'animateur.
L'accompagnant n'est là que pour l'aider à réfléchir.

Sur le terminal d'animation, l'animateur peut choisir la question qui sera véritablement affichée (bouton <kbd>Changer</kbd>) avant de la publier sur l'écran public.
Une fois décidé, il doit cliquer plusieurs fois sur le bouton <kbd>Publier</kbd>, pour publier la question et chaque réponse qu'il énonce l'une après l'autre. ⏱️ Un minuteur est lancé dès la publication de la question. À sa fin, le joueur doit faire un choix.

Si le joueur répond juste, l'animateur clique sur le bouton <kbd>Suivant</kbd> et le processus recommence.
L'animateur peut aussi forcer le numéro de question en le sélectionnant directement sur le terminal d'animation.

Le joueur peut aussi abandonner (bouton <kbd>Abandonner</kbd>) plutôt que de prendre le risque de mal répondre.

#### Pyramide des gains

Le numéro de question détermine la difficulté de la question, de facile à difficile selon que l'on est avant le premier palier, après le premier palier, ou après le second.
Les questions triviales peuvent être posées à n'importe quel moment.

Plusieurs pyramides de gains sont codées :
* **15 :** 15 questions avec les paliers à la 5ème et la 10ème question.
* **12 classique :** 12 questions avec les paliers à la 2ème et la 7ème question.
* **12 équilibrée :** 12 questions avec les paliers à la 4ème et la 8ème question.

Une défaite à une question ramène les gains au dernier palier passé (0 si aucun).
Un abandon conserve les gains acquis.

#### Jokers

Les trois jokers classiques du jeu sont disponibles dès le début de la partie.
Un joker additionnel est débloqué au hasard à chaque palier.

Quand le joueur principal demande d'utiliser un joker, l'animateur peut l'activer par le terminal d'animation.
En cas d'erreur, cliquer sur un joker désactivé le rend disponible de nouveau.

##### 50:50

Ce joker désactive deux mauvaises réponses au hasard.

##### Appel à un ami

Avant de lancer la partie, le joueur principal doit pré-selectionner les amis qu'il pourra solliciter.

⏱️ Cliquer sur le bouton de ce joker déclenche un minuteur de 30 secondes.
L'animateur ne doit donc l'activer qu'au moment où l'ami est prêt à entendre la question du joueur.
Le joueur principal doit en effet reposer la question et les réponses possibles à son ami avant que celui-ci ne réponde, même si l'ami est dans la salle de jeu et a déjà entendu la question par l'animateur.

##### Vote du public

Chaque membre du public assez sûr de lui vote pour exactement une réponse possible.
De préférence, le vote est anonyme par une tierce plateforme en ligne, ou un système de cartes.
Sinon un vote à main levé est réalisé.
Le nombre de votes par réponse est ensuite révélé aux joueurs.

##### Changement

Ce joker permet de changer de question.
L'animateur doit rechoisir une question et la publier.

##### Avis de l'animateur

L'animateur donne son avis librement aux joueurs, sans temps imparti.

##### Avis d'expert

Les membres du public très sûrs d'eux se lèvent.
Le joueur principal choisit un de ces experts auto-déclarés.
L'expert choisi expose son avis librement, sans temps imparti.

#### Jeu libre

🚫 _Cette fonctionnalité n'est pas encore développée._

Le principe de ce mode de jeu est de faire participer le plus grand nombre.
L'animateur anime comme il le souhaite.
Toutes les questions existantes sont soumises au public aléatoirement, sans pré-selection par l'animateur.
Le nombre de fois où les joueurs ont bien ou mal répondus est affiché au fil du jeu.
Tous les jokers sont disponibles, activables et réactivables à volonté.

## Lancement

1. Placez-vous à la racine du dépôt.
2. Activez l'environnement virtuel Python du jeu (voir [Installation](#installation)).
2. Exécutez le module `millionaire`.
Commandes Shell sous UNIX :
```shell
python -m millionaire
```

### Configuration

L'animateur peut configurer la langue, la pyramide des gains, la durée des différents minuteurs, etc.

Pour le moment, certaines configurations ne peut être gérée qu'en éditant directement le code du module [`millionaire.game`](millionaire/game.py),
notamment les valeurs par défaut du constructeur de la classe `Game`.