import collections, util, math, random, operator, poker

############################################################

# Performs Q-learning.  Read util.RLAlgorithm for more information.
# actions: a function that takes a state and returns a list of actions.
# discount: a number between 0 and 1, which determines the discount factor
# featureExtractor: a function that takes a state and action and returns a list of (feature name, feature value) pairs.
# explorationProb: the epsilon value indicating how frequently the policy
# returns a random action

class QLearningAlgorithm(util.RLAlgorithm):
    def __init__(self, actions, discount, featureExtractor, explorationProb=0.2):
        self.actions = actions
        self.discount = discount
        self.featureExtractor = featureExtractor
        self.explorationProb = explorationProb
        self.weights = collections.Counter()
        self.numIters = 0

    # Return the Q function associated with the weights and features
    def getQ(self, state, action):
        score = 0
        for f, v in self.featureExtractor(state, action):
            score += self.weights[f] * v
        return score

    # This algorithm will produce an action given a state.
    # Here we use the epsilon-greedy algorithm: with probability
    # |explorationProb|, take a random action.
    def getAction(self, state):
        self.numIters += 1
        if random.random() < self.explorationProb:
            return random.choice(self.actions(state))
        else:
            return max((self.getQ(state, action), action) for action in self.actions(state))[1]

    # Call this function to get the step size to update the weights.
    def getStepSize(self):
        return 1.0 / math.sqrt(self.numIters)

    # We will call this function with (s, a, r, s'), which you should use to update |weights|.
    # Note that if s is a terminal state, then s' will be None.  Remember to check for this.
    # You should update the weights using self.getStepSize(); use
    # self.getQ() to compute the current estimate of the parameters.
    
    def incorporateFeedback(self, state, action, reward, newState):
        if newState == None:
            x = 0
        else:
            x = max(self.getQ(newState, a) for a in self.actions(newState))
        r = reward + x*self.discount - self.getQ(state, action)
        for feature in self.featureExtractor(state, action):
            if feature[0] in self.weights.keys():
                self.weights[feature[0]] += self.getStepSize()*r*feature[1]
            else:
                self.weights[feature[0]] = self.getStepSize()*r*feature[1]


# Feature extractor
def pokerFeatureExtractor(state, action):
    handCards, tableCards, pot, oppAction, isEnd = state
    featureVector =[]
    featureValue = 1.0

    agent = poker.Agent()
    agent.hand = handCards
    
    combinedCards = handCards + tableCards
    combinedCards.sort()
    handCards.sort()
    tableCards.sort()

    handRanks = []
    tableRanks = []
    for i in range(len(handCards)):
      handRanks.append(handCards[i][0])
    for i in range(len(tableCards)):
      tableRanks.append(tableCards[i][0])
    hearts = 0
    spades = 0
    diamonds = 0
    clubs = 0
    for i in range(len(combinedCards)):
      if combinedCards[i][1] == "Hearts":
        hearts += 1
      elif combinedCards[i][1] == "Spades":
        spades += 1
      elif combinedCards[i][1] == "Diamonds":
        diamonds += 1 
      elif combinedCards[i][1] == "Clubs":
        clubs += 1 

    #feature: pot value
    featureVector.append((('pot', pot, action), featureValue))
    #feature: hand+table cards
    #featureVector.append((('c', tuple(combinedCards), action), featureValue))
    #feature: hand ranks
    featureVector.append((('h', tuple(handRanks), action), featureValue))
    #feature: table ranks
    featureVector.append((('t', tuple(tableRanks), action), featureValue))
    #feature: number of suits
    if hearts >= 3:
      featureVector.append((("Hearts", hearts, action), featureValue))
    if spades >= 3:
      featureVector.append((("Spades", spades, action), featureValue))
    if diamonds >= 3:
      featureVector.append((("Diamonds", diamonds, action), featureValue))
    if clubs >= 3:
      featureVector.append((("Clubs", clubs, action), featureValue))
    #feature: what you have in hand indicator
    if len(tableCards) != 0:
        v = agent.assessHand(tableCards)[0]
        if v >= 180:
          v = 180
        elif v >= 160:
          v = 160
        elif v >= 140:
          v = 140
        elif v >= 120:
          v = 120
        elif v >= 100:
          v = 100
        elif v >= 80:
          v = 80
        elif v >= 60:
          v = 60
        elif v >= 40:
          v = 40
        elif v >= 20:
          v = 20
        else:
          v = 0
        featureVector.append((('value', v, action),featureValue))
    #feature: indicator for every card ?
    #for card in handCards+tableCards:
    #    featureVector.append((card, featureValue))
    #feature: Opponent action and phase - Ben
    featureVector.append((('oppAct', oppAction, isEnd, action), featureValue))
    
    return featureVector


