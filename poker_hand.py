from collections import Counter
from enum import IntEnum
from functools import total_ordering
from typing import List

# 定义扑克牌花色和点数
SUITS = ['♠', '♥', '♦', '♣']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
RANK_VALUES = {rank: i for i, rank in enumerate(RANKS, start=2)}

HAND_TYPE_DESCRIPTIONS = {
    10: ("Royal Flush", "皇家同花顺"),
    9: ("Straight Flush", "同花顺"),
    8: ("Four of a Kind", "四条"),
    7: ("Full House", "葫芦"),
    6: ("Flush", "同花"),
    5: ("Straight", "顺子"),
    4: ("Three of a Kind", "三条"),
    3: ("Two Pair", "两对"),
    2: ("One Pair", "一对"),
    1: ("High Card", "高牌")
}


class HandType(IntEnum):
    HIGH_CARD = 1
    ONE_PAIR = 2
    TWO_PAIR = 3
    THREE_OF_A_KIND = 4
    STRAIGHT = 5
    FLUSH = 6
    FULL_HOUSE = 7
    FOUR_OF_A_KIND = 8
    STRAIGHT_FLUSH = 9
    ROYAL_FLUSH = 10

    def __str__(self):
        eng, chi = HAND_TYPE_DESCRIPTIONS[self.value]
        return f"{eng} ({chi})"


@total_ordering
class Card:
    def __init__(self, rank: str, suit: str):
        self.rank = rank
        self.suit = suit
        self.value = RANK_VALUES[rank]

    def __str__(self):
        return f"{self.suit}{self.rank}"

    def __repr__(self):
        return str(self)

    def __eq__(self, other: 'Card'):
        return self.value == other.value

    def __lt__(self, other: 'Card'):
        return self.value < other.value


@total_ordering
class PokerHand:
    def __init__(self, cards: List[Card]):
        if len(cards) != 7:
            raise ValueError("PokerHand must contain exactly 7 cards.")
        self.cards: List[Card] = sorted(cards.copy(), key=lambda c: c.value, reverse=True)
        self.selected: List[Card] = self.cards.copy()
        self.hand_type: HandType = HandType.HIGH_CARD
        self.evaluate_hand()

    def has_flush(self) -> bool:
        suits = [card.suit for card in self.selected]
        suit_counts = Counter(suits)
        for suit, count in suit_counts.items():
            if count >= 5:
                self.selected = [card for card in self.selected if card.suit == suit]
                return True
        return False

    def has_straight(self) -> bool:
        unique_cards = []
        seen = set()
        for card in self.selected:
            if card.value not in seen:
                seen.add(card.value)
                unique_cards.append(card)

        unique_cards.append(unique_cards[0])  # 处理 A2345 顺子

        for i in range(len(unique_cards) - 4):
            diff = unique_cards[i].value - unique_cards[i + 4].value
            if diff % 13 == 4:
                self.selected = unique_cards[i:i + 5]
                return True

        return False

    def evaluate_hand(self):
        # 先判断同花顺 / 同花 / 顺子
        if self.has_flush():
            if self.has_straight():
                self.hand_type = HandType.ROYAL_FLUSH if self.selected[0].value == 14 else HandType.STRAIGHT_FLUSH
            else:
                self.hand_type = HandType.FLUSH
            return

        if self.has_straight():
            self.hand_type = HandType.STRAIGHT
            return

        # 统计点数出现次数
        value_to_cards = {}
        for card in self.selected:
            value_to_cards.setdefault(card.value, []).append(card)

        rank_counts = Counter(card.value for card in self.selected)
        count_value_pairs = sorted(
            ((cnt, val) for val, cnt in rank_counts.items()),
            reverse=True
        )

        # 根据 count-value 重新编排所有牌
        self.selected = [value_to_cards[val].pop() for cnt, val in count_value_pairs for _ in range(cnt)]
        counts = [cnt for cnt, _ in count_value_pairs]

        # 判断非顺子/同花牌型
        if counts[0] == 4:
            self.hand_type = HandType.FOUR_OF_A_KIND
            if self.selected[-1] > self.selected[4]:
                # [:4] 是四条，[-1] 是最大 kicker
                self.selected = self.selected[:4] + [self.selected[-1]]
                return
        elif counts[0] == 3 and counts[1] >= 2:
            self.hand_type = HandType.FULL_HOUSE
        elif counts[0] == 3:
            self.hand_type = HandType.THREE_OF_A_KIND
        elif counts[0] == 2 and counts[1] == 2:
            self.hand_type = HandType.TWO_PAIR
        elif counts[0] == 2:
            self.hand_type = HandType.ONE_PAIR
        else:
            self.hand_type = HandType.HIGH_CARD
        self.selected = self.selected[:5]

    def __lt__(self, other: 'PokerHand'):
        return self.hand_type < other.hand_type and self.selected < other.selected

    def __eq__(self, other: 'PokerHand'):
        return self.hand_type == other.hand_type and self.selected == other.selected

    def __str__(self):
        return (
            f"All Cards: {self.cards}\n"
            f"Hand Type: {self.hand_type}\n"
            f"Best Five: {self.selected}"
        )


# 测试代码
if __name__ == "__main__":
    hand1 = PokerHand([
        Card('A', '♠'), Card('A', '♥'), Card('5', '♦'),
        Card('5', '♣'), Card('A', '♠'), Card('2', '♥'), Card('3', '♣')
    ])
    hand2 = PokerHand([
        Card('A', '♦'), Card('2', '♠'), Card('5', '♥'),
        Card('6', '♦'), Card('7', '♣'), Card('9', '♥'), Card('10', '♠')
    ])

    print(hand1 > hand2)  # True
    print(hand1)  # 打印牌面信息
