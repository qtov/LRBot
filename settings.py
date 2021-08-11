import os
import discord
from dotenv import load_dotenv

DESCRIPTION = """A bot for grabbing quotes from less-real's API."""

load_dotenv()
DEBUG = os.getenv('DEBUG', '0')
DEBUG = bool(int(DEBUG))  # convert to bool.
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

PREFIX = 'lr!'
ACTIVITY_NAME = PREFIX + 'help'
ACTIVITY_TYPE = discord.ActivityType.listening

LR_URL = 'https://www.less-real.com'
API_URL = f'{LR_URL}/api/v1'
