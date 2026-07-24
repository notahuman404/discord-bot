import discord
import os
from dotenv import load_dotenv
import aiohttp
import json

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse , HTMLResponse
app = FastAPI()
current_sessions = {}

@app.get("/")
def index(request: Request):
    return HTMLReponse(content = index_page)
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
index_page = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Discord Message Sender</title>
  <style>
    body { font-family: sans-serif; max-width: 400px; margin: 60px auto; padding: 0 16px; }
    label { display: block; margin-top: 14px; font-weight: bold; }
    input { width: 100%; box-sizing: border-box; padding: 8px; margin-top: 4px; font-size: 14px; }
    .buttons { margin-top: 20px; display: flex; gap: 10px; }
    button { padding: 10px 24px; font-size: 15px; cursor: pointer; }
    #startBtn { background: #5865f2; color: white; border: none; border-radius: 4px; }
    #stopBtn  { background: #ed4245; color: white; border: none; border-radius: 4px; }
    button:disabled { opacity: 0.5; cursor: not-allowed; }
    #status { margin-top: 16px; font-size: 13px; color: #555; }
  </style>
</head>
<body>
  <h2>Discord Message Sender</h2>

  <label for="token">Discord Auth Token</label>
  <input id="token" type="password" placeholder="Your Discord auth token" />

  <label for="serverId">Server ID</label>
  <input id="serverId" type="text" placeholder="Server (guild) ID" />

  <label for="channelId">Channel ID</label>
  <input id="channelId" type="text" placeholder="Channel ID" />

  <div class="buttons">
    <button id="startBtn" onclick="startLoop()">Start</button>
    <button id="stopBtn" onclick="stopLoop()" disabled>Stop</button>
  </div>

  <p id="status">Idle.</p>

  <script>
    let loopTimer = null;

    function startLoop() {
      const token     = document.getElementById('token').value.trim();
      const serverId  = document.getElementById('serverId').value.trim();
      const channelId = document.getElementById('channelId').value.trim();

      if (!token || !serverId || !channelId) {
        document.getElementById('status').textContent = 'Please fill in all three fields.';
        return;
      }

      document.getElementById('startBtn').disabled = true;
      document.getElementById('stopBtn').disabled  = false;
      document.getElementById('status').textContent = 'Running...';

      // Ping immediately, then every 2 seconds
      ping(token, serverId, channelId);
      loopTimer = setInterval(() => ping(token, serverId, channelId), 2000);
    }

    function stopLoop() {
      clearInterval(loopTimer);
      loopTimer = null;
      document.getElementById('startBtn').disabled = false;
      document.getElementById('stopBtn').disabled  = true;
      document.getElementById('status').textContent = 'Stopped.';
    }

    async function ping(token, serverId, channelId) {
      try {
        const res = await fetch('/send_message', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            auth_token: token,
            server_id:  serverId,
            channel_id: channelId
          })
        });
        const data = await res.json().catch(() => ({}));
        const now = new Date().toLocaleTimeString();
        document.getElementById('status').textContent =
          `[${now}] ${res.ok ? data.message || 'OK' : 'Error ' + res.status}`;
      } catch (err) {
        const now = new Date().toLocaleTimeString();
        document.getElementById('status').textContent = `[${now}] Request failed: ${err.message}`;
      }
    }
  </script>
</body>
</html>

"""
client.run(TOKEN)