def testQL():
  deck = poker.Deck()
  deck.shuffle()
  mdp = None
  QL = None
  human = False
  oppType = None
  humanActions = []

    #function to load weight from file.
    #Text in file should be of the format {(feature1): value1, (feature2):value2}
  def loadWeight(fileName):
      with open(fileName,'r') as inf:
          dict_from_file = eval(inf.read())
      return collections.Counter(dict_from_file)


  userInput = raw_input('Type S to simulate QLearning, hit Enter otherwise: ')
  if(userInput == 'S' or userInput == 's'):
    
    print 'What type of opponent would you like to simulate?'
    print '0. Tight-Aggressive'
    print '1. Loose-Aggressive'
    print '2. Tight-Passive'
    print '3. Loose-Passive'
    print '4. Random'
    
    userInput = int(raw_input('Opponent Type: '))
    oppType = ''
    if userInput == 0:
      oppType = 'TAG'
    elif userInput == 1:
      oppType = 'LAG'
    elif userInput == 2:
      oppType = 'TPA'
    elif userInput == 3:
      oppType = 'LPA'
    elif userInput == 4:
      oppType = 'RANDOM'
    
    print 'How many Q-Learning trials do you wish to run?'
    print 'WARNING: We strongly recommend using 1000 trials or less'
    print 'In our experience, 1000 gets done in about 10 minutes most cases'
    print 'Anything over that can take hours'
    
    userTrial = int(raw_input('Number of trials: '))
    print 'How many tests do you want to run on the generated weight vector?'
    numIter = int(raw_input('Number of tests: '))
    mdp = util.pokerMDP(deck, oppType)
    QL= QLearningAlgorithm(mdp.actions, mdp.discount(), pokerFeatureExtractor, 0.2)
    
    print util.simulate(mdp, QL, numTrials=userTrial, maxIterations=10000)
    print QL.weights
    print 'Weight length: %d' %len(QL.weights)
  else:
    human = True
    print 'What type of opponent weight-vector do you wish to start with?'
    print '0. Tight-Aggressive'
    print '1. Loose-Aggressive'
    print '2. Tight-Passive'
    print '3. Loose-Passive'
    print '4. Random'
    
    userInput = int(raw_input('Opponent Type: '))
    oppType = ''
    if userInput == 0:
      
      oppType = 'TAG'
      mdp = util.pokerMDP(deck, oppType)
      QL= QLearningAlgorithm(mdp.actions, mdp.discount(), pokerFeatureExtractor, 0.2)
      QL.weights = loadWeight('w_tag_5k.txt')
    
    elif userInput == 1:
      
      oppType = 'LAG'
      mdp = util.pokerMDP(deck, oppType)
      QL= QLearningAlgorithm(mdp.actions, mdp.discount(), pokerFeatureExtractor, 0.2)
      QL.weights = loadWeight('w_lag_5k.txt')
    
    elif userInput == 2:
      
      oppType = 'TPA'
      mdp = util.pokerMDP(deck, oppType)
      QL= QLearningAlgorithm(mdp.actions, mdp.discount(), pokerFeatureExtractor, 0.2)
      QL.weights = loadWeight('w_tpa_5k.txt')
    
    elif userInput == 3:
      
      oppType = 'LPA'
      mdp = util.pokerMDP(deck, oppType)
      QL= QLearningAlgorithm(mdp.actions, mdp.discount(), pokerFeatureExtractor, 0.2)
      QL.weights = loadWeight('w_lpa_5k.txt')
    
    elif userInput == 4:
      
      oppType = 'RANDOM'
      mdp = util.pokerMDP(deck, oppType)
      QL= QLearningAlgorithm(mdp.actions, mdp.discount(), pokerFeatureExtractor, 0.2)
      QL.weights = loadWeight('w_random_5k.txt')
    
    print 'How many games do you wish to play?'
    print 'Choose more than 10 to enable opponent recognition'
    
    numIter = int(raw_input())
      
    

  def opponentRecognition(l):
    # Assume opponent plays 10 games
    # Features: total money bet, number of folds, number of checks, number of raises
    
    totalBet = 0
    folds = 0
    checks = 0
    raises = 0
    for action in l:
      if action[0] == 'Fold':
        folds += 1
      elif action[1] == 0:
        checks += 1 
      else :
        raises += 1
      totalBet += action[1]
    betPerRaise = (1.0*totalBet)/raises
    if folds > 2:
      # tight
      if betPerRaise > 6 or 3*raises > checks:
        return 'TAG'
      else :
        return 'TPA'
    else :
      # loose
      if betPerRaise > 6 or 3*raises > checks:
        return 'LAG'
      else :
        return 'LPA'
  
  def playGame(QL, deck, table, agent, opp, human):

      def oppPlay(i,agentAction):
          oppState = (agent.hand, table.tableCards, table.bettingPot, agentAction, i)
          if not human:
              oppAction = opp.determinePolicy(oppState)
              table.incrementOppBet(oppAction[1])
              table.appendAction(oppAction)
              return oppAction
          else:
              actions = mdp.actions(oppState)
              index = input('Type action index:' + str(actions))
              print 'Your Action: ' + str(actions[index])
              table.incrementOppBet(actions[index][1])
              table.appendAction(actions[index])
              humanActions.append(actions[index])
              return actions[index]
      
      def agentPlay(i, oppAction):
          agentState = (agent.hand, table.tableCards, table.bettingPot, oppAction, i)
          agentAction = QL.getAction(agentState)
          table.incrementAgentBet(agentAction[1])
          table.appendAction(agentAction)
          if human:
            print 'Agent Action: ' + str(agentAction)
          return agentAction

      def determineFullGameWinner(deck, table, agent, opp):
        cardsNeeded = 5 - len(table.tableCards)
        if cardsNeeded > 0:
          for i in range(cardsNeeded):
            table.flipCard(deck)

          agentVal = agent.assessHand(table.tableCards)
          oppVal = opp.assessHand(table.tableCards)

          agentVal = (agentVal[0], sorted(agentVal[1], reverse=True))
          oppVal = (oppVal[0], sorted(oppVal[1], reverse=True))
    
          if agentVal[0] > oppVal[0]:
            return "Agent"
          elif agentVal[0] == oppVal[0]:
            if agentVal[1] > oppVal[1]:
              return "Agent"
            elif agentVal[1] < oppVal[1]:
              return "Opp"
            return "Tie"
            return 0
          return "Opp"

      # shuffle deck
      deck.shuffle()
      # deal players
      #table.dealPlayers(agent,opp,deck)
      if human:
        print'Your cards are:' + str(opp.hand)

      oppAction = oppPlay(0, (None,0))
                        
      if oppAction[0] == 'Fold':
          agentUtility = table.getOppBet()
          return ('OppLeft', agentUtility)

      agentAction = agentPlay(1,oppAction)                     
      if agentAction[0] == 'Fold':
          if human:
            print 'Agent\'s hand revealed: ' + str(agent.hand)
            print 'You win: %d' %table.bettingPot
          agentUtility = -(table.getAgentBet())
          couldHaveWon = determineFullGameWinner(deck, table, agent, opp)
          if couldHaveWon == "Agent" or couldHaveWon == "Tie":
            return ('GoodFold', agentUtility)
          return ('BadFold', agentUtility)

      # in case agent raises
      if agentAction[1] > oppAction[1]:

          oppAction = oppPlay(2, agentAction)
          if oppAction[0] == 'Fold':
            agentUtility = table.getOppBet()
            return ('OppLeft', agentUtility)

          agentAction = agentPlay(3, oppAction)
          if agentAction[0] == 'Fold':
            if human:
              print 'Agent\'s hand revealed: ' + str(agent.hand)
              print 'You win: %d' %table.bettingPot
            agentUtility = -(table.getAgentBet())
            couldHaveWon = determineFullGameWinner(deck, table, agent, opp)
            if couldHaveWon == "Agent" or couldHaveWon == "Tie":
              return ('GoodFold', agentUtility)
            return ('BadFold', agentUtility)
    
      # deal table - flop
      table.flipCard(deck)
      table.flipCard(deck)
      table.flipCard(deck)

      if human:
          print 'Flop: ' + str(table.tableCards)
          print 'Your cards: ' + str(opp.hand)
          print 'Pot: ' + str(table.bettingPot)
                        
      # asses hand
      oppAction = oppPlay(0, (None,0))
      if oppAction[0] == 'Fold':
          agentUtility = table.getOppBet()
          return ('OppLeft', agentUtility)

      agentAction = agentPlay(1,oppAction)
      if agentAction[0] == 'Fold':
          if human:
              print 'Agent\'s hand revealed: ' + str(agent.hand)
              print 'You win: %d' %table.bettingPot
          agentUtility = -(table.getAgentBet())
          couldHaveWon = determineFullGameWinner(deck, table, agent, opp)
          if couldHaveWon == "Agent" or couldHaveWon == "Tie":
            return ('GoodFold', agentUtility)
          return ('BadFold', agentUtility)

      # in case agent raises
      if agentAction[1] > oppAction[1]:

          oppAction = oppPlay(2, agentAction)
          if oppAction[0] == 'Fold':
            agentUtility = table.getOppBet()
            return ('OppLeft', agentUtility)

          agentAction = agentPlay(3, oppAction)
          if agentAction[0] == 'Fold':
            if human:
              print 'Agent\'s hand revealed: ' + str(agent.hand)
              print 'You win: %d' %table.bettingPot
            agentUtility = -(table.getAgentBet())
            couldHaveWon = determineFullGameWinner(deck, table, agent, opp)
            if couldHaveWon == "Agent" or couldHaveWon == "Tie":
              return ('GoodFold', agentUtility)
            return ('BadFold', agentUtility)
    
      # deal table - turn
      table.flipCard(deck)

      if human:
          print 'Turn: ' + str(table.tableCards)
          print 'Your cards: ' + str(opp.hand)
          print 'Pot: ' + str(table.bettingPot)
                        
      # asses hand
      oppAction = oppPlay(0, (None,0))
      if oppAction[0] == 'Fold':
          agentUtility = table.getOppBet()
          return ('OppLeft', agentUtility)

      agentAction = agentPlay(1,oppAction)
      if agentAction[0] == 'Fold':
          if human:
              print 'Agent\'s hand revealed: ' + str(agent.hand)
              print 'You win: %d' %table.bettingPot
          agentUtility = -(table.getAgentBet())
          couldHaveWon = determineFullGameWinner(deck, table, agent, opp)
          if couldHaveWon == "Agent" or couldHaveWon == "Tie":
            return ('GoodFold', agentUtility)
          return ('BadFold', agentUtility)

      # in case agent raises
      if agentAction[1] > oppAction[1]:

          oppAction = oppPlay(2, agentAction)
          if oppAction[0] == 'Fold':
            agentUtility = table.getOppBet()
            return ('OppLeft', agentUtility)

          agentAction = agentPlay(3, oppAction)
          if agentAction[0] == 'Fold':
            if human:
              print 'Agent\'s hand revealed: ' + str(agent.hand)
              print 'You win: %d' %table.bettingPot
            agentUtility = -(table.getAgentBet())
            couldHaveWon = determineFullGameWinner(deck, table, agent, opp)
            if couldHaveWon == "Agent" or couldHaveWon == "Tie":
              return ('GoodFold', agentUtility)
            return ('BadFold', agentUtility)

      # deal table - river
      table.flipCard(deck)
      if human:
          print 'River: ' + str(table.tableCards)
          print 'Your cards: ' + str(opp.hand)
          print 'Pot: ' + str(table.bettingPot)
                        
      # asses hand
      oppAction = oppPlay(0, (None,0))
      if oppAction[0] == 'Fold':
          agentUtility = table.getOppBet()
          return ('OppLeft', agentUtility)

      agentAction = agentPlay(1,oppAction)
      if agentAction[0] == 'Fold':
          if human:
              print 'Agent\'s hand revealed: ' + str(agent.hand)
              print 'You win: %d' %table.bettingPot
          agentUtility = -(table.getAgentBet())
          couldHaveWon = determineFullGameWinner(deck, table, agent, opp)
          if couldHaveWon == "Agent" or couldHaveWon == "Tie":
            return ('GoodFold', agentUtility)
          return ('BadFold', agentUtility)

      # in case agent raises
      if agentAction[1] > oppAction[1]:

          oppAction = oppPlay(2, agentAction)
          if oppAction[0] == 'Fold':
            agentUtility = table.getOppBet()
            return ('OppLeft', agentUtility)

          agentAction = agentPlay(3, oppAction)
          if agentAction[0] == 'Fold':
            if human:
              print 'Agent\'s hand revealed: ' + str(agent.hand)
              print 'You win: %d' %table.bettingPot
            agentUtility = -(table.getAgentBet())
            couldHaveWon = determineFullGameWinner(deck, table, agent, opp)
            if couldHaveWon == "Agent" or couldHaveWon == "Tie":
              return ('GoodFold', agentUtility)
            return ('BadFold', agentUtility)

      agentVal = agent.assessHand(table.tableCards)
      oppVal = opp.assessHand(table.tableCards)

      agentVal = (agentVal[0], sorted(agentVal[1], reverse=True))
      oppVal = (oppVal[0], sorted(oppVal[1], reverse=True))

      if human:
        print 'Agent\'s hand revealed: ' + str(agent.hand)
                        
      if agentVal[0] > oppVal[0]:
        if human:
          print 'You lose ' + str(table.bettingPot)
        return ('Win', table.getOppBet())
      elif agentVal[0] == oppVal[0]:
          if agentVal[1] > oppVal[1]:
            if human:
              print 'You lose ' + str(table.bettingPot)
            return ('Win', table.getOppBet())
          elif agentVal[1] < oppVal[1]:
              if human:
                  print 'You win ' + str(table.bettingPot)
              return ('Lose', -(table.getAgentBet()))
          return ('Win', 0) #Count ties as a win for simplicity
      if human:
          print 'You win ' + str(table.bettingPot)
      return ('Lose', -(table.getAgentBet()))


  agent = poker.Agent()
  opp = poker.Opponent(oppType)
  table = poker.Table(mdp.deck)
  stateHistory = {}
  utilityHistory = {}
  QL.explorationProb = 0 #No more exploration
  humanMultigameHistory = []
  
  for gameNum in range(numIter):
    mdp.startState()
    if human:
      mdp.table.bettingPot = 0 #Make sure starting pot is zero
    result = playGame(QL, mdp.deck, mdp.table, mdp.agent, mdp.opponent, human)
    state, utility = result[0], result[1]
    if state in stateHistory:
      stateHistory[state] += 1
    else:
      stateHistory[state] = 1
    if utility in utilityHistory:
      utilityHistory[utility] += 1
    else:
      utilityHistory[utility] = 1
    if human:
      humanMultigameHistory.append(humanActions)
      if len(humanMultigameHistory) > 10:
        humanMultigameHistory = humanMultigameHistory[1:]
      if len(humanMultigameHistory) == 10:
        humanActs = []
        for i in range(len(humanMultigameHistory)):
          for j in range(len(humanMultigameHistory[i])):
            humanActs.append(humanMultigameHistory[i][j])
        newOppType = opponentRecognition(humanActs)
        if newOppType != oppType:
          print 'You\'re playing more like a %s player' %newOppType
          print 'Loading %s weight vector' %newOppType
          oppType = newOppType
          mdp = util.pokerMDP(deck, oppType)
          QL= QLearningAlgorithm(mdp.actions, mdp.discount(), pokerFeatureExtractor, 0.2)
          if newOppType == 'TAG':
            QL.weights = loadWeight('w_tag_5k.txt')
          elif newOppType == 'LAG':
            QL.weights = loadWeight('w_lag_5k.txt')
          elif newOppType == 'TPA':
            QL.weights = loadWeight('w_tpa_5k.txt')
          else: #'LPA'
            QL.weights = loadWeight('w_lpa_5k.txt')
    deck.reset()
    agent = poker.Agent() #Easy way to reset agent, opp, table
    opp = poker.Opponent(oppType)
    table = poker.Table(mdp.deck)
  return stateHistory, utilityHistory


states, utilities = testQL()
print 'Agent Summary'
print states
print utilities
summate = 0
for key in utilities.keys():
    summate += key*utilities[key]
print summate

'''
deck = poker.Deck()
deck.shuffle()
mdp = util.pokerMDP(deck)

QL= QLearningAlgorithm(mdp.actions, mdp.discount(), pokerFeatureExtractor, 0.2)
print util.simulate(mdp, QL, numTrials=1000, maxIterations=10000)

# q.explorationProb = 0
# counter = 0
# for state in largeMDP.states:
#     if q.getAction(state) != pi[state] and state[2] != None:
#         # print state
#         # print q.getAction(state)
#         # print pi[state]
#         # print
#         counter += 1
# print counter
# vi2 = ValueIteration()
# vi2.solve(largeMDP)
# print len(largeMDP.states)
'''
