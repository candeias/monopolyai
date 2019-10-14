# MonopolyAI
A fun approach to build a AI that playes a game of Monopoly.

## Instalation
Clone this git repository to a folder. Make sure you install pipenv.

Open a pipenv shell and do

```bash
pipenv install
pipenv shell
```

## Running a game
You can simply run your first game by doing

```bash
python game.py
```

## Notes and Future
The future of this project is to build an AI that can play Monopoly. To that extend the first steps have been to code a simulation of the Monopoly games that one can then use to train some GANs (Generative Adversarial Networks) to learn how to play. To that extend there will be some functions on the board that will be able to export the player observable variables so that the AI player can make decisions
