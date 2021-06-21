import os
import discord
from dotenv import load_dotenv

load_dotenv()
DEBUG = False
TOKEN = os.getenv('DISCORD_TOKEN')
PREFIX = 'lr!'
ACTIVITY_NAME = PREFIX + 'help'
ACTIVITY_TYPE = discord.ActivityType.listening
LR_URL = 'https://www.less-real.com'
API_URL = LR_URL + '/api/v1'
