import discord
from discord import app_commands
import asyncio

from .run_timer import run_timer
from .teambot.group import Group
from .teambot.player import Player


class TimerCommand(app_commands.Group):
    def __init__(self, bot: discord.Client, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot

    @app_commands.command(name="add", description="add a new player")
    async def add(
        self,
        interaction: discord.Interaction,
        player: str,
        time: int,
        team: str = "default",
    ):
        if not any(group.name == team for group in self.bot.groups):
            new_team = Group(team)
            self.bot.groups.append(new_team)
        group = next(
            (group for group in self.bot.groups if group.name == team))
        player = Player(player, time, team)
        group.members.append(player)
        group.members.sort(key=lambda player: player.time, reverse=True)
        await interaction.response.send_message(
            f"✅ {player} ({time}s) -> {team}", ephemeral=True
        )

    @app_commands.command(
        name="update", description="update a player"
    )
    async def update(
        self,
        interaction: discord.Interaction,
        player: str,
        current_group: str,
        new_time: int = None,
        target_group: str = None,
    ):
        if not any(group.name == current_group for group in self.bot.groups):
            return await interaction.response.send_message(
                "❌ Group not found", ephemeral=True
            )
        current_team = next(
            (group for group in self.bot.groups if group.name == current_group))
        member = next(
            (p for p in current_team.members if p.name.lower() == player.lower()), None)

        if not member:
            return await interaction.response.send_message(
                f"❌ {player} not found", ephemeral=True
            )

        if new_time is not None:
            member.time = new_time

        if target_group:
            current_team.remove(member)
            if not any(group.name == target_group for group in self.bot.groups):
                new_team = Group(target_group)
                self.bot.groups.append(new_team)
                new_team.members.append(member)
            else:
                target_team = next(
                    (group for group in self.bot.groups if group.name == target_group))
                target_team.members.append(member)
                target_team.members.sort(
                    key=lambda player: player.time, reverse=True)

        await interaction.response.send_message(
            f"🔄 {player} updated.", ephemeral=True
        )

    @app_commands.command(name="list", description="List all groups and members")
    async def list(self, interaction: discord.Interaction):
        if not self.bot.groups:
            return await interaction.response.send_message(
                "ℹ️ Keine Daten.", ephemeral=True
            )
        embed = discord.Embed(title="📋 Übersicht", color=discord.Color.blue())
        for g in self.bot.groups:
            txt = "\n".join([f"• {p.name}: {p.time}s" for p in g.members])
            embed.add_field(name=f"Gruppe: {g.name}",
                            value=txt or "Leer", inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="start", description="Timer starten")
    async def start(self, interaction: discord.Interaction, gruppe: str = "default"):
        asyncio.create_task(run_timer(interaction, gruppe))

    @app_commands.command(name="delete", description="remove configuration")
    async def delete(self, interaction: discord.Integration, group: str = None):
        if group:
            team = next(
                (team for team in self.bot.groups if team.name == group), None)
            if team is None:
                return await interaction.response.send_message(
                    f"❌ {group} not found", ephemeral=True
                )
            self.bot.groups.remove(team)
        else:
            self.bot.groups = []
