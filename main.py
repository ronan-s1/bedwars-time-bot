import asyncio
import io
import os
import discord
import csv
import random
import pandas as pd
from datetime import datetime, timedelta
from discord.ext import commands
from dotenv import find_dotenv, load_dotenv
import plotly.graph_objects as go

# DING DING DING
BEDWARS_TIME = "22:00"
HOURS, MINUTES = map(int, BEDWARS_TIME.split(":"))

# Getting details for running bot
load_dotenv(find_dotenv())
TOKEN = os.getenv("TOKEN")
CHANNEL_ID = 829470513734484031
ROLE_NAME = "Bed Bugs"

# Other globals
WINS_CSV = "wins.csv"
BW_TIME_STRINGS = ["BEDS 🛏️ ROCKING 🪨 TIME ⏰", "GET ON BEDWARS NOW ❗", "BED 🛏️ BUGS 🐛 ASSEMBLE ❗", "TIME FOR BEDWARS ⏰"]

# intents to get messages
intents = discord.Intents.all()
intents.messages = True

bot = commands.Bot(command_prefix="$", intents=intents)
bot.remove_command("help")


help_message = """
- `$add <wins>`: Record the number of wins for today.
- `$wins`: Show wins history.
- `$stats`: Show wins stats.
- `$help`: Show this help message.

- `souce:` <https://github.com/ronan-s1/bedwars-time-bot>
"""

@bot.command(name="help")
async def help_command(ctx):
    await ctx.send(help_message)


@bot.command(name="add")
async def add(ctx, wins):
    win_string = ""
    df = pd.read_csv(WINS_CSV)
    max_wins = df["wins"].max()

    # check if valid number
    try:
        wins = int(wins)
        if wins < 0:
            raise ValueError
        elif wins > max_wins:
            win_string = "NEW RECORD BABY OHH YEAHHH"
            max_wins = wins
        elif wins >= 3:
            win_string = "YOOOOOOOO"
        elif wins > 1:
            win_string = "sheesh"
        elif wins > 0:
            win_string = "mid"
        elif wins == 0:
            win_string = "bruh"

    except ValueError:
        await ctx.send("must enter a positive whole number.")
        return

    current_date = datetime.now().strftime("%d %b %Y")

    # if same adding multiple wins on same date just override
    if current_date in df["date"].values:
        df.loc[df["date"] == current_date, "wins"] = wins
        df.to_csv(WINS_CSV, index=False)
        await ctx.send(f"**{win_string}**\n\n**Today's wins (updated):** {wins}\n**Date:** {current_date}\n\n**Highest wins so far:** {max_wins}")
    else:
        with open(WINS_CSV, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([current_date, wins])
        await ctx.send(f"**{win_string}**\n\n**Today's wins:** {wins}\n**Date:** {current_date}\n\n**Highscore:** {max_wins}")

# add wins to csv (not bothered to create a db)
@bot.command(name="wins")
async def wins(ctx):
    df = pd.read_csv(WINS_CSV)

    if df.empty:
        response = "No wins recorded yet."
    else:
        response = f"**Wins History:**\n```{df.to_markdown(index=False)}```"
    await ctx.send(response)

# create a chart for wins
@bot.command(name="stats")
async def chart(ctx):
    loading_message = await ctx.send("Loading...")

    df = pd.read_csv(WINS_CSV)

    if df.empty:
        await ctx.send("No wins recorded yet.")
        return

    average_wins = df["wins"].mean()
    max_wins = df["wins"].max()

    # Create the line chart and save in byte
    fig = go.Figure(data=go.Scatter(x=df["date"], y=df["wins"], mode="lines"))
    fig.update_layout(title="Wins Chart", xaxis_title="Date", yaxis_title="Wins")
    chart_bytes = fig.to_image(format="png")

    # Send the chart image and average wins to Discord
    chart_file = discord.File(io.BytesIO(chart_bytes), filename="wins_chart.png")

    await loading_message.delete()
    await ctx.send("**Wins Chart:**")
    await ctx.send(file=chart_file)
    await ctx.send(f"**Average wins:** {average_wins:.2f}\n**Highscore:** {max_wins}")


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await schedule_mentions()


async def schedule_mentions():
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print(f"Channel with ID {CHANNEL_ID} not found.")
        return

    for guild in bot.guilds:
        role = discord.utils.get(guild.roles, name=ROLE_NAME)
        if role:
            break

    if not role:
        print(f"Role '{ROLE_NAME}' not found in any server.")
        return

    if BEDWARS_TIME != "21:15":
        await channel.send(f"{role.mention} **NOTICE:**\nBedwars will now commence at **{BEDWARS_TIME}**, apologies for any inconvenience.")

    while True:
        # setting time to @
        now = datetime.now()
        target_time = now.replace(hour=HOURS, minute=MINUTES, second=0, microsecond=0)

        # If time has passed, set for tomorrow
        if now > target_time:
            target_time += timedelta(days=1)

        # Calculate the time until the target time
        delta = target_time - now
        await asyncio.sleep(delta.total_seconds())

        # CALL BED BUGS
        await channel.send(f"{role.mention} {random.choice(BW_TIME_STRINGS)}")


bot.run(TOKEN)
