import discord
import os
from dotenv import load_dotenv
import aiohttp
import json

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
app = FastAPI()
current_sessions = {}

@app.post("/send_message")
def send(request: Request):

    data = request.json()

    current_sessions.setdefault(data['channel_id'], []).append(data['auth_token'])
    
    a = await send_message_user(content=data['content'], auth_token= data['auth_token'], channel_id = data['channel_id'], server_id = data['server_id'])
    return JSONResponse({"message": "successfully sent"})

@app.post("/stop_message")
def stop(request: Request):
    data = request.json()
    if data['channel_id'] in current_sessions.keys():
        try:
            current_sessions[data['channel_id']].pop(data['auth_token'])
        except:
            return JSONResponse({"message": "Auth token not in our database"})
    else:
        JSONResponse({"message": "channel id not in our database"})
load_dotenv()

TOKEN = os.getenv("bot_token")
POKE_NAME_ID = 874910942490677270
SAVE_FOLDER = "pokemon_images"
os.makedirs(SAVE_FOLDER, exist_ok=True)
intents = discord.Intents.default()
intents.message_content = True
CHANNEL_ID = "1526236600823054386"


client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")


async def send_message_user(content, auth_token, server_id, channel_id):
    headers = {"Authorization": auth_token,
               "Content-Type": "application/json",
               "User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 14541.0.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
               "Referer": f"https://discord.com/channels/{server_id}/{channel_id}",
    }

    url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
    random_nonce = str(random.randint(10**18, (10**19) - 1))

    payload = {
        "content": content,
        "nonce": random_nonce,
        "tts": False,
        "flags": 0,
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))

    print(f"Status Code: {response.status_code}")
    try:
        print("Response:", response.json())
    except Exception:
        print("Response Text:", response.text)

@client.event
async def on_message(message):
    # Ignore everyone except Poké-Name
    if message.author.id == POKE_NAME_ID:

        print(f"{message.author}: {message.content}")
        pokename = (((message.content).split("<:_:"))[0]).split("## ")[1]
        content = f"<@716390085896962058> {pokename}"
        # use a dict that stores current sessions of the users pinging agains the channel id and server id
        auth_token = current_sessions[message.channel.id][0]
        code = await send_message_user(content, auth_token, message.guild.id, message.channel.id)
        return

client.run(TOKEN)