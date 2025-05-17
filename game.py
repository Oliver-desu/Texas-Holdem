from enum import Enum

from agent import Player
from deck import *


class Stage(Enum):
    PRE_FLOP = 0
    FLOP = 1
    TURN = 2
    RIVER = 3
    SHOWDOWN = 4

    def to_str(self) -> str:
        return _STAGE_LABELS.get(self, "未知阶段")


# 静态映射：游戏阶段的中英文标签
_STAGE_LABELS = {
    Stage.PRE_FLOP: "翻牌前（Pre-flop）",
    Stage.FLOP: "翻牌（Flop）",
    Stage.TURN: "转牌（Turn）",
    Stage.RIVER: "河牌（River）",
    Stage.SHOWDOWN: "摊牌（Showdown）",
}


class Game:
    def __init__(self, players: List[Player]):
        """
        初始化一局游戏。
        :param players: 玩家列表，至少需要 2 人
        """
        if len(players) < 2:
            raise ValueError("需要至少两名玩家")
        self.deck = Deck()
        self.players: List[Player] = players
        self.folded_players: List[Player] = []
        self.dealer_index = 0
        self.current_player_index = self.dealer_index

        self.stage: Stage = Stage.PRE_FLOP
        self.community_cards: List[Card] = []
        self.minimum_call = 0
        self.pot = 0

    def __iter__(self):
        return self

    def __next__(self):
        index = self.current_player_index
        self.current_player_index = (index + 1) % len(self.players)
        return self.players[index]

    def start_new_round(self):
        """
        开始新的一轮游戏，重置牌堆、发手牌并设定庄家。
        """
        self.deck.reset()
        self.folded_players = []
        self.dealer_index = (self.dealer_index + 1) % len(self.players)
        self.current_player_index = self.dealer_index
        self.stage = Stage.PRE_FLOP
        self.community_cards = []
        self.minimum_call = 0
        self.pot = 0

        for player in self.players:
            player.reset_for_new_round()
            player.receive_cards(self.deck.deal(2))

        print("\n=== 新的一轮开始 ===")
        print(f"本轮庄家：{self.players[self.dealer_index].name}")

    def advance_stage(self) -> bool:
        """
        推进到下一个阶段（翻牌 / 转牌 / 河牌），发放对应的公共牌并重置下注记录。
        """
        if self.stage == Stage.SHOWDOWN:
            return False
        self.stage = Stage(self.stage.value + 1)

        # 发放公共牌
        if self.stage == Stage.FLOP:
            self.community_cards += self.deck.deal(3)
        elif self.stage in {Stage.TURN, Stage.RIVER}:
            self.community_cards += self.deck.deal(1)

        print(f"\n{self.stage.to_str()} - 公共牌：{self.display_community_cards()}")

        # 重置当前轮下注信息
        self.minimum_call = 0
        for player in self.players:
            player.reset_for_new_turn()
        return True

    def record_folded(self, player: Player):
        """记录玩家弃牌。"""
        self.folded_players.append(player)

    def settle_round(self) -> bool:
        active_players = len(self.players) - len(self.folded_players)
        return active_players == 1 or self.stage == Stage.SHOWDOWN

    def record_bet(self, player: Player, actual_bet: int, total_bet: int) -> bool:
        """
        记录一次有效下注，更新底池与最低跟注金额。

        :param player: 下注的玩家
        :param actual_bet: 实际下注金额（可能为全下）
        :param total_bet: 玩家在本轮的累计下注（用于更新 minimum_call）
        :return: 是否成功记录（无效下注会提示重试）
        """
        if actual_bet is None:
            self.prompt_retry(player)
            return False

        self.pot += actual_bet
        self.minimum_call = max(self.minimum_call, total_bet)

        print(f"{player.name} 下注 {actual_bet} 筹码，剩余筹码：{player.chips}，本轮最低下注提升至 {self.minimum_call}")
        return True

    def prompt_retry(self, player: Player):
        """
        提示玩家当前下注不足并需重新操作。
        """
        required = self.minimum_call - player.turn_bet
        print(f"下注失败，当前最低下注为 {self.minimum_call}，你已下注 {player.turn_bet}，仍需 {required}，请重新操作。")

    def display_community_cards(self) -> str:
        """
        返回当前公共牌的字符串表示。
        """
        return " ".join(str(card) for card in self.community_cards)

    def show_players(self):
        """
        显示所有玩家的当前状态。
        """
        print("\n--- 玩家信息 ---")
        for player in self.players:
            print(player)
