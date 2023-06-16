from discord.ext import commands, tasks
from discord.utils import get
from discord.ext.tasks import loop
from discord.ext.commands import Bot
from datetime import date, time, datetime
import discord
import os
import youtube_dl
from dotenv import load_dotenv
import requests
import json
import random
import csv
import pandas
import asyncio
import praw
from riotwatcher import LolWatcher, ApiError

# connects to discord, creates client using connection
client = discord.Client()
client = commands.Bot(command_prefix='$')

# get token 
load_dotenv()
TOKEN = os.getenv('TOKEN')
key = os.getenv('LOLAPI')

# sad word library
# TODO: try creating a text file and importing a list 
sad_words = ['sad', 'upset', 'depressed', 'unhappy', 'miserable']

thank_bot = ['thank', 'you', 'bot']

# encouragement library
# TODO: try creating a text file and importing a list 
starter_encourage = [
    'It may not seem like it now, but you got this!',
    'We all believe in you!',
    'You are as good as the people around you :)']

# gets inspirational quotes & author from zen quotes
def get_quote():
    response = requests.get("https://zenquotes.io/api/random")
    print(response)
    json_data = json.loads(response.text)
    quote = json_data[0]['q'] + " -" + json_data[0]['a']
    return quote

# triggers when bot is ready for use
@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    count = 0
    for guild in client.guilds:
        print(f'{guild.id} (name: {guild.name})')
        count += 1
    remind.start()
    await client.change_presence(activity=discord.Game(name="Memory Games"))

@client.event
async def on_message(message):
    # testing purposes
    print(f'message: {message.content} received')

    # stops the bot from responding to itself 
    if message.author == client.user:
        return

    # greeting from the Bot
    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')
    
    # inspirational quote
    if message.content.startswith('$inspire'):
        quote = get_quote()
        await message.channel.send(quote)

    # get memes from r/memes
    # TODO: only works with r/memes atm
    if message.content.startswith('$image subreddit: r/'):

        REDDIT_ID = os.getenv('REDDIT_ID')
        REDDIT_SECRET = os.getenv('REDDIT_SECRET')
        reddit = praw.Reddit(client_id=REDDIT_ID,
                            client_secret=REDDIT_SECRET,
                            username ='i am not ',
                            password ='putting this',
                            user_agent='onto the internet!')

        subred = message.content[20:]
        print(f'meme request from subreddit: {subred}')
        subreddit = reddit.subreddit(subred)
        all_submissions = []
        top = subreddit.top(limit = 50)

        for sub in top:
            print(sub)
            all_submissions.append(sub)

        random_submission = random.choice(all_submissions)
        name = random_submission.title
        url = random_submission.url
        em = discord.Embed(title = name)
        em.set_image(url = url)
        await message.channel.send(embed = em)
    
    # level checker for LoL
    # TODO: update env codes?
    if message.content.startswith('$LoL level: '):
        region = 'euw1'
        name = message.content[11:]
        print(f'getting account: {name}')
        watcher = LolWatcher(key)
        summoner = watcher.summoner.by_name(region,name)
        level = summoner['summonerLevel']
        await message.channel.send(f'{name} is level {level}')
    
    # receiving remind requests
    if message.content.startswith('$remind'):
        f = open(r"D:\VScode\Discord-bot-2021\reminders.csv",'a')

        #info
        print(f'reminder channel id: {message.channel.id}')

        # reformating the message
        message.content.strip('$remind ')
        a = message.content.find('<') 
        b = message.content.find('>') 
        c = message.content.find(' @ ')
        ID = str(message.channel.id)

        # adding it to the csv file
        user = message.content[a:b+1]
        reminder = message.content[b+2:c]
        date_time = message.content[c+3:]
        full_message = (user,reminder,date_time,ID)
        csv.writer(f).writerow(full_message)
        f.close()
        await message.channel.send('reminder set!')

    # checking all stored reminders, currently returns in a weird format
    # ckecing must be done is a globally muted text channel to prevent @tting all users
    if message.content.startswith('$check reminders'):
        df = pandas.read_csv(r'D:\VScode\Discord-bot-2021\reminders.csv')
        df.columns = [''] * len(df.columns)
        await message.channel.send(df)

@loop(seconds=60)
async def remind():
    print(f'----------------')
    print(f'checking time: {datetime.today()}')
    df = pandas.read_csv(r'D:\VScode\Discord-bot-2021\reminders.csv',
    parse_dates=['date_time']  
    )
    row = -1
    print(f'old df: {df}')
    for datefull in df['date_time']:
        row += 1
        date = datefull.strftime('%Y-%m-%d %H:%M')

        #deleting reminders from the past
        if (date<datetime.today().strftime('%Y-%m-%d %H:%M')) == True:
            message = str(f'{df.reminder[row]}')
            print(f'!PAST! reminder: {message}, at time: {date}')
            index = (df.index[df["date_time"] == datefull])
            df = df.drop(index)
 
        #reminders at the current minute
        elif (date==datetime.today().strftime('%Y-%m-%d %H:%M')) == True:
            message = str(f'{df.reminder[row]}')
            ID = df.ID[row]
            index = (df.index[df["date_time"] == datefull])
            print(f'!PRESENT! reminder: {message}, at time: {date}')
            channel = client.get_channel(int(ID))
            await channel.send(message)
            df = df.drop(index)

        elif (date>datetime.today().strftime('%Y-%m-%d %H:%M')) == True:
            print(f'!FUTURE! reminder: {df.reminder[row]}, time: {date}')

    with open (r'D:\VScode\Discord-bot-2021\reminders.csv', 'w') as f:
        df.to_csv(f,index=False)
    
    df = pandas.read_csv(r'D:\VScode\Discord-bot-2021\reminders.csv',
        parse_dates=['date_time']  
        )
    print(f'new df: {df}')
    print(f'----------------')

client.run('or this')

# TODO: "feet per second" => post feet pic
# TODO: "formula giver?"