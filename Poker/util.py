import collections, random
import poker

# An abstract class representing a Markov Decision Process (MDP).
class MDP:
    # Return the start state.
    def startState(self): raise NotImplementedError("Override me")

    # Return set of actions possible from |state|.
    def actions(self, state): raise NotImplementedError("Override me")

    # Return a list of (newState, prob, reward) tuples corresponding to edges
    # coming out of |state|.
    # Mapping to notation from class:
    #   state = s, action = a, newState = s', prob = T(s, a, s'), reward = Reward(s, a, s')
    # If IsEnd(state), return the empty list.
    def succAndProbReward(self, state, action): raise NotImplementedError("Override me")

    def discount(self): raise NotImplementedError("Override me")

    # Compute set of states reachable from startState.  Helper function for
    # MDPAlgorithms to know which states to compute values and policies for.
    # This function sets |self.states| to be the set of all states.
    def computeStates(self):
        self.states = set()
        queue = []
        self.states.add(self.startState())
        queue.append(self.startState())
        while len(queue) > 0:
            state = queue.pop()
            for action in self.actions(state):
                for newState, prob, reward in self.succAndProbReward(state, action):
                    if newState not in self.states:
                        self.states.add(newState)
                        queue.append(newState)
        # print "%d states" % len(self.states)
        # print self.states

############################################################

# An algorithm that solves an MDP (i.e., computes the optimal
# policy).
class MDPAlgorithm:
    # Set:
    # - self.pi: optimal policy (mapping from state to action)
    # - self.V: values (mapping from state to best values)
    def solve(self, mdp): raise NotImplementedError("Override me")

############################################################

# Abstract class: an RLAlgorithm performs reinforcement learning.  All it needs
# to know is the set of available actions to take.  The simulator (see
# simulate()) will call getAction() to get an action, perform the action, and
# then provide feedback (via incorporateFeedback()) to the RL algorithm, so it can adjust
# its parameters.
class RLAlgorithm:
    # Your algorithm will be asked to produce an action given a state.
    def getAction(self, state): raise NotImplementedError("Override me")

    # We will call this function when simulating an MDP, and you should update
    # parameters.
    # If |state| is a terminal state, this function will be called with (s, a,
    # 0, None). When this function is called, it indicates that taking action
    # |action| in state |state| resulted in reward |reward| and a transition to state
    # |newState|.
    def incorporateFeedback(self, state, action, reward, newState): raise NotImplementedError("Override me")

############################################################

# Perform |numTrials| of the following:
# On each trial, take the MDP |mdp| and an RLAlgorithm |rl| and simulates the
# RL algorithm according to the dynamics of the MDP.
# Each trial will run for at most |maxIterations|.
# Return the list of rewards that we get for each trial.
def simulate(mdp, rl, numTrials=10, maxIterations=1000, verbose=False,
             sort=False):
    # Return i in [0, ..., len(probs)-1] with probability probs[i].
    def sample(probs):
        target = random.random()
        accum = 0
        for i, prob in enumerate(probs):
            accum += prob
            if accum >= target: return i
        raise Exception("Invalid probs: %s" % probs)

    totalRewards = []  # The rewards we get on each trial
    outputProgress = maxIterations / 100
    for trial in range(numTrials):
        if trial%outputProgress == 0:
            print 'Current progress: %d' %trial
        state = mdp.startState()
        #print state
        sequence = [state]
        totalDiscount = 1
        totalReward = 0
        for _ in range(maxIterations):
            action = rl.getAction(state)
            transitions = mdp.succAndProbReward(state, action)
            if sort: transitions = sorted(transitions)
            if len(transitions) == 0:
                rl.incorporateFeedback(state, action, 0, None)
                break

            # Choose a random transition
            i = sample([prob for newState, prob, reward in transitions])
            newState, prob, reward = transitions[i]
            sequence.append(action)
            sequence.append(reward)
            sequence.append(newState)

            rl.incorporateFeedback(state, action, reward, newState)
            totalReward += totalDiscount * reward
            totalDiscount *= mdp.discount()
            state = newState
        if verbose:
            print "Trial %d (totalReward = %s): %s" % (trial, totalReward, sequence)
        totalRewards.append(totalReward)
    return totalRewards

