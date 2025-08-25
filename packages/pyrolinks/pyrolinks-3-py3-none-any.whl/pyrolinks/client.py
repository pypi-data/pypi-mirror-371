import logging
from pyrogram import Client as PyroClient
from .core import generate_link
from .server import run_server
from .errors import PyroLinksError, ServerError

class Client:
    """
    High-level wrapper around Pyrogram Client:
    - Binds HTTP server
    - Generates direct download links
    - Optional logging control via `log_level`
    """

    def __init__(
        self,
        api_id: int,
        api_hash: str,
        bot_token: str,
        *,
        schema: str = "http",
        domain: str | None = None,
        ip: str = "0.0.0.0",
        port: int = 8080,
        route: str = "/dl",
        ssl_cert: str | None = None,
        ssl_key: str | None = None,
        log_level: int = logging.INFO,  # User can set logging level
        **client_kwargs
    ):
        """
        Initialize the Pyrolinks Client.

        log_level: logging.DEBUG, INFO, WARNING, ERROR
        """
        logging.basicConfig(level=log_level)
        self.logger = logging.getLogger("PyrolinksClient")

        if schema not in ("http", "https"):
            raise ValueError("schema must be 'http' or 'https'")

        self.schema = schema
        self.domain = domain
        self.ip = ip or "0.0.0.0"
        self.port = port
        self.route = route
        self.ssl_cert = ssl_cert
        self.ssl_key = ssl_key
        self.bot = PyroClient(**client_kwargs)
        self.runner = None
        self.site = None

    @property
    def base_url(self) -> str:
        host_for_link = self.domain if self.domain else self.ip
        return f"{self.schema}://{host_for_link}:{self.port}{self.route}"

    async def start(self):
        self.logger.info("Starting Pyrolinks client and server...")
        try:
            await self.bot.start()
            self.runner, self.site = await run_server(
                self.bot,
                host=self.ip,
                port=self.port,
                route=self.route,
                ssl_cert=self.ssl_cert,
                ssl_key=self.ssl_key
            )
        except Exception as e:
            raise ServerError(f"Failed to start bot/server: {e}") from e

    async def stop(self):
        self.logger.info("Stopping Pyrolinks client and server...")
        try:
            if self.site:
                await self.site.stop()
            if self.runner:
                await self.runner.cleanup()
            await self.bot.stop()
        except Exception as e:
            raise ServerError(f"Failed to stop bot/server: {e}") from e

    def on_message(self, *args, **kwargs):
        return self.bot.on_message(*args, **kwargs)

    async def generate_link(self, message):
        try:
            return await generate_link(message, self.base_url)
        except Exception as e:
            raise PyroLinksError(f"Failed to generate link: {e}") from e