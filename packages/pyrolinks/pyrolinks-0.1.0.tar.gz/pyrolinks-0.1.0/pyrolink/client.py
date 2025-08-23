from pyrogram import Client as PC, idle
from .core import generate_link
from .server import run_server

class Client:
    def __init__(self,host="0.0.0.0", port=8080, route="/dl", **client_kwargs):
        self.host = host
        self.port = port
        self.route = route
        self.bot = PC(**client_kwargs)

    @property
    def base_url(self):
        return f"http://{self.host}:{self.port}{self.route}"

    async def start(self):
        await self.bot.start()
        self.runner, self.site = await run_server(self.bot, host=self.host, port=self.port, route=self.route)

    async def stop(self):
        await self.site.stop()
        await self.runner.cleanup()
        await self.bot.stop()

    def on_message(self, *args, **kwargs):
        return self.bot.on_message(*args, **kwargs)

    async def generate_link(self, message):
        return await generate_link(message, self.base_url)
