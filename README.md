
# pMADI

Markov decision process and reinforcement learning

  

## Introduction

In this project we consider an agent that has to move through a labyrinth, this labyrinth is composed of different tiles which are described in the following table.

  

| Tile name | Tile symbol | Description |
| ---- | ---- | ---- |
| Starting position | ● |  |
| Empty room | (blank) |  |
| Wall | ∎ | Cannot move there |
| enemy | E | the agent kill the enemy with a probability of 0.7 or dies |
| Trap | ▲ | the agent dies (p 0.1), goes back to the starting position (0.3), or nothing happens |
| Crack | C| Immediate death |
| Treasure | T | Can be picked up |
| Sword | † | Can be picked up |
| Key | K | Can be picked up, opens the treasure |
| Portal | ◯ | The agent is teleported in a random room of the labyrinth |
| Moving Platform | - | The agent is moved to one of the adjacent tiles |
  
Example of an instance of the labyrinth :

  

<p align="center">
<img src="https://raw.githubusercontent.com/gualt1995/pMADI/master/labyrinth.png" width="500" title="">
</p>

To complete the labyrinth the agent has to find a key, find the treasure that can be opened by this key and finally go back to its starting position. In addition the agent can also pick up a sword, which allows it to kill enemies instantly.

The goal of this project is to find the optimal policy so that the agent can achieve his objective, to do so we modeled this game as a Markovian decision process where the states are defined as the following (pos_x, pos_y, has_key, has_sword, has_treasure), and the possible actions are to go up, down, left or right. as for the transitions between the states, we calculate this value in function of different tiles where the agent can end up on after a given movement.

The different methods used for the optimisation are the following

-   Value Iteration
    
-   Policy iteration
    
-   Q Learning
    
The descriptions of the algorithms used to implement these can be found in the full report for this project in madi.pdf (french only)


## Usage :

Just run main.py, requires numpy, all the features are available there.


## Original project by :

[Gualtiero Mottola](https://github.com/gualt1995)<br>
[Alexandre Bontems](https://github.com/schonwetter)<br>
