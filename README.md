# Space Invaders

## Présentation

Bienvenue sur mon projet MicroPython pour le cours de M.POULAILLEAU Vincent.

Le but de ce projet est de crée un jeux de type Space Invaders sur carte STM32F4-Dicovery.

Avec l'affichage UART de notre carte.

On contrôle notre vaisseau à l'aide de l'accéléromètre de la carte.

On tire des missiles grâce au bouton de la carte.

Les déplacements des vaisseau ennemis, leur tires, la vélocité et le nombre maximum de nos missiles sont contrôler par timer.

Il y a plusieurs pages dans ce jeux, la page principale, la page de jeux (différents niveaux au furs et à mesure qu'on tue les ennemis), la page de victoire et la page de défaite.

Les règles du jeux sont écrites sur la page principale du jeux avant de commencer.

Découvrez les différents niveaux.

Et Obtenez le meilleurs Score !

## Initialisation du jeux

Tous d'abord pour pouvoir flasher la carte STM32 et écrire du code python, vous pouvez suivre le pdf micropython_installation.pdf de M.POULAILLEAU Vincent ou toutes les informations sont détaillé.

Pour jouer au jeux, il vous faut faire un premier test avec votre accéléromètre pour récupérer la valeur quand votre carte est à plats.

Le code valeur_accel.py va vous permettre de récupérer ces valeur.

![code](https://user-images.githubusercontent.com/70941138/119276882-cda23d00-bc1c-11eb-9bfe-0a36a14cf1f9.PNG)

il vous suffit de changer les adresse de lecture X et Y de votre accéléromètre si elles sont différentes de celle marqué.

Ayant une STM32 version B mon accéléromètre est LIS302DL avec comme adresse pour X : 0x29 et Y : 0x2B

Copié l'intégralité du code valeur_accel.py (avec les adresse changer si besoin), brancher votre carte en UART et ouvrez la fenêtre d'échange pour afficher le résultat en UART.

![code2](https://user-images.githubusercontent.com/70941138/119277274-f7f4fa00-bc1e-11eb-9d58-07cd5e212fcf.PNG)

Une fois les valeurs récupérer, rentrer ces valeur dans le code main.py dans les variable balanced_x et balanced_y.

N'oublié pas de changer les adresse de lecture dans ce code aussi si vous les aviez changés dans le code précédent

Une fois les variables modifié, remplacer le fichier code main.py que vous avez modifié a la place du fichier main.py de la carte.

Vous pouvez maintenant jouer à ce jeux avec l'affichage en UART !


## Récapitulatif du projet

Les plus grandes difficulté rencontré dans la création de ce jeux sont:
  - Le manque d'inspiration a certain moment
  - Le choix aléatoire des ennemies qui tire
  - La création des différentes page du jeux (Home, Niveau de jeux, page Victoire, page Défaite)

Mais chaque problèmes as des solutions:
  - Prendre une pause, un bon café, un bon bol d'air frais et c'est reparti
  - Recherche sur internet l'utilisation du module random avec la fonction choise
  - Du temps (même s’il est rare), de la patiente et de la persévérance
  
Mais je me suis aussi amélioré sur:
  - La création et utilisation de Classe
  - Définition de fonction
  - Utilisation de boucle for / while et des interruption de boucles avec les break
  
Pour finir, ce projet ma énormément appris en créativité pour toujours essayer de me dépasser, faire des recherche sur chaque problème / erreurs rencontré, mais c'est un projet que nous avons fait tous le long du programme pour apprendre a manipulé chaque notions apprise durant les cours qui permet de manipuler plus facilement et de voir un projet grandir à petit pas.

C'est pour cela que je remercie notre intervenant M.POULAILLEAU Vincent pour les notions qui nous as appris, sont intérêt au python et ça façons d'enseigné qui rends les cours dynamique


## SPOILS VIDEO DU JEUX !!!

https://user-images.githubusercontent.com/70941138/119910768-255fe180-bf58-11eb-8339-7c0f8040aa8c.mp4
