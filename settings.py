import os
import discord
from dotenv import load_dotenv

load_dotenv()
DEBUG = False
TOKEN = os.getenv('DISCORD_TOKEN')
PREFIX = 'lr!'
client = discord.Client()
