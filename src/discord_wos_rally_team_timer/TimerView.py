import discord


import asyncio


class TimerView(discord.ui.View):
    def __init__(self, bot, group_name):
        super().__init__(timeout=None)
        self.bot = bot
        self.group_name = group_name

    @discord.ui.button(
        label="🔄 Neustart", style=discord.ButtonStyle.primary, custom_id="restart"
    )
    async def restart(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if self.group_name in self.bot.active_tasks:
            await interaction.response.send_message("⚠️ Läuft bereits!", ephemeral=True)
        else:
            await (
                interaction.response.defer()
            )  # Verhindert "Interaktion fehlgeschlagen"
            # Wir übergeben die aktuelle Nachricht zum Löschen
            from discord_wos_rally_team_timer.run_timer import run_timer

            asyncio.create_task(
                run_timer(interaction, self.group_name, old_msg=interaction.message)
            )

    @discord.ui.button(
        label="🛑 Stopp", style=discord.ButtonStyle.danger, custom_id="cancelled"
    )
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.group_name in self.bot.active_tasks:
            self.bot.active_tasks[self.group_name].cancel()
            await interaction.response.send_message("🛑 Gestoppt.", ephemeral=True)
