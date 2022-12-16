# Self-Organizing Multi-Agent Systems Coursework 2022-2023

### Overview

This folder contains all the code and documentation for Team 7's (Inigo's) SOMAS coursework submission. It's a model of the "Escape the Pitt" game, trained on and participated in by a DDPG neural network intelligent agent.

To go to the game logic, see [game.py](./source/game/game). For details about the DDPG neural network, see [ddpg_peasant.py](./source/game/actors/ddpg_peasant.py). 

## Installation

Install Python 3.10

```bash
> sudo apt-get install python
```

Create a virtual environment

```bash
> python3 -m venv .enviroment
```

Activate that environment

```bash
> . .environment/bin/activate
```

Install dependencies

```bash
> pip3 install -r requirements.txt
```

## Running the game

What to the files do?

- [main.py](./source/main.py) runs an instance of the game with the trained network agent
- [train.py](./source/train.py) trains a neural network under given conditions, and saves the weights model

#### How do I run them?

Run the game

```bash
> python3 source/main.py 
```

Train a network with randomly acting team members

```bash
> python3 source/train.py random
```

Note that training will invoke TensorFlow, and will take a few seconds to begin printing results. At least, it does on my laptop.

Test its performance

```bash
> python3 source/profile.py random
```

