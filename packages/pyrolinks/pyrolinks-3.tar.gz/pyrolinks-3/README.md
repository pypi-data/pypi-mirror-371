# PyroLinks
A simple Pyrogram-based module to create streaming download links for Telegram files !

```bash
pip install pyrolinks
```

**🍺Example**
```python
import asyncio
import logging
from pyrolinks import Client
from pyrolinks.errors import PyroLinksError
from pyrogram import filters, idle

API_ID = 123456
API_HASH = "your_api_hash"
BOT_TOKEN = "your_bot_token"
bot = Client(
    name = "pyrolinks",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    log_level=logging.INFO,
    max_concurrent_transmissions=10,
    schema="http",
    domain="domain.com",
    ip="0.0.0.0",
    port=8080,
    route="/dl",
)


@bot.on_message(
    filters.private & (filters.document | filters.video | filters.audio | filters.photo)
)
async def handler(client, message):
    try:
        link = await bot.generate_link(message)
        await message.reply(f"✅ Direct link:\n{link}")
    except PyroLinksError as e:
        await message.reply(f"❌ Error: {e}")


async def main():
    await bot.start()
    print(f"Bot and server running at {bot.base_url}")
    await idle()
    print("Stopping bot and server...")
    await bot.stop()


loop = asyncio.get_event_loop()
loop.run_until_complete(main())

```
