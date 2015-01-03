import collections, math, random, itertools, operator

##########################################
#
##########################################

class Deck(object):
    """docstring for Deck"""
    testDeckSize = 6 #Deck of cards 2 - 6
    fullDeckSize = 14 #Deck of cards 2 - 14, 14 being an Ace

    def __init__(self, ranksize = fullDeckSize):
        suits = ["Hearts", "Spades", "Diamonds", "Clubs"]
        self.cards = [(x, y) for x in range(2, ranksize + 1) for y in suits] #First is value, second is suit
        self.cardCount = 4*ranksize

    def shuffle(self):
        random.shuffle(self.cards)

    def reset(self, ranksize = fullDeckSize):
        suits = ["Hearts", "Spades", "Diamonds", "Clubs"]
        self.cards = [(x, y) for x in range(2, ranksize + 1) for y in suits] #First is value, second is suit
        self.cardCount = 4*ranksize

    def draw(self):
        self.cardCount -= 1
        return self.cards.pop(0)

class Table(object):
    
    def __init__(self, deck):
        self.pairReward = 20
        self.twoPairsReward = 40
        self.threeOfAKindReward = 60
        self.straightReward = 80
        self.flushReward = 100
        self.fullHouseReward = 120
        self.fourOfAKindReward = 140
        self.straightFlushReward = 160
        self.royalFlushReward = 180
        self.tableCards = []
        self.bettingPot = 0
        self.agentBet = 0 #T
        self.oppBet = 0 #T
        self.actionHistory = [] #T
        self.deck = deck #C

    def incrementPot(self, newBet):
        self.bettingPot += newBet

    def getAgentBet(self): #T
        return self.agentBet

    def incrementAgentBet(self, bet): #T
        self.agentBet += bet
        self.incrementPot(bet)

    def getOppBet(self): #T
        return self.oppBet

    def incrementOppBet(self, bet): #T
        self.oppBet += bet
        self.incrementPot(bet)
        
    def getLastAction(self): #T
        if len(self.actionHistory) == 0:
            return None
        return self.actionHistory[-1]

    def getActionHistory(self): #T
        return self.actionHistory

    def appendAction(self, action): #T
        self.actionHistory.append(action)
        
    def flipCard(self, deck):
        self.tableCards.append(deck.draw())

    def dealPlayers(self, player1, player2, deck):
        player1.receiveCard(deck.draw()) #Alternate deals to players
        player2.receiveCard(deck.draw())
        player1.receiveCard(deck.draw())
        player2.receiveCard(deck.draw())

    def playGame(self):
        return

    def determineValue(self, cards):
        if len(cards) > 5:
            raise Exception('Need 5 cards not %s' %(len(cards)))
        cards.sort()
        cards.reverse() #Put high card first
 
        def straight(cards):
          if len(cards) != 5:
            return (False, 0)
              
          rank = cards[0][0] #Rank of first card
          #see if this is an Ace card; handle this one differently
          if rank == 14 and cards[4][0] != 1:
            aceLow = (1, cards[0][1]) #Not normally a valid card; used to model a low ace
            aceLowCards = cards[1:]
            aceLowCards.append(aceLow)
            aceLowCards.sort()
            aceLowCards.reverse()
            if straight(aceLowCards)[0]: return (True, aceLowCards[0])
          #print cards
          for i in range(1, 5):
          #  print cards[i-1], cards[i]
            if (rank - 1) != cards[i][0]: return (False, 0)
            else: rank -= 1
          #print 'pass'
          return (True, cards[0])

        def flush(cards):
          if len(cards) != 5:
            return (False, 0)
              
          suit = cards[0][1]
          for card in cards:
            if card[1] != suit:
              return (False, 0)
          return (True, max(cards))
                  
          
        def fourOfAKind(cards):
          if len(cards) < 4:
            return (False, 0)
          counter = 0
          for x in range(0, 2):
            for card in cards:
              if cards[x][0] == card[0]:
                counter +=1
            if counter == 4:
              return (True, cards[x])
            counter = 0
          return (False, 0)
          
        def threeOfAKind(cards):
          if len(cards) < 3:
            return (False, 0)
          counter = 0
          for x in range(0,3):
            for card in cards:
              if cards[x][0] == card[0]:
                counter +=1
            if counter == 3:
              return (True, cards[x])
            counter = 0
          return (False, 0)
                
        def pair(cards):
          if len(cards) < 2:
            return (False, 0)
          counter = 0
          for x in range(0, len(cards)-1):
            for card in cards:
              if cards[x][0] == card[0]:
                counter +=1
            if counter == 2:
              return (True, cards[x])
            counter = 0
          return (False, 0)
          
        #Royal Flush
        def royalFlush(cards):
          return (flush(cards)[0] and straight(cards)[0] and max(cards)[0]==14, max(cards))
        #Straight Flush
        def straightFlush(cards):
          return (flush(cards)[0] and straight(cards)[0], max(cards))
        #4 of a kind 
        #Full House
        def fullHouse(cards):
          if threeOfAKind(cards[0:3])[0] and pair(cards[3:])[0]:
            return (True, threeOfAKind(cards[0:3])[1])
          
          if pair(cards[0:2])[0] and threeOfAKind(cards[2:])[0]:
            return (True, threeOfAKind(cards[2:])[1])
          
          return (False,0)
          
        #Flush
        #Straight
        #Three of a kind
        #Two Pair
        def twoPairs(cards):
          return ((pair(cards[0:3])[0] and pair(cards[3:])[0]) or (pair(cards[0:2])[0] and pair(cards[2:])[0]), max(cards))
        #One Pair
        #High Card

        result = royalFlush(cards)
        if result[0]: return self.royalFlushReward + result[1][0]
        result = straightFlush(cards)
        if result[0]: return self.straightFlushReward + result[1][0]
        result = fourOfAKind(cards)
        if result[0]: return self.fourOfAKindReward + result[1][0]
        result = fullHouse(cards)
        if result[0]: return self.fullHouseReward + result[1][0]
        result = flush(cards)
        if result[0]: return self.flushReward + result[1][0]
        result = straight(cards)
        if result[0]: return self.straightReward + result[1][0]
        result = threeOfAKind(cards)
        if result[0]: return self.threeOfAKindReward + result[1][0]
        result = twoPairs(cards)
        if result[0]: return self.twoPairsReward + result[1][0]
        result = pair(cards)
        if result[0]: return self.pairReward + result[1][0]
        else: return cards[0][0]
        
