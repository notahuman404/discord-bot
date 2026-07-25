import discord
import os
from dotenv import load_dotenv
import aiohttp
import json
import random
import requests
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse , HTMLResponse
current_sessions = {}

load_dotenv()

TOKEN = os.getenv("bot_token")
POKE_NAME_ID = 874910942490677270
SAVE_FOLDER = "pokemon_images"
os.makedirs(SAVE_FOLDER, exist_ok=True)
intents = discord.Intents.default()
intents.message_content = True
CHANNEL_ID = "1526236600823054386"
client = discord.Client(intents=intents)
import asyncio
from contextlib import asynccontextmanager
@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(client.start(TOKEN))  # note: start(), not run()
    yield
    await client.close()

app = FastAPI(lifespan=lifespan)

@app.api_route("/health", methods=["GET", "HEAD"])
async def health(request: Request):
  return {"status": "ok"}

@app.get("/")
def index(request: Request):
    return HTMLResponse(content = index_page)

@app.post("/send_message")
async def send(request: Request):

    data = await request.json()

    current_sessions.setdefault(f"{data['channel_id']}", []).append(data['auth_token'])
    
    a = await send_message_user(content=data.get('content', 'hello from discord bot!'), auth_token= data['auth_token'], channel_id = data['channel_id'], server_id = data['server_id'])
    return JSONResponse({"message": "successfully sent"})

@app.post("/stop_message")
async def stop(request: Request):
    data = await request.json()
    if data['channel_id'] in current_sessions.keys():
        try:
            current_sessions[data['channel_id']].pop(data['auth_token'])
        except:
            return JSONResponse({"message": "Auth token not in our database"})
    else:
        JSONResponse({"message": "channel id not in our database"})

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
        content = f"<@716390085896962058>c {pokename}"
        # use a dict that stores current sessions of the users pinging agains the channel id and server id
        auth_token = current_sessions.get(f"{message.channel.id}")[0]
        code = await send_message_user(content, auth_token, message.guild.id, message.channel.id)
        return
index_page = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Message Sender</title>
<style>
  :root {
    --bg: #1e1f22;
    --panel: #2b2d31;
    --field: #1e1f22;
    --border: #3f4147;
    --text: #f2f3f5;
    --muted: #949ba4;
    --accent: #5865f2;
    --accent-hover: #4752c4;
    --danger: #da373c;
    --danger-hover: #a12d2f;
    --ok: #23a55a;
  }

  * { box-sizing: border-box; }

  body {
    margin: 0;
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--bg);
    font-family: "gg sans", "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    color: var(--text);
    padding: 24px;
  }

  .card {
    width: 100%;
    max-width: 400px;
    background: var(--panel);
    border-radius: 12px;
    padding: 28px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.35);
  }

  .card h1 {
    font-size: 18px;
    font-weight: 700;
    margin: 0 0 4px;
    letter-spacing: 0.2px;
  }

  .card .subtitle {
    font-size: 13px;
    color: var(--muted);
    margin: 0 0 22px;
  }

  label {
    display: block;
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.02em;
    color: var(--muted);
    margin-bottom: 6px;
    margin-top: 16px;
  }

  label:first-of-type { margin-top: 0; }

  input {
    width: 100%;
    background: var(--field);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 10px 12px;
    font-size: 14px;
    color: var(--text);
    transition: border-color 0.15s ease;
  }

  input::placeholder { color: #6b6e76; }

  input:focus {
    outline: none;
    border-color: var(--accent);
  }

  .buttons {
    display: flex;
    gap: 10px;
    margin-top: 24px;
  }

  button {
    flex: 1;
    padding: 11px 0;
    font-size: 14px;
    font-weight: 600;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    transition: background 0.15s ease, transform 0.05s ease;
  }

  button:active { transform: translateY(1px); }

  button:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }

  #startBtn { background: var(--accent); color: white; }
  #startBtn:not(:disabled):hover { background: var(--accent-hover); }

  #stopBtn { background: var(--danger); color: white; }
  #stopBtn:not(:disabled):hover { background: var(--danger-hover); }

  #status {
    margin-top: 18px;
    font-size: 13px;
    color: var(--muted);
    display: flex;
    align-items: center;
    gap: 8px;
    min-height: 18px;
  }

  .dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: var(--muted);
    flex-shrink: 0;
  }

  .dot.running { background: var(--ok); box-shadow: 0 0 0 3px rgba(35,165,90,0.2); }
  .dot.error { background: var(--danger); box-shadow: 0 0 0 3px rgba(218,55,60,0.2); }
</style>
</head>
<body>

  <div class="card">
    <h1>Message Sender</h1>
    <p class="subtitle">Send an automated message on a fixed interval.</p>

    <label for="token">Auth Token</label>
    <input id="token" type="password" placeholder="Bot token" />

    <label for="serverId">Server ID</label>
    <input id="serverId" type="text" placeholder="e.g. 123456789012345678" />

    <label for="channelId">Channel ID</label>
    <input id="channelId" type="text" placeholder="e.g. 987654321098765432" />

    <div class="buttons">
      <button id="startBtn" onclick="startLoop()">Start</button>
      <button id="stopBtn" onclick="stopLoop()" disabled>Stop</button>
    </div>

    <p id="status"><span class="dot" id="statusDot"></span><span id="statusText">Idle</span></p>
  </div>

  <script>
    let loopTimer = null;

    function setStatus(text, state) {
      document.getElementById('statusText').textContent = text;
      const dot = document.getElementById('statusDot');
      dot.className = 'dot' + (state ? ' ' + state : '');
    }

    function startLoop() {
      const token     = document.getElementById('token').value.trim();
      const serverId  = document.getElementById('serverId').value.trim();
      const channelId = document.getElementById('channelId').value.trim();

      if (!token || !serverId || !channelId) {
        setStatus('Please fill in all three fields.', 'error');
        return;
      }

      document.getElementById('startBtn').disabled = true;
      document.getElementById('stopBtn').disabled  = false;
      setStatus('Running...', 'running');

      // Ping immediately, then every 2 seconds
      ping(token, serverId, channelId);
      loopTimer = setInterval(() => ping(token, serverId, channelId), 2000);
    }

    function stopLoop() {
      clearInterval(loopTimer);
      loopTimer = null;
      document.getElementById('startBtn').disabled = false;
      document.getElementById('stopBtn').disabled  = true;
      setStatus('Stopped', null);
    }

    async function ping(token, serverId, channelId) {
      try {
        const res = await fetch('/send_message', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            auth_token: token,
            server_id:  serverId,
            channel_id: channelId,
            content: "Jai Shri Krishna!"
          })
        });
        const data = await res.json().catch(() => ({}));
        const now = new Date().toLocaleTimeString();
        setStatus(`[${now}] ${res.ok ? data.message || 'OK' : 'Error ' + res.status}`, res.ok ? 'running' : 'error');
      } catch (err) {
        const now = new Date().toLocaleTimeString();
        setStatus(`[${now}] Request failed: ${err.message}`, 'error');
      }
    }
  </script>

</body>
</html>
"""
