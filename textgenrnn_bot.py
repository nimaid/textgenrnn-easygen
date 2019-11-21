# Work with Python 3.6
import textgenrnn
import discord
import random
import string
import os
import zipfile
import tempfile
import shutil
import time
import datetime
import json

JSON_NAME = 'discord_bot.json'

json_file = dict()
TOKEN = ''
try:
    with open(JSON_NAME, 'r') as f:
        json_file = json.load(f)
    TOKEN = json_file['token']
except:
    TOKEN = input('Input Discord Token: ')
    json_file = dict()
    json_file['token'] = TOKEN
    with open(JSON_NAME, 'w') as f:
        json.dump(json_file, f)

client = discord.Client()

def random_name(length):
    return ''.join(random.choices(string.digits + string.ascii_uppercase + string.ascii_lowercase, k=length))

def gen_text(brain_name, length, temp=1.0):
    #extract brain
    brain = os.path.dirname(__file__)
    brain = os.path.join(brain, "brains")
    brain = os.path.join(brain, brain_name + ".zip")
    
    tempdir_base = tempfile.gettempdir()
    tempdir_base = os.path.join(tempdir_base, 'textgenrnn-easygen')
    tempdir = os.path.join(tempdir_base, random_name(32))
    while os.path.exists(tempdir):
        tempdir = os.path.join(tempdir_base, random_name(32))
    if not os.path.exists(tempdir_base):
        os.mkdir(tempdir_base)
    os.mkdir(tempdir)
    with zipfile.ZipFile(brain, 'r') as zf:
        zf.extractall(tempdir)

    #generate text
    start_time = time.time()
    from textgenrnn import textgenrnn

    textgen = textgenrnn(weights_path = os.path.join(tempdir, 'weights.hdf5'),
                         vocab_path = os.path.join(tempdir, 'vocab.json'),
                         config_path = os.path.join(tempdir, 'config.json'))

    print('Creating {} characters...'.format(length))
    text = textgen.generate(max_gen_length = length,
                            return_as_list = True,
                            temperature = temp)[0]

    gen_secs = time.time() - start_time
    gen_time =  str(datetime.timedelta(seconds=gen_secs)).split(':')
    time_text = str(round(float(gen_time[-1]))) + " seconds"
    if len(time_text) >= 2:
        mins = gen_time[-2]
        if mins[0] == '0':
            mins = mins[1:]
        if mins not in ('', '0'):
            time_text = mins + " minutes, " + time_text
    if len(time_text) >= 3:
        hours = gen_time[-3]
        if hours[0] == '0':
            hours = hours[1:]
        if hours not in ('', '0'):
            time_text = hours + " hours, " + time_text
    print('Done making text! It took {}.'.format(time_text))
    print(text)
    print('\nCleaning up...')
    shutil.rmtree(tempdir)
    print('All done!')
    return text

@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    content = message.content.split(" ")
    if content[0] == "!textgenrnn":
        msg = None
        try:
            length = int(content[2])
            try:
                msg = gen_text(content[1], int(content[2]))
            except:
                msg = "Invalid model name: " + content[1]
        except:
            msg = "Invalid length: " + content[2]
        
        await client.send_message(message.author, msg)

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(TOKEN)
