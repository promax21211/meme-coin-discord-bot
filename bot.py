import os
import discord
import aiohttp
from discord.ext import commands, tasks
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# Start Flask server in background
Thread(target=run_flask).start()

TOKEN = os.getenv("DISCORD_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")
DEX_API = os.getenv("DEX_API")
PUMPFUN_API = os.getenv("PUMPFUN_API")
COINGECKO_API = os.getenv("COINGECKO_API")
JUPITER_API = os.getenv("JUPITER_API")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="-", intents=intents)

mongo_client = AsyncIOMotorClient(MONGO_URI)
db = mongo_client["meme_coin_bot"]

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    check_reminders.start()

async def fetch_json(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

@bot.command()
async def recommendcoin(ctx):
    await ctx.send("🔍 Scanning for top meme coin...")

    try:
        pump_data = await fetch_json(f"{PUMPFUN_API}coins/recent")
        if not pump_data or len(pump_data) == 0:
            await ctx.send("🚫 No trending coins found.")
            return

        top_coin = pump_data[0]
        token_name = top_coin.get("name")
        token_address = top_coin.get("id")
        buyers = top_coin.get("buyers")
        chart_url = f"https://dexscreener.com/solana/{token_address}"
        banner_url = f"https://pump.fun/{token_address}"

        embed = discord.Embed(title=f"🪙 Token: {token_name}", description=f"🔗 Address: `{token_address}`", color=0x00ff99)
        embed.add_field(name="👥 Buyers", value=str(buyers), inline=True)
        embed.add_field(name="📎 Chart", value=f"[Click Here]({chart_url})", inline=True)
        embed.add_field(name="🖼️ Banner", value=f"[Pump.Fun]({banner_url})", inline=True)
        embed.set_footer(text="Recommended based on Pump.fun latest")
        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.command()
async def tellabout(ctx, *, address):
    await ctx.send(f"🔎 Analyzing token: `{address}` ...")

    try:
        screener_data = await fetch_json(f"{DEX_API}/pairs/solana/{address}")
        if not screener_data.get("pair"):
            await ctx.send("❌ No info found for that token.")
            return

        token_info = screener_data["pair"]
        embed = discord.Embed(title=f"📘 Token Info: {token_info['baseToken']['name']}", color=0x00ccff)
        embed.add_field(name="💰 Price", value=token_info['priceUsd'], inline=True)
        embed.add_field(name="💧 Liquidity", value=f"${token_info['liquidity']['usd']}", inline=True)
        embed.add_field(name="📈 Volume 24h", value=f"${token_info['volume']['h24']}", inline=True)
        embed.add_field(name="🔁 Transactions/min", value=str(token_info['txCount']['m5']), inline=True)
        embed.add_field(name="📎 Chart", value=f"[View Chart](https://dexscreener.com/solana/{address})", inline=False)
        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"❌ Error fetching data: {str(e)}")

@bot.command()
async def currentinfo(ctx, *, address):
    await ctx.send(f"📊 Getting live info for: `{address}`")

    try:
        screener_data = await fetch_json(f"{DEX_API}/pairs/solana/{address}")
        token = screener_data.get("pair")
        if not token:
            await ctx.send("❌ Token info not found.")
            return

        embed = discord.Embed(title=f"📍 Current Stats: {token['baseToken']['name']}", color=0xff9900)
        embed.add_field(name="💰 Price", value=token['priceUsd'], inline=True)
        embed.add_field(name="💧 Liquidity", value=f"${token['liquidity']['usd']}", inline=True)
        embed.add_field(name="📈 5m Volume", value=f"${token['volume']['m5']}", inline=True)
        embed.add_field(name="🔁 Trades/Min", value=token['txCount']['m5'], inline=True)
        embed.add_field(name="👥 Holders", value="N/A", inline=True)
        embed.add_field(name="📎 Chart", value=f"[View Chart](https://dexscreener.com/solana/{address})", inline=False)
        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"❌ Error fetching data: {str(e)}")

@bot.command()
async def remind(ctx, *, address):
    user_id = str(ctx.author.id)
    token_doc = {
        "user_id": user_id,
        "token_address": address,
        "start_time": discord.utils.utcnow()
    }
    await db.reminders.insert_one(token_doc)
    await ctx.send(f"⏳ You will get updates on `{address}` in DM for 2 hours.")

@tasks.loop(minutes=15)
async def check_reminders():
    reminders = await db.reminders.find({}).to_list(length=50)
    for r in reminders:
        user = await bot.fetch_user(int(r['user_id']))
        token_address = r['token_address']
        try:
            screener_data = await fetch_json(f"{DEX_API}/pairs/solana/{token_address}")
            token = screener_data.get("pair")
            if token:
    msg = (
        f"📢 Update for `{token['baseToken']['name']}`\n"
        f"💰 Price: {token['priceUsd']}\n"
        f"📈 5m Volume: ${token['volume']['m5']}\n"
        f"💧 Liquidity: ${token['liquidity']['usd']}"
    )
    await user.send(msg)
        except:
            continue

bot.run(TOKEN)
