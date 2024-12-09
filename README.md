# Game Optimization Project

Authored By: Simon Lidwell

--------------

*Table of Contents*

* [Introduction](#introduction)
    * [How to Run This Project](#how-to-run-this-project)
* [Game Optimization Theory](#game-optimization-theory)
* [Project Deliverables](#project-deliverables)
* [Limitations](#limitations)
* [Future Work](#future-work)
* [Conclusion](#conclusion)

## Introduction

I hope this project finds you well Professor Isken (I had to add that in there because I saw your announcement about
unintended consequences of GenAI in tech hiring).

I had a ton of fun putting this together, it has truly been a while since I've worked on some kind of programming
passion project. So I tried my best to put together something respectable. The idea behind this comes from the engineer
within me that needs to know how things are made. Well, in this case, how to win games.

I added in a bit of *personal flare* to this project to try and challenge myself programmatically rather than just turn
in the most basic thing you have ever gotten.

### How to Run This Project

There are two ways you can get this project up and running:

1. **Using the `uv` package manager**

   If you are planning on using `uv`, here is the best way to do that in my opinion:

    ```bash
    uv install
    # if you don't have uv installed then:
    #   pip install pipx
    #   pipx install uv
    #   uv install
    uv run python -m src.main
    ```

2. **Using the `pip` package manager**

   If you prefer to use `pip`, follow these steps (I used Python 3.13):

    ```bash
    python -m venv .venv
    .venv\Scripts\activate

    pip install -r requirements.txt
    python -m src.main
    ```

After getting the backend spun up, you should be able to walk
through [game_optimization_project.ipynb](game_optimization_project.ipynb).

## Game Optimization Theory

### What is Minimax?
The Minimax algorithm is a decision-making algorithm commonly used in two-player, turn-based games like Tic Tac Toe,
Chess, and Checkers. It simulates all possible moves in the game, evaluates the potential outcomes, and chooses the move
that maximizes the AI's chances of winning while minimizing the opponent's chances.

### How it works
* The algorithm recursively explores all possible game states resulting from each move.
* It alternates between maximizing and minimizing at each level of recursion.

### Advantages of Minimax
* **Optimal Play:** Ensures the AI plays optimally, never losing if a win or tie is possible.
* **Simplicity:** Straightforward to implement for simple games like Tic Tac Toe.

## Project Deliverables

**Gameplay**

## Limitations

* **Computationally Intensive:** Not suitable for games with large state spaces without optimizations like Alpha-Beta
  pruning.
* **Assumes Optimal Opponent:** The AI assumes the opponent plays optimally, which may not always be the case in
  real-world scenarios.

## Future Work

Details on possible future improvements.

## Conclusion

Summary of the project and final thoughts.
