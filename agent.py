# agent.py
from typing import List

from poker_hand import Card


class Player:
    def __init__(self, name: str, chips: int = 1000):
        """
        初始化玩家对象。
        :param name: 玩家姓名
        :param chips: 初始筹码数，默认值为 1000
        """
        self.name = name
        self.chips = chips
        self.hand: List[Card] = []
        self.round_bet = 0  # 本回合总下注（从发牌到摊牌）
        self.turn_bet = 0  # 当前轮下注（如 pre-flop/flop/turn/river）
        self.folded = False

    def receive_cards(self, cards: List[Card]):
        """
        接收两张手牌。
        """
        self.hand = cards

    def bet(self, amount: int, minimum_call: int = 0):
        """
        执行下注操作。
        - 若下注不足以跟注 minimum_call，且不是全下，则视为无效。
        - 若下注金额超过玩家现有筹码，则自动全下。

        :param amount: 想下注的筹码数
        :param minimum_call: 当前最低跟注金额
        :return: (Player, 实际下注金额, 当前轮总下注)，若无效下注则返回 (Player, None, None)
        """
        if amount < self.chips and amount + self.turn_bet < minimum_call:
            return self, None, None

        actual = min(amount, self.chips)
        self.chips -= actual
        self.round_bet += actual
        self.turn_bet += actual
        return self, actual, self.turn_bet

    def call(self, minimum_call: int):
        """
        跟注操作。
        """
        return self.bet(minimum_call - self.turn_bet, minimum_call)

    def allin(self):
        """
        全下操作。
        """
        return self.bet(self.chips)

    def fold(self):
        """
        弃牌操作。
        """
        self.folded = True

    def reset_for_new_round(self):
        """
        新回合开始时重置状态（清空手牌与下注记录）。
        """
        self.hand = []
        self.round_bet = 0
        self.turn_bet = 0
        self.folded = False

    def reset_for_new_turn(self):
        """
        每轮开始前重置当前轮下注。
        """
        self.turn_bet = 0

    def __str__(self):
        """
        返回玩家当前状态的字符串描述。
        """
        hand_str = " ".join(str(card) for card in self.hand) if self.hand else "No cards"
        return (
            f"{self.name}: {hand_str} | Chips: {self.chips} | "
            f"Round Bet: {self.round_bet} | Folded: {self.folded}"
        )
