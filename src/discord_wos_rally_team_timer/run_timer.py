from .TimerView import TimerView
import discord
import asyncio


async def run_timer(interaction: discord.Interaction, group_name: str, bot, old_msg=None):
    if not any(group.name == group_name for group in bot.groups):
        return

    team = next((group for group in bot.groups if group.name == group_name))
    players = team.members
    pending = list(players)  # new a object not a name
    delay = team.delay

    current = players[0].time + delay
    stop_at = players[-1].time - 2

    view = TimerView(bot, group_name)
    embed = discord.Embed(
        title=f"⏱️ Live-Timer: {group_name}", color=discord.Color.gold()
    )

    # create and update messages
    if interaction.response.is_done():
        # If button rerun pressed: delete old messages
        if old_msg:
            try:
                await old_msg.delete()
            except:
                pass
        msg = await interaction.channel.send(embed=embed, view=view)
    else:
        await interaction.response.send_message(f"🚀 Startet...", ephemeral=True)
        msg = await interaction.channel.send(embed=embed, view=view)

    bot.active_tasks[group_name] = asyncio.current_task()

    try:
        while current >= stop_at:
            embed.clear_fields()
            embed.add_field(
                name="⏲️ Countdown", value=f"**{max(0, current)}s**", inline=True
            )

            status_list = []
            for player in players:
                if player in pending:
                    diff = current - player.time
                    status = f"⏳ in {diff}s" if diff > 0 else "🔔 **JETZT**"
                    status_list.append(f"**{player.name}**: {status}")
                else:
                    status_list.append(f"~~{player.name}~~: ✅")

            embed.add_field(
                name="👥 Status", value="\n".join(status_list), inline=False
            )

            # Trigger update list
            triggered = [
                player for player in pending if player.time == current]
            for player in triggered:
                pending.remove(player)

            await msg.edit(embed=embed, view=view)
            if not pending and current <= stop_at:
                break

            await asyncio.sleep(1)
            current -= 1

        embed.title = f"🏁 {group_name} Beendet"
        embed.color = discord.Color.green()
        for child in view.children:
            if child.label == "🛑 Stopp":
                child.disabled = True
        await msg.edit(embed=embed, view=view)

    except asyncio.CancelledError:
        embed.title = f"🛑 {group_name} Abgebrochen"
        embed.color = discord.Color.red()
        for child in view.children:
            if child.label == "🛑 Stopp":
                child.disabled = True
        await msg.edit(embed=embed, view=view)
    finally:
        if group_name in bot.active_tasks:
            del bot.active_tasks[group_name]