################CONSTANTS###################
MIN_BET = 5
MEDIUM_BET = 10
MAX_BET = 15
############################################
class pokerMDP(MDP):
    def __init__(self, deck, oppType):
        """
        table: instance of Table class
        agent: our player
        opponent: our opponent
        """
        self.table = None
        self.agent = None
        self.opponent = None
        self.deck = deck
        self.oppType = oppType
    # Return the start state.
    # Look at this function to learn about the state representation.
    # The first element of the tuple is the sum of the cards in the player's
    # hand.  The second element is the index of the next card, if the player peeked in the
    # last action.  If they didn't peek, this will be None.  The final element
    # is the current deck.
    # State = (cardsInHand, cardsOnTable, pot, lastAction, IsEnd?)
    # (agent.hand, table.tableCards, table.bettingPot, table.history[-1], IsEnd?)
    def startState(self):
        
        self.deck.reset()
        self.deck.shuffle()
        table = poker.Table(self.deck)
        self.table = table
        opp = poker.Opponent(self.oppType)
        self.opponent = opp
        self.agent = poker.Agent()
        table.dealPlayers(self.agent, self.opponent, self.deck)
        state = (self.agent.hand, [], 0, (None, 0), 0)
        firstAction = opp.determinePolicy(state)
        table.actionHistory.append(firstAction)
        table.incrementOppBet(firstAction[1])
        
        if table.getLastAction() == None:
            return (self.agent.hand, [], 0, (None, 0), 0)
        else :
            return (self.agent.hand, [], table.bettingPot, (None, 0), 1) 
    # Return set of actions possible from |state|.
    def actions(self, state):
        lastAction = self.table.getLastAction()
        if state[4] == 0 or lastAction == None:
            return [('Fold', 0), ('Bet', 0), ('Bet', MIN_BET), ('Bet', MEDIUM_BET), ('Bet', MAX_BET)]
        l = [('Bet', 0), ('Bet', MIN_BET), ('Bet', MEDIUM_BET), ('Bet', MAX_BET)]
        actions = [('Fold', 0)]
        if state[4] == 1:
            if lastAction == ('Bet', 0):
                return l   # if the opponent checks, we should never fold
            for action in l:
                if action[1] >= lastAction[1]:
                    actions.append(action)
            return actions
        if state[4] == 2:
            beforeLastAction = self.table.getActionHistory()[-2]
            diff = lastAction[1] - beforeLastAction[1]
            if diff == 0:
                return [('Bet', 0)]
            else:
                actions.append(('Bet', diff))
                return actions
        if state[4] == 3 or state[4] == 4:
            return [('Bet', 0)]
        
    # Return a list of (newState, prob, reward) tuples corresponding to edges
    # coming out of |state|.  Indicate a terminal state
    # by setting the IsEnd indicator to 4.
    def succAndProbReward(self, state, action):
        ans = []
        history = self.table.getActionHistory()
        if state[4] == 4:
            return []
        if state[3][0] == 'Fold':
            ans.append(((state[0], state[1], state[2], ('Fold', 0), 4), 1, self.table.getOppBet() ))
            self.table.actionHistory.append(state[3])
            self.table.actionHistory.append(action)
            return ans
        if action[0] == 'Fold':
            ans.append(((state[0], state[1], state[2], ('Fold', 0), 4), 1, (-1)*self.table.getAgentBet() ))
            self.table.actionHistory.append(action)
            return ans
        if len(state[1]) == 3 or len(state[1]) == 4 :
            stateForOpp = (state[0], state[1], state[2], action, state[4])
            oppAction = self.opponent.determinePolicy(stateForOpp)
            if state[4] == 2 or state[4] == 3:
                for card in self.deck.cards:
                    s = list(state[1])
                    s.append(card)
                    p = 1.0 / len(self.deck.cards)
                    ans.append(((state[0], s, state[2] + action[1], oppAction, (state[4]+2) % 4), p, 0)) # need to actually draw those cards
                self.deck.draw()
            else:
                ans.append(((state[0], state[1], state[2] + action[1], oppAction, (state[4]+2) % 4), 1, 0))
            self.table.actionHistory.append(oppAction)
            self.table.actionHistory.append(action)
            self.table.incrementOppBet(oppAction[1])
            self.table.incrementAgentBet(action[1])
            return ans

        if len(state[1]) < 3:
            stateForOpp = (state[0], state[1], state[2], action, state[4])
            oppAction = self.opponent.determinePolicy(stateForOpp)
            if state[4] == 2 or state[4] == 3:
                for card1 in self.deck.cards:
                    for card2 in self.deck.cards:
                        if card2 != card1:
                            for card3 in self.deck.cards:
                                if card3 != card2 and card3 != card1:
                                    s = list(state[1])
                                    s.append(card1)
                                    s.append(card2)
                                    s.append(card3)
                                    L = len(self.deck.cards)
                                    p = 1.0 / (L*(L-1)*(L-2))
                                    ans.append(((state[0], s, state[2] + action[1], oppAction, (state[4]+2) % 4), p, 0)) 
                self.deck.draw()
                self.deck.draw()
                self.deck.draw()
            else:
                ans.append(((state[0], state[1], state[2] + action[1], oppAction, (state[4]+2) % 4), 1, 0))
            
            self.table.actionHistory.append(oppAction)
            self.table.actionHistory.append(action)
            self.table.incrementOppBet(oppAction[1])
            self.table.incrementAgentBet(action[1])
            return ans
        if len (state[1]) == 5:
            stateForOpp = (state[0], state[1], state[2], action, state[4])
            oppAction = self.opponent.determinePolicy(stateForOpp)
            if state[4] == 2 or state[4] == 3:
                #print state[1]
                agentVal = self.agent.assessHand(state[1])
                oppVal = self.opponent.assessHand(state[1])
                agentVal = (agentVal[0], sorted(agentVal[1], reverse=True))
                oppVal = (oppVal[0], sorted(oppVal[1], reverse=True))

                if agentVal[0] > oppVal[0]:
                    reward = self.table.getOppBet()
                elif agentVal[0] == oppVal[0]:
                    if (agentVal[1] > oppVal[1]):
                        reward = self.table.getOppBet()
                    else:
                        reward = (-1)*self.table.getAgentBet()
                else:
                    reward = (-1)*self.table.getAgentBet()

                ans.append(((state[0], state[1], state[2] + action[1], action, 4), 1, reward))
            else :
                ans.append(((state[0], state[1], state[2] + action[1], action, (state[4]+2) % 4), 1, 0))

            self.table.actionHistory.append(oppAction)
            self.table.actionHistory.append(action)
            self.table.incrementOppBet(oppAction[1])
            self.table.incrementAgentBet(action[1])
            return ans
        
    def discount(self):
        return 1

############################################################
