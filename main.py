#hello from github
#importing all needed functions for setting and running the bot to code
import discord
from discord.ext import commands

import logging

import requests
import json

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
    if message.content.lower().lstrip().startswith("tweet "):
        #deletes the message
        await message.delete()

        #splits the current text to handle before and after the @ and then the text
        Handle1, Handle2, Text = await handleAndText(message.content, "tweet")
        userMsg = await forReplys(Handle1, Handle2, message)

        userMsg += f"\n{Text}"
        print(message.author.mention + "\n" + userMsg)

        #rather than send the message into the chat it instead sends the message to the persons dms
        #more uses with stuff such as tupper which is person specific and the bot cant send as a tupper
        await message.author.send(userMsg)

    elif message.content.lower().lstrip().startswith("poll "):
        #deletes the message
        await message.delete()

        #splits the current text to handle before and after the @ and then the text
        Handle1, Handle2, Text = await handleAndText(message.content, "poll")
        userMsg = await forReplys(Handle1, Handle2, message)
        PollOptions = Text.splitlines()

        userMsg += "\nnumber of responces:0"
        for option in PollOptions:
            userMsg += f"\n> {option} ~ **0%** ~ **0 votes**"

        print(message.author.mention + "\n" + userMsg)

        webhooks = await message.channel.webhooks()

        webhook = discord.utils.get(webhooks, name="PollBot")
        if webhook is None:
            print("creating")
            webhook = await message.channel.create_webhook(name="PollBot")
                
        await webhook.send(content=userMsg, username="PollBot")

    elif message.content.lower().lstrip().startswith("vote "):
        #deletes the message
        await message.delete()

        userVote = message.content.replace("vote", '', 1).strip()
        print(userVote)
        if message.reference:
            webhooks = await message.channel.webhooks()
            webhook = discord.utils.get(webhooks, name="PollBot")

            message = await message.channel.fetch_message(message.reference.message_id)
            messageRep = (message.content).split("\n")

            j = 0
            
            for i in messageRep:
                comparison = ((((messageRep[j])[2:]).split("~"))[0]).strip()
                ##need to make it so it removes the percentage and votes of end, split with tilda, add tilda to poll creation
                if messageRep[j].startswith("> ") and comparison == userVote:
                    print(f"|{comparison}|{userVote}")
                    messageRep, votesTotal = await editPollsTotal(messageRep, j)
                    print("completed total")
                    messageRep = await editPollsVote(messageRep, j, votesTotal)
                    print("completed line total")
                    break
                else:
                    j += 1
                    
            finalMessage = ""
            for i in messageRep:
                finalMessage += i + "\n"

            try:
                await webhook.edit_message(message.id, content=finalMessage)
                print("Poll message updated successfully")
            except Exception as e:
                print("Failed to edit poll message:", e)

    elif message.content.lower().lstrip().startswith("retweet "):
        #deletes the message
        await message.delete()

        #splits the current text to handle before and after the @ and then the text
        Handle1, Handle2, Text = await handleAndText(message.content, "retweet")
        userMsg = await forReplys(Handle1, Handle2, message)

        userMsg += f"\n{Text}"
        print(message.author.mention + "\n" + userMsg)
        retweetMsg = (await message.channel.fetch_message(message.reference.message_id)).content
        for retweetLine in retweetMsg.split("\n"):
            finaltTweetMsg += ("\t" + retweetLine)
        print(finaltTweetMsg)

        await message.author.send(userMsg + "\n" + finaltTweetMsg)


    elif "gorkus " in message.content.lower().lstrip() and not(message.content.lower().lstrip().startswith("tweet ")) and not message.author.bot:
        messageRep = message.content.lower().lstrip().split("\n")

        # get first line and checks if reply goes to line 2 to get proper handle line
        if "replying" in messageRep[0]:
            handle = messageRep[1].split("@")
        else:
            handle = messageRep[0].split("@")

        exuse = await gorkus()
        exuse = f"*replying to @{handle[1]}*\n" + "**gorkus** @TheGreat\n\n" + exuse
        print(exuse)

        webhooks = await message.channel.webhooks()

        webhook = discord.utils.get(webhooks, name="Gorkus")
        if webhook is None:
            print("creating")
            webhook = await message.channel.create_webhook(name="Gorkus")

        await webhook.send(content=exuse, username="Gorkus")

    #lets the bot handle other messages while dealing with 1 message
    await bot.process_commands(message)


async def handleAndText(MessageCont, type):
    tweeterHandleAndText = (MessageCont.split('@', 1))

    if ("Tweet" in tweeterHandleAndText[0]):
        Handle1 = tweeterHandleAndText[0].replace("Tweet", '', 1).strip()
    else:
        Handle1 = tweeterHandleAndText[0].replace(type, '', 1).strip()

    Handle2AndText = tweeterHandleAndText[1].split('\n', 1)
    Handle2 = Handle2AndText[0]

    Text = Handle2AndText[1]
    if "" not in (Text.split('\n', 1))[0]:
        print("no space")
    print("empty?" + Text.split('\n', 1)[0] + "empty?")
    print("text" + Text.split('\n', 1)[1])

    return (Handle1, Handle2, Text)

async def forReplys(Handle1, Handle2, message):
    #checks if the message is a reply to another tweet
    if message.reference:
        # gets the person being replied toos message, to get handle to add to reply message
        messageRep = ((await message.channel.fetch_message(message.reference.message_id)).content).split("\n")

        # get first line and checks if reply goes to line 2 to get proper handle line
        if "replying" in messageRep[0]:
            handle = messageRep[1].split("@")
        else:
            handle = messageRep[0].split("@")
            
        print(message.content)

        # formats users message
        userMsg = (f"*replying to @{handle[1]}*\n**{Handle1}** @{Handle2}")
    else:
        userMsg = (f"**{Handle1}** @{Handle2}")
    return userMsg

async def editPollsTotal(messageRep, line):
    line2 = messageRep[1].split(":")
    votesTotal = int(line2[1])+1
    messageRep[1] = line2[0] + ":" + str(votesTotal)
    return messageRep, votesTotal

async def editPollsVote(messageRep, line, votes):

    i=0
    
    for currentLine in messageRep:
        if currentLine.startswith("> "):
            voteLine = currentLine.split("~")
            voteLineCount = int(voteLine[2].replace("**", "").replace(" votes", "").strip())

            print(f"|{messageRep[i]}|{currentLine}|")
            if i == line:
                voteLineCount += 1

            percentage = (voteLineCount/votes)*100
            messageRep[i] = f"{voteLine[0].strip()} ~ **{round(percentage, 2)}%** ~ **{voteLineCount} votes**"
            
        i += 1
    
    return messageRep

#prelininary function to test fake grok that just gives an ecuse for everything
async def gorkus():
    #gets exuse from api
    excuse = json.loads(requests.get("https://naas.isalman.dev/no").content)
    #prints content
    #will be replaced with webhook like pollbot
    return(excuse["reason"])

@bot.command()
async def thelp(ctx):
    await ctx.send(f"welcome to disctweet\n\nthe bot as it is in this state(version 1.3) has 2 functions:\ntweet and reply\n-tweet is done by writing the word 'tweet' followed by your handle (user @user) then your text for the tweet\n-reply is done by following the same format as the first one but by treating it like a normal discord reply\nthe message will be deleted from the channel and the tweet formated version in your dms\n\nbelow is a formated command:\ntweet user @user\nyour message here\n\n3rd function in development although usable wont do anything which is poll")

bot.run(token, log_handler=handler, log_level=logging.DEBUG)
