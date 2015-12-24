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

    # from http://stackoverflow.com/questions/12933964/printing-a-list-of-objects-of-user-defined-class
    def __repr__(self):
        return str(self)

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
            # TODO: doesn't detect king pairs
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


class Table(object):
    def __init__(self, game, round, deck, crib_player):
        self.game = game
        self.round = round
        self.deck = deck
        self.crib_player = crib_player
        self.hands = deck.hands
        self.table_cards = []
        self.count = 0
        self.go_declared = False
        self.go_declared_player = -1
        # the person who doesn't have the crib starts
        self.player = (self.crib_player+1)%2
        self.num_cards_played = 0

    def __str__(self):
        s = ""
        s += "Table cards: " + str(self.table_cards) + ". Count: " + str(self.count)
        s += ". "
        if self.go_declared:
            s += "Go declared by player " + str(self.go_declared_player) + "."
        return s

    def __repr__(self):
        return str(self)

    # plays cards interactively
    def play_cards_interactive(self):
        # initialize the table
        self.reset_table()
        for hand in self.hands:
            for c in hand.cards:
                c.played = False
        # keep track of fifteens, pairs, three+four of a kinds, and runs
        while self.num_cards_played < 8:
            if self.player == 0:
                self.prompt_user_play_cards()
            else:
                self.computer_play_cards()

    def reset_table(self):
        self.count = 0
        self.table_cards = []
        self.go_declared = False
        self.go_declared_player = -1

    def prompt_user_play_cards(self):
        while True:
            try:
                print "Count is " + str(self.count) + ". Here is what's on the table: "
                print self.table_cards, "."
                print "Here is what's in your hand: ",
                print self.hands[0]
                print "Here are the cards you can play: ",
                playable_cards = self.get_playable_cards(self.hands[0])
                print playable_cards
                if self.go_declared:
                    print "Computer said Go."
                if len(playable_cards) == 0:
                    # Go
                    self.declare_go()
                else:
                    # prompt the user to enter a card
                    card = int(raw_input("Please select a card (1-"+str(len(playable_cards))+") to play."))
                    if card <= 0 or card > len(playable_cards):
                        raise ValueError
                    print "Selected card " + str(card) +  "."
                    self.play_card(playable_cards[card-1])
                break
            except ValueError:
                print "Invalid card number."

    def computer_play_cards(self):
        # get the cards that can be played
        playable_cards = self.get_playable_cards(self.hands[1])
        # if we can't play any cards, Go.
        if len(playable_cards) == 0:
            self.declare_go()
        else:
            # otherwise, pick a random card and play it
            self.play_card(playable_cards[0])

    def get_playable_cards(self, hand):
        # returns a subset of the cards that are allowed to be played, given the count
        playable_cards = []
        for c in hand.cards:
            if not c.played and self.count + c.value <= 31:
                playable_cards.append(c)
        return playable_cards

    # plays a card.
    def play_card(self, card):
        # extract the card from the hand and put it on the table
        self.table_cards.append(card)
        print "cards on table: ", str(self.table_cards)
        print "card just played: ", card
        card.played = True
        self.count += card.value
        say(str(self.count))
        self.num_cards_played += 1
        # score points
        # Fifteen and thirty-one
        if self.count == 15 or self.count == 31:
            self.game.update_score(self.player, 2)
            say("for two")
        # Pairs etc.
        self.table_score_pairs()
        # Runs etc.
        self.table_score_runs()
        # update the player
        if not self.go_declared:
            self.player = (self.player+1)%2

    # declares Go
    def declare_go(self):
        if self.go_declared:
            # go was already declared by the other player, so reset the table
            # and give yourself one point
            self.game.update_score(self.player, 1)
            self.reset_table()
        else:
            # we are the first ones to declare go, so declare it
            self.go_declared = True
            self.go_declared_player = self.player
        # update the player
        self.player = (self.player+1)%2


    def table_score_pairs(self):
        # look back and see how many pairs there were in a row
        num_pairs = 0
        paired_value = self.table_cards[-1].number
        for i in range(len(self.table_cards)-1,-1,-1):
            c = self.table_cards[i]
            if c.number == paired_value:
                num_pairs += 1
            else:
                break
        if num_pairs >= 2:
            self.game.update_score(self.player, math.factorial(num_pairs))
            say(str(num_pairs/2) + " pairs for " + str(math.factorial(num_pairs)))

    def table_score_runs(self):
        # look back and see if the last n cards constitute a run. Get the largest such n
        # first, bucket sort all the cards on the table
        buckets = {}
        for i in range(1, 14):
            buckets[i] = 0
        for c in self.table_cards:
            buckets[c.number] += 1
        # start with all the cards in the table, and see if we can make a run with them.
        # If so, return. If not, incrementally remove a card from the table and repeat.
        num_cards = len(self.table_cards)
        for i in range(len(self.table_cards)):
            # identify whether the counts are all 0s and 1s
            all_01s = True
            min_val = 15
            max_val = -1
            for j in range(1, 14):
                all_01s = all_01s and (buckets[j] == 0 or buckets[j] == 1)
                if buckets[j] == 1:
                    min_val = min(min_val, j)
                    max_val = max(max_val, j)
            # if not, we can't make a run with these cards
            if not all_01s:
                buckets[self.table_cards[i].number] -= 1
                num_cards -= 1
                continue
            # otherwise, see if the minimum and maximum values differ by the right amount
            if max_val - min_val + 1 == num_cards and num_cards >= 3:
                # we found a match
                self.game.update_score(self.player, num_cards)
                say("run of " + str(num_cards) + " for " + str(num_cards))
                return
            else:
                buckets[self.table_cards[i].number] -= 1
                num_cards -= 1
                continue






