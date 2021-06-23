import os
import discord
from dotenv import load_dotenv

DESCRIPTION = """A bot for grabbing quotes from less-real's API."""
DEBUG = False

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
TENOR_TOKEN = os.getenv('TENOR_TOKEN')

PREFIX = 'l!'
ACTIVITY_NAME = PREFIX + 'help'
ACTIVITY_TYPE = discord.ActivityType.listening

LR_URL = 'https://www.less-real.com'
API_URL = f'{LR_URL}/api/v1'
