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

#when bot is on send this in consol
@bot.event
async def on_ready():
    print(f"good to go - {bot.user.name}")

#when message sent with certain contents send back warning
@bot.event
async def on_message(message):
    #check for word
    if  message.content.lower().lstrip().startswith("tweet "):
        #deletes the message
        await message.delete()

        tweeterHandleAndText = (message.content.split('@', 1))
        Handle1 = tweeterHandleAndText[0].replace('tweet', '', 1).strip()
        Handle2AndText = tweeterHandleAndText[1].split('\n', 1)
        Handle2 = Handle2AndText[0]
        Text = Handle2AndText[1]

        #checks if the message is a reply to another tweet
        if message.reference:
            #gets the person being replied toos message, to get handle to add to reply message
            messageRep = ((await message.channel.fetch_message(message.reference.message_id)).content).split("\n")

            #get first line and checks if reply goes to line 2 to get proper handle line
            if "replying" in messageRep[0]:
                handle = messageRep[1].split("@")
                print(message.content)
            else:
                handle = messageRep[0].split("@")
                print(message.content)

            #formats users message
            userMsg = (f"*replying to @{handle[1]}*\n**{Handle1}** @{Handle2}\n{Text}")
        else:
            userMsg = (f"**{Handle1}** @{Handle2}\n{Text}")
        print(message.author.mention + "\n" + userMsg)

        #rather than send the message into the chat it instead sends the message to the persons dms
        #more uses with stuff such as tupper which is person specific and the bot cant send as a tupper
        await message.author.send(userMsg)

    #lets the bot handle other messages while dealing with 1 message
    await bot.process_commands(message)

@bot.command()
async def thelp(ctx):
    await ctx.send(f"welcome to disctweet\n\nthe bot as it is in this state(version 1) has 2 functions:\ntweet and reply\n-tweet is done by writing the word 'tweet' followed by your handle (user @user) then your text for the tweet\n-reply is done by following the same format as the first one but by treating it like a normal discord reply\nthe message will be deleted from the channel and the tweet formated version in your dms\n\nbelow is a formated command:\ntweet user @user\nyour message here")

bot.run(token, log_handler=handler, log_level=logging.DEBUG)