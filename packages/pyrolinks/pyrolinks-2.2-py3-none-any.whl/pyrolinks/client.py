from pyrogram import Client as PyroClient
from .core import generate_link
from .server import run_server
from .errors import PyroLinksError, ServerError

class Client:
    """
    High-level wrapper around Pyrogram Client:
    - Binds an HTTP server on the specified IP and port.
    - Generates direct download links for Telegram media.
    - Allows optional domain and SSL configuration for links.
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
        **client_kwargs
    ):
        """
        Initialize the Pyrolinks Client.

        Parameters:
        - api_id, api_hash, bot_token: Credentials for Telegram API.
        - schema: "http" or "https" for generated links.
        - domain: Optional domain for link generation.
        - ip: Bind address for the HTTP server.
        - port: Port number for the HTTP server.
        - route: URL path prefix for download links.
        - ssl_cert, ssl_key: Paths to SSL certificate and key files.
        - client_kwargs: Additional parameters passed to Pyrogram Client.
        """

        if schema not in ("http", "https"):
            raise ValueError("schema must be 'http' or 'https'")

        self.schema = schema
        self.domain = domain
        self.ip = ip or "0.0.0.0"
        self.port = port
        self.route = route
        self.ssl_cert = ssl_cert
        self.ssl_key = ssl_key

        # Instantiate the underlying Pyrogram client with extra kwargs
        self.bot = PyroClient(**client_kwargs)

        # Internal references to the web server runner and site
        self.runner = None
        self.site = None

    @property
    def base_url(self) -> str:
        """
        Build the base URL used for download links.
        Falls back to IP if domain is not provided.
        """
        host_for_link = self.domain if self.domain else self.ip
        return f"{self.schema}://{host_for_link}:{self.port}{self.route}"

    async def start(self):
        """
        Start both the Pyrogram client and the HTTP server.
        Raises ServerError on failure.
        """
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
        """
        Stop the HTTP server and the Pyrogram client gracefully.
        Raises ServerError on failure.
        """
        try:
            if self.site:
                await self.site.stop()
            if self.runner:
                await self.runner.cleanup()
            await self.bot.stop()
        except Exception as e:
            raise ServerError(f"Failed to stop bot/server: {e}") from e

    def on_message(self, *args, **kwargs):
        """
        Shortcut to Pyrogram's on_message handler.
        Allows registering message handlers with decorators or filters.
        """
        return self.bot.on_message(*args, **kwargs)

    async def generate_link(self, message):
        """
        Generate a direct download link for a Telegram message.
        Raises PyroLinksError if link generation fails.
        """
        try:
            return await generate_link(message, self.base_url)
        except Exception as e:
            raise PyroLinksError(f"Failed to generate link: {e}") from e