class Agent(object):
    def __init__(self):
        self.hand = []
        self.cash = 100

    def receiveCard(self, tuple):
        self.hand.append(tuple)

    def assessHand(self, tableCards):
        bestHand = []

        # pre-flop
        if len(tableCards)==0:
            bestHand = self.hand
            #print '2 from hand, 0 from table'
            return (t.determineValue(bestHand), bestHand)

        # at flop
        if len(tableCards)==3:
            bestHand = self.hand + tableCards
            #print '2 from hand, 3 from table'
            return (t.determineValue(bestHand), bestHand)

        # at turn (4th card)
        if len(tableCards)==4:
            combValues = []
            for i in xrange(1,len(self.hand)+1):
                #print '%s from hand, %s from table' %(i, 5-i)
                for handCombination in itertools.combinations(self.hand, i):
                    for tableCombination in itertools.combinations(tableCards, len(tableCards)-i+1):
                        #print tableCombination
                        bestHand = list(handCombination) + list(tableCombination)
                        #print bestHand
                        combValues.append((t.determineValue(bestHand), bestHand))
            #print combValues
            # sort list by value and get all the hands resulting in an equivalent max value
            combValues = sorted(combValues, reverse=True)
            result = [combi for combi in combValues if combi[0] == combValues[0][0]]
            # sort list by best hand
            result = sorted(result, key= lambda var: var[1], reverse=True)
            return result[0]

        #at river
        if len(tableCards)==5:
            combValues = []
          # taking into account player hand
            for i in xrange(1,len(self.hand)+1):
                #print '%s from hand, %s from table' %(i, 5-i)
                for handCombination in itertools.combinations(self.hand, i):
                    for tableCombination in itertools.combinations(tableCards, len(tableCards)-i): 
                        #print tableCombination
                        bestHand = list(handCombination) + list(tableCombination)
                        #print bestHand
                        combValues.append((t.determineValue(bestHand), bestHand))
          # only looking at table cards
            #print '0 from hand, 5 from table'
            bestHand = tableCards
            #print bestHand
            combValues.append((t.determineValue(bestHand), bestHand))
            # sort list by value and get all the hands resulting in an equivalent max value
            # print [item[0] for item in combValues]
            combValues = sorted(combValues, reverse=True)
            # print [item[0] for item in combValues]
            result = [combi for combi in combValues if combi[0] == combValues[0][0]]
            # sort list by best hand
            result = sorted(result, key= lambda var: var[1], reverse=True)
            #print result
            # return first item in sorted list: one with the best 
            return result[0]

