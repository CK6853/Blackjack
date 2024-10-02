import random

class Card:
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value
    
    def __str__(self):
        return f"{self.getName()} of {self.suit}"
    
    def getName(self):
        match self.value:
            case 1:
                return "Ace"
            case 11: 
                return "Jack"
            case 12:
                return "Queen"
            case 13:
                return "King"
            case _:
                return self.value

class Deck:
    def __init__(self, numDecks = 1):
        self.cards = []
        self.numDecks = numDecks
        self.addNewDeck()

    def addNewDeck(self):
        for _ in range(self.numDecks):
            for suit in ["Hearts", "Diamonds", "Spades", "Clubs"]:
                for value in range(1,14):
                    newCard = Card(suit, value)
                    self.cards.append(newCard)

    def shuffle(self):
        tempArray = []
        while len(self.cards) > 0:
            randomIndex = random.randint(0,len(self.cards)-1)
            tempArray.append(self.cards.pop(randomIndex))
        self.cards = tempArray

    def deal(self, target = None, number = 1):
        self.testForEmpty()
        if target == None:  return self.cards.pop(0)

        for _ in range(number):
            self.testForEmpty()
            target.add(self.cards.pop(0))

    def testForEmpty(self):
        if len(self.cards) == 0:
            self.addNewDeck()
            self.shuffle()

    def add(self, newCard):
        self.cards.append(newCard)
    
class Hand(Deck):
    def __init__(self, isOnlyHand = True):
        self.cards = []
        self.isOnlyHand = isOnlyHand
    
    def __str__(self):
        if str(Score(self.cards)) == "-1": 
            printStr = "Bust!\n"
        else:
            printStr = f"Score: {Score(self.cards)}\n"
        for card in self.cards:
            printStr += f"{card}\n"
        if self.isBlackJack(): printStr += "Blackjack!\n"
        return printStr
    
    def getScores(self):
        return Score(self.cards).scores
    
    def isBlackJack(self):
        if not self.isOnlyHand: return False
        if len(self.cards) != 2: return False
        if self.cards[0].value == 1 and self.cards[1].value >= 10: return True
        if self.cards[1].value == 1 and self.cards[0].value >= 10: return True
        return False

class Score:
    def __init__(self, deck):
        self.scores = []
        self.scores.append(0)

        for card in deck:
            self.addCard(card)
        self.scores = list(dict.fromkeys(self.scores))
        self.scores.sort()

    def addCard(self, card):
        if card.value == 1:
            self.addNewAce()
        else:
            for i in range(len(self.scores)):
                if self.scores[i] == -1: continue
                self.scores[i] = self.scores[i] + min(card.value, 10)
        for i in range(len(self.scores)):
            if self.scores[i] > 21: self.scores[i] = -1
        
    def addNewAce(self):
        newScores = []
        for score in self.scores:
            if score == -1: continue
            newScores.append(score + 1)
            newScores.append(score + 11)
        self.scores = newScores

    def __str__(self):
        if len(self.scores) == 1 and self.scores[0] == 0: return "0"

        returnStr = ""
        for i in range(len(self.scores)):
            if self.scores[i] == -1: continue
            if returnStr == "":
                returnStr = str(self.scores[i])
            else:
                returnStr += " or " + str(self.scores[i])
        if returnStr == "": return "-1"
        return returnStr

def Main():
    deck = Deck()
    deck.shuffle()

    playerWins = 0
    dealerWins = 0

    playing = True
    while playing:
        print(f"Cards remaining: {len(deck.cards)}")
        playerHand = Hand()
        dealerHand = Hand()
        playerHand2 = None

        deck.deal(dealerHand)
        deck.deal(playerHand, 2)
        
        print("Dealer showing:")
        print(dealerHand)
        print("")
        
        if playerHand.cards[0].value == playerHand.cards[1].value and getYesNo(playerHand) == "yes":
            playerHand2 = Hand()
            playerHand2.add(playerHand.cards.pop())
            deck.deal(playerHand)
            deck.deal(playerHand2)
            # Could do this much more cleanly, and accounting for the possibility of more than one split hand
            # For a 1-day build, I can't be bothered

        if getTopScore(playerHand) != 21: playerHand = resolveHand(deck, playerHand)
        if not playerHand2 == None and getTopScore(playerHand2) != 21: playerHand2 = resolveHand(deck, playerHand2)

        while shouldDealerHit(dealerHand, playerHand, playerHand):
            deck.deal(dealerHand)

        print("-----Final hands-----")
        print("Your hand:")
        print(playerHand)
        if not playerHand2 == None:
            print("Your second hand:")
            print(playerHand2)
        print("Dealer's hand:")
        print(dealerHand)

        if playerHand2 == None: 
            dealerWins, playerWins = displayWinner(dealerHand, playerHand, dealerWins, playerWins)

        else:
            dealerWins, playerWins = displayWinner(dealerHand, playerHand, dealerWins, playerWins, "First Hand: ")
            dealerWins, playerWins = displayWinner(dealerHand, playerHand2, dealerWins, playerWins, "Second Hand: ")

        print(f"Dealer has won {dealerWins} hands, player has won {playerWins} hands.")

        playing = getContinuePlaying()

    print("Thanks for playing!")

def getContinuePlaying():
    while True:
        response = input("Do you want to continue playing? ")
        if response != "yes" and response != "no": 
            print("Valid options are 'yes' or 'no'")
        else:
            return response == "yes"

def displayWinner(dealerHand, playerHand, dealerWins, playerWins, prefixString = ""):
    if isBust(playerHand) or getTopScore(dealerHand) > getTopScore(playerHand):
        print(prefixString + "Dealer wins!")
        dealerWins += 1
    elif getTopScore(dealerHand) < getTopScore(playerHand):
        print(prefixString + "You win!")
        playerWins += 1
    else:
        print(prefixString + "Draw!")
    
    return dealerWins, playerWins

def resolveHand(deck, playerHand):
    print("Your hand:")
    print(playerHand)
    while True: # One of the cases will always eventually return
        response = getPlayerResponse()

        match response:
            case "hit":
                deck.deal(playerHand)
                print(playerHand)
                if isBust(playerHand): 
                    print("You busted!")
                    return playerHand
                if getTopScore(playerHand) == 21:
                    return playerHand
            case "stand":
                return playerHand    

def getYesNo(hand):
    print("Your hand:")
    print(hand)
    while True:
        response = input("Do you want to split your hand? ")
        if response != "yes" and response != "no": 
            print("Valid options are 'yes' or 'no'")
        else:
            return response
        
def getPlayerResponse():
    while True:
        response = input("What do you want to do? (hit or stand)")
        if response != "hit" and response != "stand": 
            print("Valid options are 'hit' or 'stand'")
        else:
            return response
        
def isBust(hand):
    return str(Score(hand.cards)) == "-1"

def getTopScore(hand):
    return int(max(Score(hand.cards).scores))

def shouldDealerHit(dealerHand, playerHand1, playerHand2):
    # Quick and dirty - dealer hits until above 16 or beating the player

    if isBust(dealerHand): return False
    if getTopScore(dealerHand) > 16: return False

    if playerHand2 == None:
        if getTopScore(playerHand1) > getTopScore(dealerHand): return True
    else:
        if getTopScore(playerHand1) > getTopScore(dealerHand) and getTopScore(playerHand2) > getTopScore(dealerHand): return True
    
    return False
Main()