class Game(object):
    def __init__(self, interactive):
        self.interactive = interactive
        self.score = [0, 0]
        self.crib_player = 0

    def play(self):
        while not self.game_over():
            self.play_round()
            self.crib_player = (self.crib_player+1)%2

    # one round of a game
    def play_round(self):
        Round(self)

    # returns True if the game is over
    def game_over(self):
        return self.score[0] >= 121 or self.score[1] >= 121

    # updates the score
    def update_score(self, player, points):
        self.score[player] += points
        self.print_score()
        if self.game_over():
            # the player just won
            self.winner = player
            self.destruct()

    # wraps up the game
    def destruct(self):
        print "Player " + str(self.player+1) + " has won. Final score: ",
        print_score(self)

    # prints out the score
    def print_score(self):
        print "YOU: " + str(self.score[0]) + " - " + str(self.score[1]) + " :COMPUTER"


class Round(object):
    def __init__(self, game):
        self.game = game
        self.crib_player = self.game.crib_player
        self.play()

    def play(self):
        # print out the score to the player
        self.game.print_score()
        # shuffle the cards and deal them
        self.deck = Deck()
        # show the six cards to the player, and ask them to select cards to put in the crib.
        crib_cards = self.player_select_crib()
        crib_cards.extend(self.select_crib())
        self.deck.crib = Hand(crib_cards)
        # show the top card on the deck
        self.deck.show_top_card()
        # interactively play the cards
        Table(self.game, self, self.deck, self.crib_player).play_cards_interactive()
        # score the hands
        self.score_hands_interactive()
        # show the score at the end of the turn
        self.game.print_score()

    # ask the player to select two cards for the crib
    def player_select_crib(self):
        crib_cards = []
        # show the hand to the player and ask them to pick two cards
        print "Here are the cards in your hand. It is your",
        if self.crib_player == 1:
            print "opponent's",
        print "crib."
        while len(crib_cards) < 2:
            # from https://docs.python.org/2/tutorial/errors.html
            try:
                print self.deck.hands[0]
                card = int(raw_input("Please select a card (1-"+str(len(self.deck.hands[0].cards))+") to put in your crib."))
                if card <= 0 or card > 6:
                    raise ValueError
                if self.deck.hands[0].cards[card-1] in crib_cards:
                    raise ValueError
                crib_cards.append(self.deck.hands[0].cards.pop(card-1))
                print "Selected card " + str(card) +  "."
            except ValueError:
                print "Invalid card number."
        return crib_cards

    # computer program to select the crib
    def select_crib(self):
        # stub
        crib_cards = []
        crib_cards.append(self.deck.hands[1].cards.pop(0))
        crib_cards.append(self.deck.hands[1].cards.pop(1))
        return crib_cards

    # scores the hands
    def score_hands_interactive(self):
        if self.crib_player == 1:
            print "YOUR HAND..."
        else:
            print "YOUR OPPONENT'S HAND..."
        self.game.update_score((self.crib_player+1)%2, self.deck.hands[(self.crib_player+1)%2].score(self.deck.top_card))
        if self.crib_player == 0:
            print "YOUR HAND..."
        else:
            print "YOUR OPPONENT'S HAND..."
        self.game.update_score(self.crib_player, self.deck.hands[self.crib_player].score(self.deck.top_card))
        print "YOUR",
        if self.crib_player == 1:
            print "OPPONENT'S",
        print "CRIB..."
        self.game.update_score(self.crib_player, self.deck.crib.score(self.deck.top_card))

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


    def show_top_card(self):
        print "top card is: " + str(self.top_card)

    # string representation of a deck
    def __str__(self):
        string = ""
        string += "Player 1: " + str(self.hands[0]) + "\n"
        string += "Player 2: " + str(self.hands[1]) + "\n"
        string += "Top card: " + str(self.topcard) + "\n"
        string += "Crib: " + str(self.crib) + "\n"
        return string

    def __repr__(self):
        return str(self)



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

    def __repr__(self):
        return str(self)

def say(string):
    os.system("say '" + string + "'")


