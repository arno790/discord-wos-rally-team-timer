from .player import Player


class Group:
    def __init__(self, name: str, members: list[Player] = None, delay: int = 3):
        self.name = name
        self.members = members if members is not None else []
        self.delay = delay
