import discord
from discord.ext import tasks
from datetime import datetime, timedelta
import mariadb
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_latest_player_count():
    try:
        conn = mariadb.connect(
            user=os.environ.get("DB_USER", "user"), 
            password=os.environ.get("DB_PASSWORD", "pass"),
            host=os.environ.get("DB_HOST", "localhost"),
            database=os.environ.get("DB_NAME", "database")
        )
        cur = conn.cursor()
        cur.execute("SELECT * FROM playercount")
        currentTime = datetime.now() - timedelta(minutes=10)

        message = "----- Current Player Status -----\n\n"
        for name, count, time in cur:
            convertedtime = time
            if convertedtime < currentTime:
                count = 0
            message += f"- {name}: {count} players\n"
        return message
    except mariadb.Error as e:
        logger.error(f"Error getting player count: {e}")
        return "--- Server error ---"
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return "--- Server error ---"

def run_discord_bot():
    TOKEN = os.environ.get("DISCORD_TOKEN", "token")
    intents = discord.Intents.default()
    client = discord.Client(intents=intents)
    channel = None

    @client.event
    async def on_ready():
        global channel
        logger.info(f'{client.user} is now running')
        gotChannel = discord.utils.get(client.get_all_channels(), name="players-online")
        channel = gotChannel
        logger.info(f'Got channel with ID {channel.id if channel else "None"}')

        if channel:
            test.start()
            inviteCleanUp.start()
        else:
            logger.error("Channel 'players-online' not found")

    @tasks.loop(hours=1, reconnect=True)
    async def inviteCleanUp():
        try:
            inviteChannel = discord.utils.get(client.get_all_channels(), name="game-lobby-invites")
            if inviteChannel:
                messagesDeletedCount = 0
                async for message in inviteChannel.history(limit=200):
                    currentTime = datetime.now(message.created_at.tzinfo) - timedelta(minutes=30)
                    if message.created_at < currentTime:
                        messagesDeletedCount += 1
                        await message.delete()
                logger.info(f"Deleted {messagesDeletedCount} old invite messages")
            else:
                logger.warning("game-lobby-invites channel not found")
        except Exception as e:
            logger.error(f"Error during invite cleanup: {e}")

    @tasks.loop(minutes=1, reconnect=True)
    async def test():
        global channel

        try:
            if channel:
                messages = [mess async for mess in channel.history(limit=2)]
                dateTimeStr = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                updateMessage = f"{get_latest_player_count()}\n{dateTimeStr}"
                if messages:
                    try:
                        message = await channel.fetch_message(channel.last_message_id)
                        if message:
                            await message.edit(content=updateMessage)
                        else:
                            logger.warning(f"Message edit failed: {dateTimeStr}")
                    except Exception as e:
                        logger.error(f"Error while trying to update message: {e}")
                else:
                    await channel.send(updateMessage)
                logger.info(f'Sending update: {dateTimeStr}')
            else:
                logger.error('Channel not found')
        except Exception as e:
            logger.error(f"Error during message update: {e}")

    client.run(TOKEN)

run_discord_bot()

