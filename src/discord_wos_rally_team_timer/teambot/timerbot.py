import discord
from discord.ext import commands
from ..TimerCommand import TimerCommand


class TimerBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix="!", intents=intents)
        self.groups = []  # list of Groups
        self.active_tasks = {}

    async def setup_hook(self):
        self.tree.add_command(TimerCommand(name="timer", bot=self))
        await self.tree.sync()
        print(f"✅ Befehle für {self.user} synchronisiert.")
