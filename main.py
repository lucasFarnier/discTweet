#importing all needed functions for setting and running the bot to code
import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os

#importing the token
load_dotenv()
token = os.getenv("DISCORD_TOKEN")

#sets up bot for coding
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

#placeholder for when replying to messages
replyie = ""

#when bot is on send this in consol
@bot.event
async def on_ready():
    print(f"good to go {bot.user.name}")

#when message sent with certain contents send back warning
@bot.event
async def on_message(message):
    #check for word
    if "tweet" in message.content.lower() and message.author != bot.user:
        #deletes the message
        await message.delete()

        #creates a default message
        userMsg = (f"** user** @user\n{message.content}")

        if message.reference:
            userMsg = (f"*replying to @user*\n** user** @user\n{message.content}")

        await message.channel.send(userMsg)

    #lets the bot handle other messages while dealing with 1 message
    await bot.process_commands(message)

bot.run(token, log_handler=handler, log_level=logging.DEBUG)