class Opponent(object):
    def __init__(self, opponentType):
        self.hand = []
        self.opponentType = opponentType
        self.roundBet = 0
        self.betExploreProb = 0.2
        if opponentType == 'TAG': #Will rarely play, and often bet
          self.bettingFrequency = 0.8
          self.initialFoldProb = [0, 0, 0, 0, 0.05, 0.1, 0.15, 0.2]
          self.initialHandBets = [15, 10, 5, 5, 5, 0, 0, 0] #Cash willing to initally bet
          self.maxInitialBet = [15, 15, 10, 10, 5, 5, 5, 5] #Cash willing to max bet
          self.gameFoldProb = [0.2, 0.1, 0.05, 0, 0, 0, 0, 0, 0, 0] #Probability of folding given a hand
          self.gameBets = [0, 0, 0, 5, 5, 10, 15, 15, 15, 15] #Nothing, pair, 2P, 3K, straight, flush, fullHouse, 4K, straight flush, royal flush
          self.maxGameBets = [0, 5, 5, 10, 10, 15, 15, 15, 15, 15]
        elif opponentType == 'LAG': #Will always play, and often bet
          self.bettingFrequency = 0.8
          self.initialFoldProb = [0, 0, 0, 0, 0, 0, 0, 0]
          self.initialHandBets = [15, 10, 5, 5, 5, 0, 0, 0] #Cash willing to initally bet
          self.maxInitialBet = [15, 15, 10, 5, 5, 0, 0, 0] #Percentage of initial cash willing to max bet
          self.gameFoldProb = [0.05, 0.01, 0, 0, 0, 0, 0, 0, 0, 0]
          self.gameBets = [0, 0, 0, 5, 5, 10, 15, 15, 15, 15] #Nothing, pair, 2P, 3K, straight, flush, fullHouse, 4K, straight flush, royal flush
          self.maxGameBets = [0, 0, 5, 10, 10, 15, 15, 15, 15, 15]
        elif opponentType == 'TPA': #Will rarely play, and rarely bet
          self.bettingFrequency = 0.1
          self.maxRank = 7
          self.initialFoldProb = [0, 0, 0, 0, 0.05, 0.1, 0.15, 0.2]
          self.initialHandBets = [10, 5, 5, 5, 0, 0, 0, 0] #Cash willing to initally bet
          self.maxInitialBet = [10, 10, 10, 5, 5, 5, 0, 0] #Percentage of initial cash willing to max bet
          self.gameFoldProb = [0.2, 0.1, 0.05, 0, 0, 0, 0, 0, 0, 0]
          self.gameBets = [0, 0, 0, 5, 5, 5, 5, 5, 10, 15] #Nothing, pair, 2P, 3K, straight, flush, fullHouse, 4K, straight flush, royal flush
          self.maxGameBets = [0, 0, 5, 5, 10, 15, 15, 15, 15, 15]
        elif opponentType == 'LPA': #Will always play, and rarely initiate a bet
          self.bettingFrequency = 0.1
          self.maxRank = 7
          self.initialFoldProb = [0, 0, 0, 0, 0, 0, 0, 0]
          self.initialHandBets = [10, 5, 5, 5, 0, 0, 0, 0] #Cash willing to initally bet
          self.maxInitialBet = [15, 15, 15, 15, 15, 15, 15, 15] #Percentage of initial cash willing to max bet
          self.gameFoldProb = [0.05, 0.01, 0, 0, 0, 0, 0, 0, 0, 0]
          self.gameBets = [0, 0, 0, 5, 5, 5, 5, 5, 10, 15] #Nothing, pair, 2P, 3K, straight, flush, fullHouse, 4K, straight flush, royal flush
          self.maxGameBets = [15, 15, 15, 15, 15, 15, 15, 15, 15, 15]
        # 'RANDOM' is also a type of opponent with all random actions
    def receiveCard(self, tuple):
        self.hand.append(tuple)

    def identifyStartHandRank(self, handCards):
      if len(handCards) != 2:
        raise Exception('Need 2 cards not %s' %(len(handCards)))

      rank1 = [[(14, 'off'), (14, 'off')], [(13, 'off'), (13, 'off')], [(12, 'off'), (12, 'off')],
                [(11, 'off'), (11, 'off')], [(14, 'same'), (13, 'same')]]
      rank2 = [[(10, 'off'), (10, 'off')], [(14, 'same'), (12, 'same')], [(14, 'same'), (11, 'same')],
                [(13, 'same'), (12, 'same')], [(14, 'off'), (13, 'off')]]
      rank3 = [[(9, 'off'), (9, 'off')], [(14, 'same'), (10, 'same')], [(13, 'same'), (11, 'same')],
                [(12, 'same'), (11, 'same')], [(11, 'same'), (10, 'same')], [(14, 'off'), (12, 'off')]]
      rank4 = [[(8, 'off'), (8, 'off')], [(13, 'same'), (10, 'same')], [(12, 'same'), (10, 'same')],
                [(11, 'same'), (9, 'same')], [(10, 'same'), (9, 'same')], [(9, 'same'), (8, 'same')],
                [(14, 'off'), (11, 'off')], [(13, 'off'), (12, 'off')]]
      rank5 = [[(7, 'off'), (7, 'off')], [(14, 'same'), (9, 'same')], [(14, 'same'), (8, 'same')],
                [(14, 'same'), (7, 'same')], [(14, 'same'), (6, 'same')], [(14, 'same'), (5, 'same')],
                [(14, 'same'), (4, 'same')], [(14, 'same'), (3, 'same')], [(14, 'same'), (2, 'same')],
                [(12, 'same'), (9, 'same')], [(10, 'same'), (8, 'same')], [(9, 'same'), (7, 'same')],
                [(8, 'same'), (7, 'same')], [(7, 'same'), (6, 'same')], [(13, 'off'), (11, 'off')],
                [(12, 'off'), (11, 'off')], [(11, 'off'), (10, 'off')]]
      rank6 = [[(6, 'off'), (6, 'off')], [(5, 'off'), (5, 'off')], [(13, 'same'), (9, 'same')],
                [(11, 'same'), (8, 'same')], [(8, 'same'), (6, 'same')], [(7, 'same'), (5, 'same')],
                [(5, 'same'), (4, 'same')], [(14, 'off'), (10, 'off')], [(13, 'off'), (10, 'off')],
                [(12, 'off'), (10, 'off')]]
      rank7 = [[(4, 'off'), (4, 'off')], [(3, 'off'), (3, 'off')], [(2, 'off'), (2, 'off')], 
                [(13, 'same'), (8, 'same')], [(13, 'same'), (7, 'same')], [(13, 'same'), (6, 'same')], [(13, 'same'), (5, 'same')],
                [(13, 'same'), (4, 'same')], [(13, 'same'), (3, 'same')], [(13, 'same'), (2, 'same')],
                [(12, 'same'), (8, 'same')], [(10, 'same'), (7, 'same')], [(6, 'same'), (4, 'same')],
                [(5, 'same'), (3, 'same')], [(4, 'same'), (3, 'same')], [(11, 'off'), (9, 'off')],
                [(10, 'off'), (9, 'off')], [(9, 'off'), (8, 'off')]]
      # 'rank8' is everything else
      
      simpleCards = [[None, 'off'], [None, 'off']]
      if handCards[0][1] == handCards[1][1]:
        simpleCards[0][1] = 'same'
        simpleCards[1][1] = 'same'

      topValue = max(handCards)
      botValue = min(handCards)
      simpleCards[0][0] = topValue[0]
      simpleCards[1][0] = botValue[0]
      tupleCards = [tuple(simpleCards[0]), tuple(simpleCards[1])]

      if tupleCards in rank1:
        return 1
      elif tupleCards in rank2:
        return 2
      elif tupleCards in rank3:
        return 3
      elif tupleCards in rank4:
        return 4
      elif tupleCards in rank5:
        return 5
      elif tupleCards in rank6:
        return 6
      elif tupleCards in rank7:
        return 7
      return 8 #End of identifyStartHandRank

    def assessHand(self, tableCards):
        bestHand = []

        # pre-flop
        if len(tableCards)==0:
            bestHand = self.hand
            #print '2 from hand, 0 from table'
            return (t.determineValue(bestHand), bestHand)

        # at flop
        if len(tableCards)==3:
            bestHand = self.hand + tableCards
            #print '2 from hand, 3 from table'
            return (t.determineValue(bestHand), bestHand)

        # at turn (4th card)
        if len(tableCards)==4:
            combValues = []
            for i in xrange(1,len(self.hand)+1):
                #print '%s from hand, %s from table' %(i, 5-i)
                for handCombination in itertools.combinations(self.hand, i):
                    for tableCombination in itertools.combinations(tableCards, len(tableCards)-i+1):
                        #print tableCombination
                        bestHand = list(handCombination) + list(tableCombination)
                        #print bestHand
                        combValues.append((t.determineValue(bestHand), bestHand))
            #print combValues
            # sort list by value and get all the hands resulting in an equivalent max value
            combValues = sorted(combValues, reverse=True)
            result = [combi for combi in combValues if combi[0] == combValues[0][0]]
            # sort list by best hand
            result = sorted(result, key= lambda var: var[1], reverse=True)
            return result[0]

        #at river
        if len(tableCards)==5:
            combValues = []
          # taking into account player hand
            for i in xrange(1,len(self.hand)+1):
                #print '%s from hand, %s from table' %(i, 5-i)
                for handCombination in itertools.combinations(self.hand, i):
                    for tableCombination in itertools.combinations(tableCards, len(tableCards)-i): 
                        #print tableCombination
                        bestHand = list(handCombination) + list(tableCombination)
                        #print bestHand
                        combValues.append((t.determineValue(bestHand), bestHand))
          # only looking at table cards
            #print '0 from hand, 5 from table'
            bestHand = tableCards
            #print bestHand
            combValues.append((t.determineValue(bestHand), bestHand))
            # sort list by value and get all the hands resulting in an equivalent max value
            # print [item[0] for item in combValues]
            combValues = sorted(combValues, reverse=True)
            # print [item[0] for item in combValues]
            result = [combi for combi in combValues if combi[0] == combValues[0][0]]
            # sort list by best hand
            result = sorted(result, key= lambda var: var[1], reverse=True)
            #print result
            # return first item in sorted list: one with the best 
            return result[0]

    def determineBet(self, normBet):
          if normBet == 0:
            if random.random() < self.betExploreProb:
              return ('Bet', 5)
            else:
              return ('Bet', 0)
          elif normBet == 5:
            prob = random.random()
            if prob < self.betExploreProb:
              return ('Bet', 0)
            elif prob < 1 - self.betExploreProb:
              return ('Bet', 5)
            else:
              return ('Bet', 10)
          elif normBet == 10:
            prob = random.random()
            if prob < self.betExploreProb:
              return ('Bet', 5)
            elif prob < 1 - self.betExploreProb:
              return ('Bet', 10)
            else:
              return ('Bet', 15)
          else:
            if random.random() < self.betExploreProb:
              return ('Bet', 10)
            else:
              return ('Bet', 15)

    def determineValIndex(self, value):
        if value >= 20:
          if value < 40:
            return 1 #Pair
          elif value < 60:
            return 2 #Two pair
          elif value < 80:
            return 3 #3 Kind
          elif value < 100:
            return 4 #Straight
          elif value < 120:
            return 5 #Flush
          elif value < 140:
            return 6 #Full House
          elif value < 160:
            return 7 #4 Kind
          elif value < 180:
            return 8 #Straight Flush
          else:
            return 9 #Royal Flush
        return 0 #Nothing

    def determineTAGPolicy(self, handCards, tableCards, oppPastAction):
      #oppPastAction: Touple of past action and amount to stay in at the pot, (None, 0) if first
      #Actions: (Fold, 0), (Bet, 0), (Bet, 5), (Bet, 10), (Bet, 15)
      if len(handCards) != 2:
        raise Exception('Hand needs 2 cards not %s' %(len(handCards)))

      #print oppPastAction
      oppAction = oppPastAction[0]
      currPhaseBet = oppPastAction[1]

      if oppAction == 'Fold': #Game is over; agent gave up
        return ('Fold', 0)

      if len(tableCards) == 0: #Pre-flop
        handRank = self.identifyStartHandRank(handCards)
        if oppAction == None:
          if random.random() < self.initialFoldProb[handRank - 1]: #Decreasing chance as rank goes up
            return ('Fold', 0)
          #Otherwise; see how we will normally bet
          normBet = self.initialHandBets[handRank-1]
          #Will weight neighboring bets with 0.2 probability
          #So if amount is 15 or 0; probability of betting 15/0 is 0.8
          #If amount is 5, for instance though, will bet 5 with 0.6 prob, 0 with 0.2 prob, and 10 with 0.2 prob
          #Use the determineBet function to handle these cases
          return self.determineBet(normBet)
        elif oppAction == 'Bet':
          if self.maxInitialBet[handRank-1] < currPhaseBet: #Fold if we would bet too much
            if random.random() < self.initialFoldProb[handRank - 1]:
              return ('Fold', 0)
          return ('Bet', currPhaseBet)
        else: #Invalid oppAction
          raise Exception('Invalid oppAction %s' %oppAction)

      if len(tableCards) == 3: #Flop
        value = self.assessHand(tableCards)[0]
        index = self.determineValIndex(value)
        #print value

        #print index

        haveStraight = straightAfterFlop(handCards, tableCards)
        haveFlush = flushAfterFlop(handCards, tableCards)

        if oppAction == None:
          if index > 4 or haveFlush == 1 or haveStraight == 1: #Fantastic chance of winning! Good shot at Straight/flush or greater - be very agressive
            #Go on - Bet!
            normBet = self.gameBets[index]
            return self.determineBet(normBet)
          else:
            #Should we 'explore' with a bet??
            if random.random() < self.bettingFrequency: #Raise this turn
              normBet = self.gameBets[index]
              return self.determineBet(normBet)
            else: #Continue, but don't bet
              return ('Bet', 0)
        elif oppAction == 'Bet':
          if index > 4 or haveFlush == 1 or haveStraight == 1: #Good chance of winning - match whatever agent wants!
            return ('Bet', currPhaseBet)
          else: #Less odds of winning
            if self.maxGameBets[index] < currPhaseBet: #Would bet too much
              if random.random() < self.gameFoldProb[index]:
                return ('Fold', 0)
            return ('Bet', currPhaseBet)
        else: #Invalid oppAction
          raise Exception('Invalid oppAction %s' %oppAction)

      if len(tableCards) == 4 or len(tableCards) == 5: #Turn and River turns
        value = self.assessHand(tableCards)[0]
        index = self.determineValIndex(value)

        haveStraight = straightAfterTurn(handCards, tableCards)
        haveFlush = flushAfterTurn(handCards, tableCards)

        if oppAction == None:
          if index > 4 or haveFlush == 1 or haveStraight == 1: #Fantastic chance of winning! Be agressive
            normBet = self.gameBets[index]
            return self.determineBet(normBet)
          else:
            if (index < 5 and haveFlush == -1) or (index < 4 and haveStraight == -1 and haveFlush != 1):
              #Too much risk: Don't bet
              return ('Bet', 0)
            #Should we 'explore' with a bet??
            elif random.random() < self.bettingFrequency: #Raise this turn
              normBet = self.gameBets[index]
              return self.determineBet(normBet)
            else: #Continue, but don't bet
              return ('Bet', 0)
        elif oppAction == 'Bet':
          if index > 4 or haveFlush == 1 or haveStraight == 1: #Good chance of winning - match whatever agent wants!
            return ('Bet', currPhaseBet)
          elif (index < 5 and haveFlush == -1) or (index < 4 and haveStraight == -1 and haveFlush != 1): 
            #Too much risk, abort
            return ('Fold', 0)
          else: #Less odds of winning
            if self.maxGameBets[index] < currPhaseBet: #Would bet too much
              if random.random() < self.gameFoldProb[index]:
                return ('Fold', 0)
            return ('Bet', currPhaseBet)
        else: #Invalid oppAction
          raise Exception('Invalid oppAction %s' %oppAction)

      print handCards
      print tableCards
      print oppPastAction
      return (None, None) #Error if this reaches here

    def determineLAGPolicy(self, handCards, tableCards, oppPastAction):
            #oppPastAction: Touple of past action and amount to stay in at the pot, (None, 0) if first
      #Actions: (Fold, 0), (Bet, 0), (Bet, 5), (Bet, 10), (Bet, 15)
      if len(handCards) != 2:
        raise Exception('Hand needs 2 cards not %s' %(len(handCards)))

      #print oppPastAction
      oppAction = oppPastAction[0]
      currPhaseBet = oppPastAction[1]

      if oppAction == 'Fold': #Game is over; agent gave up
        return ('Fold', 0)

      if len(tableCards) == 0: #Pre-flop
        handRank = self.identifyStartHandRank(handCards)
        if oppAction == None:
          if random.random() < self.initialFoldProb[handRank - 1]: #Decreasing chance as rank goes up
            return ('Fold', 0)
          #Otherwise; see how we will normally bet
          normBet = self.initialHandBets[handRank-1]
          #Will weight neighboring bets with 0.2 probability
          #So if amount is 15 or 0; probability of betting 15/0 is 0.8
          #If amount is 5, for instance though, will bet 5 with 0.6 prob, 0 with 0.2 prob, and 10 with 0.2 prob
          #Use the determineBet function to handle these cases
          return self.determineBet(normBet)
        elif oppAction == 'Bet':
          if self.maxInitialBet[handRank-1] < currPhaseBet: #Fold if we would bet too much
            if random.random() < self.initialFoldProb[handRank - 1]:
              return ('Fold', 0)
          return ('Bet', currPhaseBet)
        else: #Invalid oppAction
          raise Exception('Invalid oppAction %s' %oppAction)

      if len(tableCards) == 3: #Flop
        value = self.assessHand(tableCards)[0]
        index = self.determineValIndex(value)

        haveStraight = straightAfterFlop(handCards, tableCards)
        haveFlush = flushAfterFlop(handCards, tableCards)

        if oppAction == None:
            #Should we 'explore' with a bet??
            if random.random() < self.bettingFrequency: #Raise this turn
              normBet = self.gameBets[index]
              return self.determineBet(normBet)
            else: #Continue, but don't bet
              return ('Bet', 0)
        elif oppAction == 'Bet':
          if index > 4 or haveFlush == 1 or haveStraight == 1: #Good chance of winning - match whatever agent wants!
            return ('Bet', currPhaseBet)
          else: #Less odds of winning
            if self.maxGameBets[index] < currPhaseBet: #Would bet too much
              if random.random() < self.gameFoldProb[index]:
                return ('Fold', 0)
            return ('Bet', currPhaseBet)
        else: #Invalid oppAction
          raise Exception('Invalid oppAction %s' %oppAction)

      if len(tableCards) == 4 or len(tableCards) == 5: #Turn and River turns
        value = self.assessHand(tableCards)[0]
        index = self.determineValIndex(value)

        haveStraight = straightAfterTurn(handCards, tableCards)
        haveFlush = flushAfterTurn(handCards, tableCards)

        if oppAction == None:
            if (index < 5 and haveFlush == -1) or (index < 4 and haveStraight == -1 and haveFlush != 1):
              #Too much risk: Don't bet
              return ('Bet', 0)
            #Should we 'explore' with a bet??
            elif random.random() < self.bettingFrequency: #Raise this turn
              normBet = self.gameBets[index]
              return self.determineBet(normBet)
            else: #Continue, but don't bet
              return ('Bet', 0)
        elif oppAction == 'Bet':
          if index > 4 or haveFlush == 1 or haveStraight == 1: #Good chance of winning - match whatever agent wants!
            return ('Bet', currPhaseBet)
          elif (index < 5 and haveFlush == -1) or (index < 4 and haveStraight == -1 and haveFlush != 1): 
            #Too much risk, abort
            return ('Fold', 0)
          else: #Less odds of winning
            if self.maxGameBets[index] < currPhaseBet: #Would bet too much
              if random.random() < self.gameFoldProb[index]:
                return ('Fold', 0)
            return ('Bet', currPhaseBet)
        else: #Invalid oppAction
          raise Exception('Invalid oppAction %s' %oppAction)

      print handCards
      print tableCards
      print oppPastAction
      return (None, None) #Error if this reaches here

    def determineTPAPolicy(self, handCards, tableCards, oppPastAction):
      #oppPastAction: Touple of past action and amount to stay in at the pot, (None, 0) if first
      #Actions: (Fold, 0), (Bet, 0), (Bet, 5), (Bet, 10), (Bet, 15)
      if len(handCards) != 2:
        raise Exception('Hand needs 2 cards not %s' %(len(handCards)))

      #print oppPastAction
      oppAction = oppPastAction[0]
      currPhaseBet = oppPastAction[1]

      if oppAction == 'Fold': #Game is over; agent gave up
        return ('Fold', 0)

      if len(tableCards) == 0: #Pre-flop
        handRank = self.identifyStartHandRank(handCards)
        if oppAction == None:
          if random.random() < self.initialFoldProb[handRank - 1]: #Decreasing chance as rank goes up
            return ('Fold', 0)
          #If rank is too high, don't bet if we stay in
          if handRank >= self.maxRank:
            return ('Bet', 0)
          #Otherwise; see how we will normally bet
          normBet = self.initialHandBets[handRank-1]
          #Will weight neighboring bets with 0.2 probability
          #So if amount is 15 or 0; probability of betting 15/0 is 0.8
          #If amount is 5, for instance though, will bet 5 with 0.6 prob, 0 with 0.2 prob, and 10 with 0.2 prob
          #Use the determineBet function to handle these cases
          return self.determineBet(normBet)
        elif oppAction == 'Bet':
          if self.maxInitialBet[handRank-1] < currPhaseBet: #Fold if we would bet too much
            if random.random() < self.initialFoldProb[handRank - 1]:
              return ('Fold', 0)
          return ('Bet', currPhaseBet)
        else: #Invalid oppAction
          raise Exception('Invalid oppAction %s' %oppAction)

      if len(tableCards) == 3: #Flop
        value = self.assessHand(tableCards)[0]
        index = self.determineValIndex(value)
        #print value

        #print index

        haveStraight = straightAfterFlop(handCards, tableCards)
        haveFlush = flushAfterFlop(handCards, tableCards)

        if oppAction == None:
          if index > 4 or haveFlush == 1 or haveStraight == 1: #Fantastic chance of winning! Good shot at Straight/flush or greater - be very agressive
            #Go on - Bet!
            normBet = self.gameBets[index]
            return self.determineBet(normBet)
          else:
            #Should we 'explore' with a bet??
            if random.random() < self.bettingFrequency: #Raise this turn
              normBet = self.gameBets[index]
              return self.determineBet(normBet)
            else: #Continue, but don't bet
              return ('Bet', 0)
        elif oppAction == 'Bet':
          if index > 4 or haveFlush == 1 or haveStraight == 1: #Good chance of winning - match whatever agent wants!
            return ('Bet', currPhaseBet)
          else: #Less odds of winning
            if self.maxGameBets[index] < currPhaseBet: #Would bet too much
              if random.random() < self.gameFoldProb[index]:
                return ('Fold', 0)
            return ('Bet', currPhaseBet)
        else: #Invalid oppAction
          raise Exception('Invalid oppAction %s' %oppAction)

      if len(tableCards) == 4 or len(tableCards) == 5: #Turn and River turns
        value = self.assessHand(tableCards)[0]
        index = self.determineValIndex(value)

        haveStraight = straightAfterTurn(handCards, tableCards)
        haveFlush = flushAfterTurn(handCards, tableCards)

        if oppAction == None:
          if index > 4 or haveFlush == 1 or haveStraight == 1: #Fantastic chance of winning! Be agressive
            normBet = self.gameBets[index]
            return self.determineBet(normBet)
          else:
            if (index < 5 and haveFlush == -1) or (index < 4 and haveStraight == -1 and haveFlush != 1):
              #Too much risk: Don't bet
              return ('Bet', 0)
            #Should we 'explore' with a bet??
            elif random.random() < self.bettingFrequency: #Raise this turn
              normBet = self.gameBets[index]
              return self.determineBet(normBet)
            else: #Continue, but don't bet
              return ('Bet', 0)
        elif oppAction == 'Bet':
          if index > 4 or haveFlush == 1 or haveStraight == 1: #Good chance of winning - match whatever agent wants!
            return ('Bet', currPhaseBet)
          elif (index < 5 and haveFlush == -1) or (index < 4 and haveStraight == -1 and haveFlush != 1): 
            #Too much risk, abort
            return ('Fold', 0)
          else: #Less odds of winning
            if self.maxGameBets[index] < currPhaseBet: #Would bet too much
              if random.random() < self.gameFoldProb[index]:
                return ('Fold', 0)
            return ('Bet', currPhaseBet)
        else: #Invalid oppAction
          raise Exception('Invalid oppAction %s' %oppAction)

      print handCards
      print tableCards
      print oppPastAction
      return (None, None) #Error if this reaches here

    def determineLPAPolicy(self, handCards, tableCards, oppPastAction):
            #oppPastAction: Touple of past action and amount to stay in at the pot, (None, 0) if first
      #Actions: (Fold, 0), (Bet, 0), (Bet, 5), (Bet, 10), (Bet, 15)
      if len(handCards) != 2:
        raise Exception('Hand needs 2 cards not %s' %(len(handCards)))

      #print oppPastAction
      oppAction = oppPastAction[0]
      currPhaseBet = oppPastAction[1]

      if oppAction == 'Fold': #Game is over; agent gave up
        return ('Fold', 0)

      if len(tableCards) == 0: #Pre-flop
        handRank = self.identifyStartHandRank(handCards)
        if oppAction == None:
          if random.random() < self.initialFoldProb[handRank - 1]: #Decreasing chance as rank goes up
            return ('Fold', 0)
          #If rank is too high, don't bet if we stay in
          if handRank >= self.maxRank:
            return ('Bet', 0)
          #Otherwise; see how we will normally bet
          normBet = self.initialHandBets[handRank-1]
          #Will weight neighboring bets with 0.2 probability
          #So if amount is 15 or 0; probability of betting 15/0 is 0.8
          #If amount is 5, for instance though, will bet 5 with 0.6 prob, 0 with 0.2 prob, and 10 with 0.2 prob
          #Use the determineBet function to handle these cases
          return self.determineBet(normBet)
        elif oppAction == 'Bet':
          if self.maxInitialBet[handRank-1] < currPhaseBet: #Fold if we would bet too much
            if random.random() < self.initialFoldProb[handRank - 1]:
              return ('Fold', 0)
          return ('Bet', currPhaseBet)
        else: #Invalid oppAction
          raise Exception('Invalid oppAction %s' %oppAction)

      if len(tableCards) == 3: #Flop
        value = self.assessHand(tableCards)[0]
        index = self.determineValIndex(value)

        haveStraight = straightAfterFlop(handCards, tableCards)
        haveFlush = flushAfterFlop(handCards, tableCards)

        if oppAction == None:
            #Should we 'explore' with a bet??
            if random.random() < self.bettingFrequency: #Raise this turn
              normBet = self.gameBets[index]
              return self.determineBet(normBet)
            else: #Continue, but don't bet
              return ('Bet', 0)
        elif oppAction == 'Bet':
          if index > 4 or haveFlush == 1 or haveStraight == 1: #Good chance of winning - match whatever agent wants!
            return ('Bet', currPhaseBet)
          else: #Less odds of winning
            if self.maxGameBets[index] < currPhaseBet: #Would bet too much
              if random.random() < self.gameFoldProb[index]:
                return ('Fold', 0)
            return ('Bet', currPhaseBet)
        else: #Invalid oppAction
          raise Exception('Invalid oppAction %s' %oppAction)

      if len(tableCards) == 4 or len(tableCards) == 5: #Turn and River turns
        value = self.assessHand(tableCards)[0]
        index = self.determineValIndex(value)

        haveStraight = straightAfterTurn(handCards, tableCards)
        haveFlush = flushAfterTurn(handCards, tableCards)

        if oppAction == None:
            if (index < 5 and haveFlush == -1) or (index < 4 and haveStraight == -1 and haveFlush != 1):
              #Too much risk: Don't bet
              return ('Bet', 0)
            #Should we 'explore' with a bet??
            elif random.random() < self.bettingFrequency: #Raise this turn
              normBet = self.gameBets[index]
              return self.determineBet(normBet)
            else: #Continue, but don't bet
              return ('Bet', 0)
        elif oppAction == 'Bet':
          if index > 4 or haveFlush == 1 or haveStraight == 1: #Good chance of winning - match whatever agent wants!
            return ('Bet', currPhaseBet)
          elif (index < 5 and haveFlush == -1) or (index < 4 and haveStraight == -1 and haveFlush != 1): 
            #Too much risk, abort
            return ('Fold', 0)
          else: #Less odds of winning
            if self.maxGameBets[index] < currPhaseBet: #Would bet too much
              if random.random() < self.gameFoldProb[index]:
                return ('Fold', 0)
            return ('Bet', currPhaseBet)
        else: #Invalid oppAction
          raise Exception('Invalid oppAction %s' %oppAction)

      print handCards
      print tableCards
      print oppPastAction
      return (None, None) #Error if this reaches here

    def determinePolicy(self, state):
      handCards = self.hand
      tableCards = state[1]
      lastAction = state[3]
      if state[4] == 3:
        lastAction = (None, 0)

      act = None
      if self.opponentType == 'TAG':
        act = self.determineTAGPolicy(handCards, tableCards, lastAction)
      if self.opponentType == 'LAG':
        act = self.determineLAGPolicy(handCards, tableCards, lastAction)
      if self.opponentType == 'TPA':
        act = self.determineTPAPolicy(handCards, tableCards, lastAction)
      if self.opponentType == 'LPA':
        act = self.determineLPAPolicy(handCards, tableCards, lastAction)
      if self.opponentType == 'RANDOM':
        val = random.random()
        if val < 0.2:
          act = ('Fold', 0)
        elif val < 0.4:
          act = ('Bet', 0)
        elif val < 0.6:
          act = ('Bet', 5)
        elif val < 0.8:
          act = ('Bet', 10)
        else:
          act = ('Bet', 15)

      if state[0] == 0:
        self.roundBet = act[1]
      if state[4] == 2:
        diff = act[1] - self.roundBet
        act = (act[0], diff)
      return act

  

