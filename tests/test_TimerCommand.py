import pytest
from unittest.mock import AsyncMock, MagicMock

from discord_wos_rally_team_timer.TimerCommand import TimerCommand
from discord_wos_rally_team_timer.teambot.group import Group
from discord_wos_rally_team_timer.teambot.player import Player


@pytest.fixture
def mock_bot():
    bot = MagicMock()
    bot.groups = []
    bot.active_tasks = {}
    return bot


@pytest.fixture
def mock_interaction(mock_bot):
    interaction = AsyncMock()
    interaction.client = mock_bot
    interaction.response.send_message = AsyncMock()
    return interaction


@pytest.mark.asyncio
async def test_add_player_creates_new_group(mock_interaction, mock_bot):
    command_group = TimerCommand(bot=mock_bot)

    # .callback nutzen, um die Funktion direkt aufzurufen
    await command_group.add.callback(
        command_group, mock_interaction, player="Wick", time=100, team="Alpha"
    )

    assert len(mock_bot.groups) == 1
    assert mock_bot.groups[0].name == "Alpha"
    assert mock_bot.groups[0].members[0].name == "Wick"


@pytest.mark.asyncio
async def test_add_player_sorting(mock_interaction, mock_bot):
    # WICHTIG: Sicherstellen, dass die Liste leer ist,
    # falls mock_bot von anderen Tests wiederverwendet wurde
    mock_bot.groups = []

    command_group = TimerCommand(bot=mock_bot)

    # Bestehende Gruppe mit einem langsamen Spieler vorbereiten
    group = Group("Alpha")
    group.members.append(Player("Langsam", 200, "Alpha"))
    mock_bot.groups.append(group)

    # Neuen schnelleren Spieler hinzufügen
    # (Wir nutzen hier 'Schnell', nicht 'Wick')
    await command_group.add.callback(
        command_group, mock_interaction, player="Schnell", time=50, team="Alpha"
    )

    # Prüfung der Sortierung: 200 > 50 -> Langsam (Index 0), Schnell (Index 1)
    assert len(mock_bot.groups[0].members) == 2
    assert mock_bot.groups[0].members[0].name == "Langsam"
    assert mock_bot.groups[0].members[1].name == "Schnell"


@pytest.mark.asyncio
async def test_update_non_existent_group(mock_interaction, mock_bot):
    command_group = TimerCommand(bot=mock_bot)

    # .callback nutzen
    await command_group.update.callback(
        command_group, mock_interaction, player="Wick", current_group="Ghost"
    )

    args, _ = mock_interaction.response.send_message.call_args
    assert "Group not found" in args[0]


@pytest.mark.asyncio
async def test_delete_specific_group(mock_interaction, mock_bot):
    command_group = TimerCommand(bot=mock_bot)
    mock_bot.groups = [Group("Alpha"), Group("Beta")]

    # .callback nutzen
    await command_group.delete.callback(command_group, mock_interaction, group="Alpha")

    assert len(mock_bot.groups) == 1
    assert mock_bot.groups[0].name == "Beta"
