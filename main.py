# main.py

from agent import Player
from game import Game


def main():
    players = [Player("Alice"), Player("Bob"), Player("C")]
    game = Game(players)
    game.minimum_call = 20
    game_loop(game)


def game_loop(game: Game):
    """
    主游戏流程：开始新回合并进入下注循环。
    """
    game.start_new_round()
    game.show_players()

    print("\n=== 开始下注环节 ===")

    while True:
        for player in game:
            if game.settle_round():
                return
            if player.folded:
                continue
            if player.turn_bet == game.minimum_call and player.acted:
                game.advance_stage()
                break
            while not handle_action(game, player):
                pass


def handle_action(game: Game, player: Player) -> bool:
    """
    处理玩家输入并执行相应操作。
    :return: 若操作成功返回 True，否则 False（将再次请求输入）
    """
    command = input(f"{player.name} 的操作（allin / bet X / call / check / fold / info）：").strip().lower()

    if command.startswith("bet "):
        try:
            amount = int(command.split()[1])
            return game.record_bet(*player.bet(amount, game.minimum_call))
        except (IndexError, ValueError):
            print("请输入有效的下注金额，例如：bet 50")
            return False

    elif command == "allin":
        return game.record_bet(*player.allin())

    elif command == "call":
        return game.record_bet(*player.call(game.minimum_call))

    elif command == "check":
        if game.minimum_call > 0:
            game.prompt_retry(player)
            return False
        player.check()
        print(f"{player.name} 选择过牌")
        return True

    elif command == "fold":
        game.record_folded(player.fold())
        print(f"{player.name} 弃牌")
        return True

    elif command == "info":
        print(player)
        return False

    else:
        print("无效命令，请重新输入。")
        return False


if __name__ == "__main__":
    main()