# given a set of cards, function gives the largest number of consecutive cards in set
def checkStraightLength(cards):
  cards.sort()
  #print cards
  cardRanks = [x[0] for x in cards]
  rankCounter = collections.Counter(cardRanks)
  ranks = rankCounter.keys()
  ranks.sort()
  maxLength = 1
  curLength = 1
  curRank = ranks[0]
  for i in xrange(1, len(ranks)):
    if ranks[i] == (curRank + 1):
      curLength += 1
      curRank += 1
      if curLength > maxLength: maxLength = curLength
    else:
      curLength = 1
      curRank = ranks[i]
  if cards[-1][0] == 14 and 1 not in cardRanks:
    #Test for Ace case
    aceLow = (1, cards[-1][1]) #Not normally a valid card; used to model a low ace
    aceLowCards = cards[0:len(cards)-1]
    aceLowCards.append(aceLow)
    aceLowCards.sort()
    maxLength = max(maxLength, checkStraightLength(aceLowCards))
  return maxLength

def straightAfterFlop(handCards, tableCards):
  both = checkStraightLength(handCards + tableCards)
  table = checkStraightLength(tableCards)
  return (both > table) and (both >= 3)

def straightAfterTurn(handCards, tableCards):
  both = checkStraightLength(handCards + tableCards)
  table = checkStraightLength(tableCards)
  if (both > table) and (both >= 4):
    return 1 #You can get a straight
  if table == 4:
    return -1 #You're in danger
  return 0

