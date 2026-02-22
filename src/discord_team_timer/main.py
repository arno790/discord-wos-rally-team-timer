import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import os
from dotenv import load_dotenv

'''Blame AI for these code'''


class TimerBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix="!", intents=intents)
        self.groups = {}
        self.delays = {}
        self.active_tasks = {}

    async def setup_hook(self):
        self.tree.add_command(TimerGroup(name="timer"))
        await self.tree.sync()
        print(f"✅ Befehle für {self.user} synchronisiert.")


bot = TimerBot()


async def run_timer(interaction: discord.Interaction, g_name: str, old_msg=None):
    if g_name not in bot.groups or not bot.groups[g_name]:
        return

    players = list(bot.groups[g_name])
    pending = list(players)
    delay = bot.delays.get(g_name, 3)

    current = players[0]['time'] + delay
    stop_at = players[-1]['time'] - 2

    view = TimerView(bot, g_name)
    embed = discord.Embed(
        title=f"⏱️ Live-Timer: {g_name}", color=discord.Color.gold())

    # Nachricht erstellen oder updaten
    if interaction.response.is_done():
        # Falls durch Button-Neustart: Alte Nachricht löschen für Sauberkeit
        if old_msg:
            try:
                await old_msg.delete()
            except:
                pass
        msg = await interaction.channel.send(embed=embed, view=view)
    else:
        await interaction.response.send_message(f"🚀 Startet...", ephemeral=True)
        msg = await interaction.channel.send(embed=embed, view=view)

    bot.active_tasks[g_name] = asyncio.current_task()

    try:
        while current >= stop_at:
            embed.clear_fields()
            embed.add_field(name="⏲️ Countdown",
                            value=f"**{max(0, current)}s**", inline=True)

            status_list = []
            for p in players:
                if p in pending:
                    diff = current - p['time']
                    status = f"⏳ in {diff}s" if diff > 0 else "🔔 **JETZT**"
                    status_list.append(f"**{p['name']}**: {status}")
                else:
                    status_list.append(f"~~{p['name']}~~: ✅")

            embed.add_field(name="👥 Status", value="\n".join(
                status_list), inline=False)

            # Trigger (Nur interne Liste aktualisieren, keine Chat-Nachricht mehr)
            triggered = [p for p in pending if p['time'] == current]
            for p in triggered:
                pending.remove(p)

            await msg.edit(embed=embed, view=view)
            if not pending and current <= stop_at:
                break

            await asyncio.sleep(1)
            current -= 1

        embed.title = f"🏁 {g_name} Beendet"
        embed.color = discord.Color.green()
        for child in view.children:
            if child.label == "🛑 Stopp":
                child.disabled = True
        await msg.edit(embed=embed, view=view)

    except asyncio.CancelledError:
        embed.title = f"🛑 {g_name} Abgebrochen"
        embed.color = discord.Color.red()
        for child in view.children:
            if child.label == "🛑 Stopp":
                child.disabled = True
        await msg.edit(embed=embed, view=view)
    finally:
        if g_name in bot.active_tasks:
            del bot.active_tasks[g_name]

# --- 3. UI ---


class TimerView(discord.ui.View):
    def __init__(self, bot, g_name):
        super().__init__(timeout=None)
        self.bot = bot
        self.g_name = g_name

    @discord.ui.button(label="🔄 Neustart", style=discord.ButtonStyle.primary, custom_id="restart")
    async def restart(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.g_name in self.bot.active_tasks:
            await interaction.response.send_message("⚠️ Läuft bereits!", ephemeral=True)
        else:
            await interaction.response.defer()  # Verhindert "Interaktion fehlgeschlagen"
            # Wir übergeben die aktuelle Nachricht zum Löschen
            asyncio.create_task(
                run_timer(interaction, self.g_name, old_msg=interaction.message))

    @discord.ui.button(label="🛑 Stopp", style=discord.ButtonStyle.danger, custom_id="cancelled")
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.g_name in self.bot.active_tasks:
            self.bot.active_tasks[self.g_name].cancel()
            await interaction.response.send_message("🛑 Gestoppt.", ephemeral=True)

# --- 4. BEFEHLE ---


class TimerGroup(app_commands.Group):
    @app_commands.command(name="add", description="Spieler hinzufügen")
    async def add(self, interaction: discord.Interaction, user: str, zeit: int, gruppe: str = "Standard"):
        if gruppe not in bot.groups:
            bot.groups[gruppe] = []
            bot.delays[gruppe] = 3
        bot.groups[gruppe].append({"name": user, "time": zeit})
        bot.groups[gruppe].sort(key=lambda x: x['time'], reverse=True)
        await interaction.response.send_message(f"✅ {user} ({zeit}s) -> {gruppe}", ephemeral=True)

    @app_commands.command(name="update", description="Zeit ändern oder Gruppe verschieben")
    async def update(self, interaction: discord.Interaction, user: str, aktuelle_gruppe: str, neue_zeit: int = None, ziel_gruppe: str = None):
        if aktuelle_gruppe not in bot.groups:
            return await interaction.response.send_message("❌ Gruppe nicht gefunden.", ephemeral=True)
        player = next(
            (p for p in bot.groups[aktuelle_gruppe] if p['name'].lower() == user.lower()), None)
        if not player:
            return await interaction.response.send_message(f"❌ {user} nicht gefunden.", ephemeral=True)
        bot.groups[aktuelle_gruppe].remove(player)
        target = ziel_gruppe if ziel_gruppe else aktuelle_gruppe
        if target not in bot.groups:
            bot.groups[target] = []
            bot.delays[target] = 3
        if neue_zeit is not None:
            player['time'] = neue_zeit
        bot.groups[target].append(player)
        bot.groups[target].sort(key=lambda x: x['time'], reverse=True)
        await interaction.response.send_message(f"🔄 {user} aktualisiert.", ephemeral=True)

    @app_commands.command(name="list", description="Alle Gruppen anzeigen")
    async def list(self, interaction: discord.Interaction):
        if not bot.groups:
            return await interaction.response.send_message("ℹ️ Keine Daten.", ephemeral=True)
        embed = discord.Embed(title="📋 Übersicht", color=discord.Color.blue())
        for g, p_list in bot.groups.items():
            txt = "\n".join([f"• {p['name']}: {p['time']}s" for p in p_list])
            embed.add_field(name=f"Gruppe: {g}",
                            value=txt or "Leer", inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="start", description="Timer starten")
    async def start(self, interaction: discord.Interaction, gruppe: str = "Standard"):
        asyncio.create_task(run_timer(interaction, gruppe))

    @app_commands.command(name="delete", description="remove configuration")
    async def delete(self, interaction: discord.Integration, group: str = None):
        if group:
            bot.groups.pop(group, None)
        else:
            bot.groups = {}


# --- 5. START ---
if __name__ == "__main__":
    load_dotenv()
    bot.run(os.getenv('DISCORD_TOKEN'))
