# PyroLinks
A simple Pyrogram-based module to create streaming download links for Telegram files !

```bash
pip install pyrolinks
```

**🍺Example**
```python
import asyncio
from pyrogram import filters, idle
from pyrolinks import Client

API_ID = 1234
API_HASH = "abcd"
BOT_TOKEN = "1234567890:abcdefghijklmnopqrstuvwxyz"
DOMAIN = "feedozer.ir"
PORT = 8080


bot = Client(
    name="pyrolinks",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    domain=DOMAIN,
    port=PORT
)


@bot.on_message(filters.private & (filters.document | filters.video | filters.audio | filters.photo))
async def make_link(_, message):
    url = await bot.generate_link(message)
    await message.reply_text(f"✅ Link Generated:\n{url}")


async def main():
    await bot.start()
    print(f"Bot and server are running. Links will use {DOMAIN}:{PORT}")
    await idle()  
    await bot.stop()


loop = asyncio.get_event_loop()
loop.run_until_complete(main())

```
