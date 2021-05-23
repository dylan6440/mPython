# Space Invaders

## Présentation

Bienvenue sur mon projet MicroPython pour le cours de M.POULAILLEAU Vincent.

Le but de ce projet est de crée un jeux de type Space Invaders sur carte STM32F4-Dicovery.

Avec l'affichage UART de notre carte.

On controle notre vaisseau a l'aide de l'accélérométre de la carte.

On tire des missiles grâce au button de la carte.

Les déplacements des vaisseau ennemis, leur tires, la vélocité et le nombre maximum de nos missiles sont controler par timer.

Il y as plusieur page dans ce jeux, la page principale, la page de jeux (différents niveaux au furs et à mesure qu'on tue les ennemis), la page de victoire et la page de défaite.

Les régles du jeux sont ecrites sur la page principale du jeux.

Decouvrez les différents niveaux

Et Obtenez le meilleurs Score !

## Initialisation du jeux

Pour jouer au jeux, il vous faut faire un premier test avec votre accélérométre pour récuprer la valeur quand votre carte est a plats
