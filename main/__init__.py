#ChauhanMahesh/Vasusen/DroneBots/COL

from pyrogram import Client
from telethon import TelegramClient
from decouple import config
import logging, time, sys

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)

"""
ps2 : 5832484897:AAF9XsvYlzaMJWrS6hq14yaEu_RKjzT84-8
ps1 : 5926923294:AAF5IjNw_zkPUFyk5HLO2VETteoL6PvzjJI
ps3 : 6379096336:AAHKVOvumm-ErIn1bRPsHK9P3wkjw4jS5ik
ps4 : 6401894192:AAFVDctSK9k3v3z7oTdtbweGLb5gmeUTxRw

p : 6077629818:AAFTBqay0B_4yD_LrwnfpfAU2fcXU5Vs2bU
"""

# variables
API_ID = 2992000
API_HASH = "235b12e862d71234ea222082052822fd"
BOT_TOKEN = "6077629818:AAFTBqay0B_4yD_LrwnfpfAU2fcXU5Vs2bU"
FORCESUB = int("-1001711957758")
ACCESS = int("-1001879806908")
ACCESS2 = int("-1001823465454")
MONGODB_URI = "mongodb+srv://Vasusen:darkmaahi@cluster0.o7uqb.mongodb.net/cluster0?retryWrites=true&w=majority"
AUTH_USERS = 5351121397
BOT_UN = "Premiumsrcb2_bot"

bot = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN) 

Bot = Client(
    "SaveRestricted",
    bot_token=BOT_TOKEN,
    api_id=int(API_ID),
    api_hash=API_HASH
)    

try:
    Bot.start()
except Exception as e:
    print(e)
    sys.exit(1)
