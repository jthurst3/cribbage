# cribbage_objects.py
# hand, card, and other objects
# J. Hassler Thurston
# 23 December 2015

import random
import os
import math

class Hand(object):
    def __init__(self, cards):
        self.cards = cards
        self.sort()

    # prints out a player's hand
    def __str__(self):
        n = 1
        print_str = ""
        for card in self.cards:
            print_str += "("+str(n)+") "
            print_str += str(card) + "   "
            n += 1
        return print_str

    # sorts a player's hand
    def sort(self):
        self.cards.sort(key=lambda card: card.number)

    # scores a player's hand
    def score(self, top_card):
        # temporarily add the top card to the hand
        if top_card:
            self.cards.append(top_card)
        self.sort()
        # fifteens
        sc = self.score_fifteens(0)
        # pairs etc
        sc += self.score_pairs(sc)
        # runs
        sc += self.score_runs(sc)
        # remove the top card from the hand
        if top_card:
            self.cards.remove(top_card)
        # flushes
        sc += self.score_flushes(top_card, sc)
        # his knobs
        sc += self.score_his_knobs(top_card, sc)
        # return the score
        return sc

    def score_fifteens(self, current_score):
        # brute force way: for every combination of cards, see if the values add up to 15
        sc = 0
        for i in range(2**len(self.cards)):
            subset = []
            for j in range(len(self.cards)):
                if (i >> j) % 2 != 0:
                    subset.append(self.cards[j])
            # score the subset
            if get_sum(subset) == 15:
                for s in subset:
                    print s,
                print 
                sc += 2
                say( "fifteen for " + str(current_score+sc))
        return sc

    def score_pairs(self, current_score):
        sc = 0
        # cards are sorted, so check adjacent cards
        current_number = 0
        cards_at_number = 0
        actual_cards = []
        for c in self.cards:
            newnum = c.number
            if newnum != current_number:
                if cards_at_number >= 2:
                    sc += math.factorial(cards_at_number)
                    num_pairs = math.factorial(cards_at_number)/2
                    for card in actual_cards:
                        print card,
                    print
                    if num_pairs == 1:
                        say("pair for " + str(current_score+sc))
                    else:
                        say(str(num_pairs) + " pairs for " + str(current_score+sc))
                current_number = newnum
                cards_at_number = 0
                actual_cards = []

            cards_at_number += 1
            actual_cards.append(c)
        return sc

    def score_runs(self, current_score):
        sc = 0
        # cards are sorted, so check adjacent runs
        # group the cards in buckets depending on their number
        d = {}
        card_dict = {}
        for i in range(1, 15):
            d[i] = 0
            card_dict[i] = []
        for c in self.cards:
            d[c.number] += 1
            card_dict[c.number].append(c)
        # loop through the buckets again and compute the number of runs
        num_in_row = 0
        num_runs_in_row = 1
        actual_cards = []
        for i in range(1, 15):
            if d[i] == 0:
                if num_in_row >= 3:
                    sc += num_in_row * num_runs_in_row
                    for card in actual_cards:
                        print card,
                    print
                    say(str(num_runs_in_row) + " runs of " + str(num_in_row) + " for " + str(current_score+sc))
                num_in_row = 0
                num_runs_in_row = 1
                actual_cards = []
            else:
                num_in_row += 1
                num_runs_in_row *= d[i]
                actual_cards.extend(card_dict[i])
        return sc

    def score_flushes(self, top_card, current_score):
        if len(self.cards) == 0:
            return 0
        sc = 0
        # check if the cards in the hand are all of the same suit
        same_suit = True
        suit = self.cards[0].suit
        for c in self.cards:
            if c.suit != suit:
                same_suit = False
        if same_suit:
            sc += len(self.cards)
            if top_card and top_card.suit == suit:
                sc += 1
        if sc > 0:
            say("flush for " + str(current_score+sc))
        return sc

    def score_his_knobs(self, top_card, current_score):
        # check if there is a Jack in the hand that is the same suit as the top card
        if not top_card:
            return 0
        suit = top_card.suit
        for c in self.cards:
            if c.number == 11 and c.suit == suit:
                print c, "   ", top_card
                say("his knobs for " + str(current_score+1))
                return 1
        return 0


# sums up the values of cards
def get_sum(cards):
    s = 0
    for c in cards:
        s += c.value
    return s

class Deck(object):
    def __init__(self):
        self.deck = []
        # initialize the deck
        # TODO: make it so that these next few lines are only executed once when the program starts
        suits = ['Clubs', 'Spades', 'Diamonds', 'Hearts']
        for suit in suits:
            for num in range(1, 14):
                self.deck.append(Card(num, suit))
        # shuffle the deck
        self.shuffle()
        # assign hands to each player, and the top card
        self.hands = [Hand(self.deck[:6]), Hand(self.deck[6:12])]
        self.top_card = self.deck[12]
        self.crib = Hand([])

    def shuffle(self):
        # from http://stackoverflow.com/questions/473973/shuffle-an-array-with-python
        random.shuffle(self.deck)

    # string representation of a deck
    def __str__(self):
        string = ""
        string += "Player 1: " + str(self.hands[0]) + "\n"
        string += "Player 2: " + str(self.hands[1]) + "\n"
        string += "Top card: " + str(self.topcard) + "\n"
        string += "Crib: " + str(self.crib) + "\n"
        return string



class Card(object):
    def __init__(self, number, suit):
        self.number = number
        self.suit = suit
        self.name = str(number)
        self.played = False
        if number == 11:
            self.name = "Jack"
        elif number == 12:
            self.name = "Queen"
        elif number == 13:
            self.name = "King"
        elif number == 1:
            self.name = "Ace"
        self.value = min(number, 10)

    def __str__(self):
        return self.name + " of " + self.suit

def say(string):
    os.system("say '" + string + "'")


d = Deck()
print d.hands[0]
print d.top_card
print d.hands[0].score(d.top_card)
