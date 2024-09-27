🌐 Translate me from French with [Google](https://github-com.translate.goog/alexandrehuat/who-wants-to-be-a-millionaire/tree/main?_x_tr_sl=fr&_x_tr_tl=de&_x_tr_hl=fr&_x_tr_pto=wapp)!

# [UNDER DEV] _Qui veut gagner des millions ?_ personnalisable en Python pour jouer entre amis

Incarnez Jean-Pierre Foucault et invitez vos amis ou collègues à tenter de gagner le million grâce à ce jeu en présentiel ou distanciel !
Ce logiciel est une reconstruction de [_Qui veut gagner des millions ?_](https://youtu.be/67fDyIkcDz4) pour une édition spéciale en entreprise.
Il est développé en Python par Alexandre Huat, Ingénieur Scientifique des Données, sous licence [Creative Commons Attribution – Utilisation Non-Commerciale – Partage dans les Mêmes Conditions (CC BY-NC-SA) 4.0 International](https://creativecommons.org/licenses/by-nc-sa/4.0/?ref=chooser-v1).

## Installation

* Installez [Python 3.12](https://www.python.org/downloads/). 
* Clonez le dépôt et ouvrez un terminal à sa racine.
* Créez un environnement virtuel, activez-le et installez les dépendances. Commandes Shell sous UNIX :
```shell
# Création
python3.12 -m pip install -U pip setuptools wheel venv
mkdir -p ~/.virtualenvs
python3.12 -m venv ~/.virtualenvs/millionaire
# Activation
source ~/.virtualenvs/millionaire/bin/activate
# Installation
python -m pip install -U pip setuptools wheel
pip install -r requirements.txt
```

Activez l'environnement virtuel à l'ouverture de chaque nouvelle session de terminal visant à utiliser le code du dépôt.

## Données de jeu

### Musique

Pour jouer avec les animations sonores, téléchargez une première fois les fichiers sons.
```shell
python -m dl_soundtrack
```

Vous pouvez modifiez les sons utilisés en modifiant le contenu du répertoire `data/sound`.
Pour plus de détails, consultez le script de téléchargement et le fichier `resources/tracklist.tsv`.

### Questions-réponses

Déposez vos questions personnalisées dans le fichier `data/questions.tsv`.
Il contient une question-réponse par ligne. Aucune ligne d'en-tête n'est attendue.
Les colonnes sont interprétées de cette manière (de gauche à droite) :
1. La question
2. La bonne réponse
3. Une 1ère mauvaise réponse
4. Une 2ème mauvaise réponse
5. Une 3ème mauvaise réponse
6. Le niveau de difficulté (nombre), lié aux paliers du jeu :
   * 1 = facile ;
   * 2 = médian ;
   * 3 = difficile.
   * 0 = trivial mais humoristique : bien répondre n'augmente pas les gains et le nombre de questions passés, mais mal répondre fait perdre comme d'habitude ;
7. Si la question peut être utilisée en qualification ou non : cellule non-vide = oui.
8. L'auteur de la question
9. Une note qui permet de comprendre le contexte ou la réponse : affichée uniquement sur TC en jeu.


## Utilisation

### Acteurs
Ce jeu implique plusieurs acteurs humains et informatiques.

**Humains :**
* JP : Jean-Pierre Foucault, l'animateur, incarné par une personne pour toute la partie.
* JM : le(s) joueur(s) qui vont tenter de gagner le million.

**Interfaces locales :** toutes connectées au même ordinateur qui exécute l'application de jeu.
* TC : le terminal central de JP, une interface que seul JP peut consulter et qui permet de tout contrôler.
* EP : l'écran public où l'application diffuse les questions soumises aux JM, les scores, etc.
* HP : la sortie sonore (haut-parleur).

**Interface externe :**
* TR : un terminal de réponse auquel chaque JM a accès indépendamment pour soumettre confidentiellement une réponse à JP. JP doit pouvoir savoir précisément quel JM a soumis avant un autre. Deux cas d'utilisation : question de rapidité (qualification) et joker d'avis du public. Le TR utilise un outil de sondage du type Microsoft Forms pour générer un sondage renouvelable dont les questions sont exactement :
  * « Nom du joueur » dont la réponse est un texte court libre, optionnelle si joker.
  * « Réponse » dont les réponses possibles (boutons radio) sont « A », « B », « C » et « D ».

### Déroulement

* HP et EP lancent le générique de début.
* TC présente une interface où sélectionner :
  * Présentation des candidats :
    * HP lance la musique de présentation des candidats. JP présente les candidats.
  * Qualifications :
    * HP lance la musique d'ouverture de qualification. TC propose une question de rapidité jusqu'à ce que JP
      confirme.
    * EP montre la question de rapidité et ses réponses. HP lance la musique de question de rapidité.
    * JP lit la question. JM ont le temps de la musique pour répondre en secret
      sur [Microsoft Forms](https://forms.office.com/e/hd8j7w2DHJ?origin=lprLink).
    * JP compare les réponses. Le premier bon répondeur gagne. S'il n'y a aucune bonne réponse, une nouvelle
      question de rapidité est proposée.
    * HP lance la musique de victoire rapide. JP annonce le gagnant.
  * Jeu principal :
    * HP lance la musique d'accueil des JM. JP présente les JM.
    * Jusqu'à ce que JM ait répondu à 15 questions ou abandonne :
      * HP lance la musique de question selon le palier. TC montre une question jusqu'à validation de JP.
      * EP montre la question. JP énonce la question.
      * Si JM abandonne :
        * HP lance la musique d'abandon.
        * EP révèle la bonne réponse. JP l'énonce et félicite JM.
      * Sinon :
        * Si JM demande à utiliser un joker : TODO
        * Si le palier 1 est passé :
          * HP lance la musique de dernier mot.
          * JP demande si c'est le dernier mot.
        * EP révèle la bonne réponse. JP l'énonce et félicite JM.
        * Si JM a bien répondu :
          * HP lance la musique de gain du palier.
          * Les gains de JM augmentent.
        * Sinon :
          * HP lance la musique de gain du palier.
          * Les gains de JM tombent au dernier palier.
      * EP affiche les résultats de JM. JP remercie JM.
* HP lance le générique de fin.