#!/usr/bin/env python
# cribbage.py
# plays the game cribbage on the command line, or plays against itself for purposes of machine learning
# J. Hassler Thurston
# 21 December 2015

import random

class Card(object):
    def __init__(self, number, suit):
        self.number = number
        self.suit = suit
        self.name = str(number)
        if number == 11:
            self.name = "Jack"
        elif number == 12:
            self.name = "Queen"
        elif number == 13:
            self.name = "King"
        elif number == 1:
            self.name = "Ace"
        self.value = max(number, 10)

    def __str__(self):
        return self.name + " of " + self.suit


def initialize_deck():
    suits = ['Clubs', 'Spades', 'Diamonds', 'Hearts']
    deck = []
    for suit in suits:
        for num in range(1, 14):
            deck.append(Card(num, suit))
    return deck
        
deck = initialize_deck()

# decide whether the game is over
def game_over(score):
    return score[0] > 120 or score[1] > 120

def play():
    score = [0, 0]
    crib_player = 0
    while not game_over(score):
        turn(score, crib_player)
        crib_player = (crib_player+1)%2

def turn(score, crib_player):
    # print out the score to the player
    print_score(score)
    # shuffle the cards and deal them
    cards = shuffle_cards()
    hands, top_card = deal(cards)
    # show the six cards to the player, and ask them to select cards to put in the crib.
    crib_cards = player_select_crib(hands[0], crib_player)
    crib_cards.extend(select_crib(hands[1], crib_player))
    # show the top card on the deck
    show_top_card(top_card)
    # interactively play the cards
    play_cards_interactive(hands, score)
    # score the hands
    score_hands_interactive(hands, score)
    # show the score at the end of the turn
    print_score(score)

# shuffle the cards in the deck
def shuffle_cards():
    # from http://stackoverflow.com/questions/473973/shuffle-an-array-with-python
    random.shuffle(deck)
    return deck

# deal out the cards to each player
def deal(cards):
    # deck is already shuffled, so pick out the top cards
    hands = [cards[:6], cards[6:12]]
    top_card = cards[12]
    return hands, top_card

# ask the player to select two cards for the crib
def player_select_crib(hand, crib_player):
    crib_cards = []
    # show the hand to the player and ask them to pick two cards
    print "Here are the cards in your hand. It is your",
    if crib_player == 1:
        print "opponent's",
    print "crib."
    print_hand(hand, True)
    while len(crib_cards) < 2:
        try:
            card = int(raw_input("Please select a card (1-6) to put in your crib."))
            if card <= 0 or card > 6:
                raise ValueError
            if hand[card-1] in crib_cards:
                raise ValueError
            crib_cards.append(hand[card-1])
            print "Selected card " + str(card) +  "."
        except ValueError:
            print "Invalid card number."
    return crib_cards

# computer program to select the crib
def select_crib(hand, crib_player):
    # stub
    return [hand[0], hand[1]]

# prints out a player's hand
# if the second argument is True, numbers the cards from 1-n
def print_hand(hand, numbered):
    n = 1
    print_str = ""
    for card in hand:
        if numbered:
            print_str += "("+str(n)+") "
        print_str += str(card) + "   "
        n += 1
    print print_str

def show_top_card(top_card):
    print "top card is: " + str(top_card)

# prints out the score
def print_score(score):
    print "Score... YOU: " + str(score[0]) + " - " + str(score[1]) + " :COMPUTER"

# plays cards interactively
def play_cards_interactive(hands, score):
    pass

# scores the hands
def score_hands_interactive(hands, score):
    pass


if __name__ == '__main__':
    play()





