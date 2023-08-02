import discord
import asyncio
import os
from datetime import datetime, timedelta


TOKEN = os.getenv("TOKEN")
CHANNEL_ID = 829470513734484031
ROLE_NAME = "Bed Bugs"

intents = discord.Intents.default()
intents.messages = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")
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

        channel = client.get_channel(CHANNEL_ID)

        if not channel:
            print(f"Channel with ID {CHANNEL_ID} not found.")
            return

        for guild in client.guilds:
            role = discord.utils.get(guild.roles, name=ROLE_NAME)
            if role:
                break

        if not role:
            print(f"Role '{ROLE_NAME}' not found in any of the guilds.")
            return

        # Mention the role
        await channel.send(f"{role.mention} NOW!")


client.run(TOKEN)
