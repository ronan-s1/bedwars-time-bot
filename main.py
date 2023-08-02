import asyncio
import os
import discord
import csv
import pandas as pd
from datetime import datetime, timedelta
from discord.ext import commands
from tabulate import tabulate
from dotenv import find_dotenv, load_dotenv

DOT_ENV_PATH = find_dotenv()
load_dotenv(DOT_ENV_PATH)

WINS_CSV = "wins.csv"
TOKEN = str(os.getenv("TOKEN"))
CHANNEL_ID = 829470513734484031
ROLE_NAME = "Bed Bugs"

intents = discord.Intents.all()
intents.messages = True

bot = commands.Bot(command_prefix="$", intents=intents)

@bot.command(name="add")
async def add(ctx, wins: int):
    if not isinstance(wins, int) or wins <= 0:
        await ctx.send("wins must be a positive whole number.")
        return

    current_date = datetime.now().strftime("%d %b %Y")
    df = pd.read_csv(WINS_CSV)

    if current_date in df["date"].values:
        await ctx.send(f"{current_date} already exists in the records. Can't add again.")
    else:
        with open(WINS_CSV, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([current_date, wins])

        df = pd.read_csv(WINS_CSV)
        max_wins = df["wins"].max()

        await ctx.send(f"**Today's wins:** {wins}\n**Date:** {current_date}\n\n**Highest wins so far:** {max_wins}")


@bot.command(name="wins")
async def wins(ctx):
    df = pd.read_csv(WINS_CSV)

    if df.empty:
        response = "No wins recorded yet."
    else:
        table = tabulate(df, headers="keys", tablefmt="simple_grid", showindex=False)
        response = f"**Wins History:**\n```{table}```"
    await ctx.send(response)
    

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")
    await schedule_mentions()


async def schedule_mentions():
    while True:
        now = datetime.now()
        target_time = now.replace(hour=21, minute=15, second=0, microsecond=0)

        if now > target_time:
            target_time += timedelta(days=1)

        # Calculate the time until the target time
        delta = target_time - now
        await asyncio.sleep(delta.total_seconds())

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

        # Mention the role
        await channel.send(f"{role.mention} TIME FOR BEDWARS ⏰")

bot.run(TOKEN)
