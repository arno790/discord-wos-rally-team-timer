import os
from dotenv import load_dotenv

from discord_wos_rally_team_timer.teambot import timerbot


if __name__ == "__main__":
    bot = timerbot.TimerBot()
    load_dotenv()
    bot.run(os.getenv("DISCORD_TOKEN"))
