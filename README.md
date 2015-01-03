Poker
=====

An implementation of a poker AI agent. This project was submitted as a final project for CS 221: Artificial Intelligence:
Principles and Techniques at Stanford University. 

This is an AI agent that plays Texas Hold'em. The game is cast as a Markov Decission Process (MDP) and I use QLearning
together with Monte Carlo simulations and epsilon-greedy algorithm to train the agent. 
First, the bot learns by playing against fixed policy opponents (tight-aggressive, loose-aggressive, tight-passive, 
loose-passive and random opponents). Then it can play against itself or a human user. 
