import nextcord
import logging
from logging.handlers import RotatingFileHandler
from nextcord.ext import commands
from databases import Database
from settings import PREFIX, DESCRIPTION

intents = nextcord.Intents.default()
intents.members = True

db = Database('sqlite:///data.db')

bot = commands.Bot(command_prefix=PREFIX, description=DESCRIPTION,
                   intents=intents)

""" Logging """
logger = logging.getLogger('lrbot')
logger.setLevel(logging.INFO)
log_formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s')
# Keep stderr default.
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(log_formatter)
fl_handler = RotatingFileHandler(
    filename='lrbot.log',
    maxBytes=10*1024*1024,
    backupCount=5,
    encoding='utf-8',
)
fl_handler.setFormatter(log_formatter)
fl_handler.setLevel(logging.WARNING)
logger.addHandler(stream_handler)
logger.addHandler(fl_handler)
