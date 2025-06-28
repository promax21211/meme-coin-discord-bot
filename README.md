# Meme Coin Discord Bot

A smart assistant Discord bot that recommends trending Solana meme coins and provides deep insights.

## 🔧 Setup

### 1. Install requirements
```
pip install -r requirements.txt
```

### 2. Add a `.env` file
Fill it with the following:

```
DISCORD_TOKEN=your_discord_token
MONGO_URI=your_mongo_uri
DEX_API=https://api.dexscreener.com/
PUMPFUN_API=https://pump.fun/api/
COINGECKO_API=https://api.coingecko.com/api/v3
JUPITER_API=https://quote-api.jup.ag/v6/quote
```

### 3. Run the bot
```
python bot.py
```

## 🚀 Commands

- `-recommendcoin`: Suggests the best trending coin with stats.
- `-tellabout <ct/address>`: Gives full breakdown of any token.
- `-currentinfo <ct/address>`: Shows current raw stats only.
- `-remind <ct/address>`: Sends updates in DM for 2 hours.
