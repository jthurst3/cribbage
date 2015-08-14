// cribbageAI.js
// Javascript functions to play Cribbage
// J. Hassler Thurston
// 22 April 2014
// edited 14 August 2015

// calculates the number of points from a given set of cards (assuming cards are in hand/crib), and the top card on the deck
function get_score(cards, starter) {
	/*
	scores are calculated based on "tricks" we can play with the cards
	tricks are according to the rules given by the American Cribbage Congress (http://www.cribbage.org/rules/rule1.asp#section7)
	SUMMARY OF TRICKS:
			- fifteen for 2 (get 2 points for having sums of cards add up to 15)
			- pair for 2 (get 2 points for having 2 of the same card)
			- three of a kind for 6 (get 6 points for having 3 of the same card)
			- four of a kind for 12 (get 12 points for having 4 of the same card)
			- run of n for n (get n points for having n consecutive cards in hand, e.g. 4 points for 8,9,10,J)
			- flush for n (get n points for having all cards in hand being of the same suit)
			- his knobs for 1 (get 1 point if hand has a Jack of the same suit as starter card)
	SUMMARY OF SCORING ALGORITHM:
			- sort the cards into ascending order
			- run through the sorted list of cards, keeping track of which tricks can be earned
    NOTE: As of August 14, 2015, this is a very unoptimized version of an algorithm. Once we get the cribbage AI working, we'll go back and modify the algorithm to make it more efficient.
	*/

    var score = 0;
    // sort the cards
    var allcards = cards.slice(0);
    allcards.push(starter);
	allcards.sort(function(a, b) {return a[0] - b[0]});
    console.log(cards, starter);
    var buckets = get_buckets(allcards);
    // compute the fifteens
    score += compute_fifteens(allcards);
    // compute pairs (NOTE: implicitly does three/four of a kind)
    score += compute_pairs(buckets);
    // compute runs
    score += compute_runs(buckets);
    // compute flushes
    score += compute_flushes(cards, starter);
    // compute his knobs
    score += compute_knobs(cards, starter);
    // return the score
    return score;


};

// compute fifteens by dynamic programming
var compute_fifteens = function(allcards) {
    // create a 2D array where each entry represents the number of combinations
    // of cards 1...i that sum to j
    var T = [];
    T.push(new Array(16));
    for(var j = 0; j < 16; j++) T[0][j] = 0;
    T[0][cardvalue(allcards[0])]++;
    for(var i = 1; i < allcards.length; i++) {
        var newarr = [];
        var val = cardvalue(allcards[i]);
        for(var j = 0; j < 16; j++) {
            // T[i,j] = T[i-1,j] + T[i-1, j-V[i]]
            var number = T[i-1][j];
            if(T[i-1][j-val]) number += T[i-1][j-val];
            newarr.push(number);
        }
        // T[i,V[i]]++
        newarr[val]++;
        T.push(newarr);
    }
    return 2* T[allcards.length-1][15];
};

// computes the number of pairs of cards in a hand
var compute_pairs = function(buckets) {
    var pairs = 0;
    for(var i = 0; i < buckets.length; i++) {
        pairs += buckets[i].length * (buckets[i].length-1);
    }
    return pairs;
};

// computes the number of runs of 3 or more exist in a hand
var compute_runs = function(buckets) {
    // loop through the buckets, computing the number of combinations of runs exist for a given run sequence
    var score = 0;
    var count = 0;
    var combos = 1;
    for(var i = 0; i < buckets.length; i++) {
        if(buckets[i].length == 0) {
            // increment the score, we've reached the end of a run
            if(count >= 3) score += count * combos;
            // reset the count and combo variables
            count = 0;
            combos = 1;
        }
        else {
            // we're still in a run, so update the count and combo variables
            count++;
            combos *= buckets[i].length;
        }
    }
    // if we've ended with a run, count that run as well
    if(count >= 3) score += count * combos;
    return score;
};

// computes whether we have a flush
var compute_flushes = function(cards, starter) {
    // NOTE: requires the hand to have at least one card in it
    var suit = cards[0][1];
    for(var i = 1; i < cards.length; i++) {
        if(cards[i][1] != suit) return 0;
    }
    // if we've gotten here, all the cards in the hand are of the same suit.
    // now we just need to check whether the starter card is of the same suit.
    if(starter[1] == suit) return cards.length + 1;
    else return cards.length;
};

// computes whether we can declare his knobs
// His knobs: When you have a Jack of the same suit in your hand as the starter card.
var compute_knobs = function(cards, starter) {
    var suit = starter[1];
    for(var i = 0; i < cards.length; i++) {
        if(cards[i][0] == 11 && cards[i][1] == suit) return 1;
    }
    return 0;
};

// groups cards into buckets, sorted by the card numbers
// NOTE: requires the cards in the hand to be sorted by number.
var get_buckets = function(cards) {
    var arr = [];
    var num = 0;
    for(var i = 1; i < 14; i++) {
        var bucket = [];
        while(num < cards.length && cards[num][0] == i) {
            bucket.push(cards[num]);
            num++;
        }
        arr.push(bucket);
    }
    return arr;
};





// computes the numeric value of the given card
// NOTE: cards are 2-tuples, the first element being the number, and
// the second number being the suit
// NOTE: Aces are value 1 by default
var cardvalue = function(card) {
    return Math.min(card[0], 10);
};


// TESTS
// creates a deck of 52 cards
var initialize_deck = function() {
    var deck = [];
    var suits = ['C','S','D','H'];
    for(var s = 0; s < suits.length; s++) {
        for(var i = 1; i <= 13; i++) {
            deck.push([i,suits[s]]);
        }
    }
    return deck;
};

// extracts a random card from the deck and removes it.
var extract_random_card = function(deck) {
    var index = Math.floor(Math.random() * deck.length);
    return deck.splice(index, 1)[0];
};

// returns an array whose first element is a 4-card hand, and whose second
// element is the "top card" on the deck.
var initialize_hand = function(deck) {
    var d = deck.slice(0);
    // pick 4 random cards for the hand, and 1 as the top card
    // NOTE: requires the deck to have >= 5 cards in it.
    var hand = [];
    for(var i = 0; i < 4; i++) {
        hand.push(extract_random_card(d));
    }
    hand.sort(function(a,b) { return a[0] - b[0]});
    return [hand, extract_random_card(d)];
};

// initialize the deck of cards
var deck = initialize_deck();

// run a number of random tests to see if functions are working
var test = function () {
    for(var i = 0; i < 1000; i++) {
        var random_hand = initialize_hand(deck);
        var hand = random_hand[0];
        var starter = random_hand[1];
        console.log(get_score(hand, starter));
    };
};

console.log(deck);
test();