def checkFlushLength(cards):
  counter = collections.Counter()
  for card in cards:
    suit = card[1]
    counter[suit] +=1
  return max(counter.iteritems(), key=operator.itemgetter(1))[1]

def flushAfterFlop(hand, tableCards):
  both = checkFlushLength(hand + tableCards)
  table = checkFlushLength(tableCards)
  if (both >= 3 and both > table):
    return True
  else:
    return False

def flushAfterTurn(hand, tableCards):
  both = checkFlushLength(hand + tableCards)
  table = checkFlushLength(tableCards)
  if (both >= 4 and both > table):
    return 1
  if table == 4:
    return -1
  else:
    return 0

d = Deck()        
t = Table(d)
p1 = Agent()
p2 = Agent()  
  
def computeBaseline(d, t, p1, p2):
  
  # possible actions are : check or fold
  actions = []
  # unsorted copy of list of cards on the table
  unsortedTableCards = []
  # shuffle deck
  d.shuffle()
  # deal players
  t.dealPlayers(p1,p2,d)
  preFlopVal = p1.assessHand(t.tableCards)
  # deal table - flop
  t.flipCard(d)
  t.flipCard(d)
  t.flipCard(d)
  unsortedTableCards += t.tableCards
  # asses hand
  if preFlopVal[0] >= 11 or flushAfterFlop(p1.hand, t.tableCards) or straightAfterFlop(p1.hand, t.tableCards):
    actions.append('check')
  else:
    actions.append('fold')
    
  # deal table - turn
  t.flipCard(d)
  unsortedTableCards.append(t.tableCards[-1])
  # asses hand
  turnVal = p1.assessHand(t.tableCards)
  if actions[-1] != 'fold':
    if turnVal[0] >= 22:
      if flushAfterTurn(p1.hand, t.tableCards) == -1:
        if turnVal[0] >= 100:
          actions.append('check')
        else:
          actions.append('fold')
      elif straightAfterTurn(p1.hand, t.tableCards) == -1:
        if turnVal[0] >= 80:
          actions.append('check')
        else:
          actions.append('fold')
      else:
        actions.append('check')
    else:
      if flushAfterTurn(p1.hand, t.tableCards) == 1 or straightAfterTurn(p1.hand, t.tableCards) == 1:
        actions.append('check')
      else:
        actions.append('fold')
  # deal table - river
  t.flipCard(d)
  unsortedTableCards.append(t.tableCards[-1])
  # asses hand
  agentVal = p1.assessHand(t.tableCards)
  oppVal = p2.assessHand(t.tableCards)
  if actions[-1] != 'fold':
    if flushAfterTurn(p1.hand, t.tableCards) == -1:
      if agentVal[0] < 100:
        actions.append('fold')
      else:
        actions.append('check')
    elif straightAfterTurn(p1.hand, t.tableCards) == -1:
      if agentVal[0] < 80:
        actions.append('fold')
      else:
        actions.append('check')
    elif agentVal[0] >= 20:
      actions.append('check')
    else: actions.append('fold')
  
  agentVal = (agentVal[0], sorted(agentVal[1], reverse=True))
  oppVal = (oppVal[0], sorted(oppVal[1], reverse=True))
  
  # See if we have (or could have) won
  #print "Agent hand: " + str(p1.hand)
  #print "Opponent hand: " + str(p2.hand)
  #print "Table cards: " + str(t.tableCards)
  #print "Unsorted table cards: " + str(unsortedTableCards)
  #print "Agent score: " + str(agentVal)
  #print "Opponent score: " + str(oppVal)
  #print "Actions :" + str(actions)

 
  if agentVal[0] > oppVal[0]:
    if actions[-1] == 'check': return 2
    else: return 0
  elif agentVal[0] == oppVal[0]:
    if (agentVal[1] > oppVal[1]):
      if actions[-1] == 'check': return 2
      else: return 0
    if (agentVal[1] < oppVal[1]):
      if actions[-1] == 'fold': return 1
      else: return -1
  else:
    if actions[-1] == 'fold': return 1
    else: return -1
  # compare actual


    
'''
if agentVal[0] > oppVal[0]:
      if actions[-1] == 'Bet': return 2
      else: return 0
  elif agentVal[0] == oppVal[0]:
      if (agentVal[1] > oppVal[1]):
          if actions[-1] == 'Bet': return 2
          else: return 0
      if (agentVal[1] < oppVal[1]):
          if actions[-1] == 'Fold': return 1
          else: return -1
      else:
          if actions[-1] == 'Fold': return 1
          else: return -1
'''
    #print computeBaseline(d, t, p1, p2)

