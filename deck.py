import random

from poker_hand import *


class Deck:
    def __init__(self):
        self.cards = [Card(rank, suit) for suit in SUITS for rank in RANKS]
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self, n: int) -> List[Card]:
        return [self.cards.pop() for _ in range(n)]

    def reset(self):
        self.cards = [Card(rank, suit) for suit in SUITS for rank in RANKS]
        self.shuffle()


if __name__ == "__main__":
    for i in range(10000):
        deck = Deck()
        hand = deck.deal(2)  # 玩家手牌
        community = deck.deal(5)  # 公共牌
        full_hand = hand + community
        poker_hand = PokerHand(full_hand)
        if poker_hand.hand_type > HandType.FULL_HOUSE:
            print(poker_hand, end="\n\n")
