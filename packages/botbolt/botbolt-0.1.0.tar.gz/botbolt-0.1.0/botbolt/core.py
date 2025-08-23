"""
botbolt.core
A friendly wrapper around nextcord for quick Discord bot development.
"""

from typing import Optional, Callable, Any, Coroutine
import logging
import nextcord
from nextcord.ext import commands

__all__ = ["Bot", "embed"]

def embed(title: str = "", description: str = "", **kwargs) -> nextcord.Embed:
    """Quick helper to build an Embed."""
    e = nextcord.Embed(title=title, description=description, **kwargs)
    return e

class Bot:
    """
    A tiny wrapper around nextcord.ext.commands.Bot with simpler defaults.

    Example:
        bot = Bot("TOKEN", prefix="!")
        @bot.event
        async def on_ready():
            bot.log(f"Logged in as {bot.user}")
        @bot.command("ping")
        async def ping(ctx):
            await bot.reply(ctx, "pong!")
        bot.run()
    """

    def __init__(self, token: str, prefix: str = "!", intents: str = "default", activity: Optional[str] = None):
        self._token = token
        intents_obj = self._make_intents(intents)
        self._bot = commands.Bot(command_prefix=prefix, intents=intents_obj)
        if activity:
            self._activity = nextcord.Game(name=activity)
        else:
            self._activity = None

        # mirror some attrs for convenience
        self.user = None  # will set after login
        self._setup_internal_events()

    # ---------------------------- Internals ----------------------------

    def _make_intents(self, level: str) -> nextcord.Intents:
        """
        Create sensible default intents.
        Levels:
            - "minimal": just guilds
            - "default": messages + guilds (message_content True)
            - "all": all intents (requires enabling in Discord Dev Portal)
        """
        lvl = (level or "default").lower()
        if lvl == "minimal":
            intents = nextcord.Intents.none()
            intents.guilds = True
            return intents
        elif lvl == "all":
            intents = nextcord.Intents.all()
            intents.message_content = True
            return intents
        else:
            intents = nextcord.Intents.default()
            intents.message_content = True
            intents.members = True  # common need
            return intents

    def _setup_internal_events(self) -> None:
        @self._bot.event
        async def on_ready():
            self.user = self._bot.user
            if self._activity:
                await self._bot.change_presence(activity=self._activity)
            self.log(f"✅ Ready as {self._bot.user}")

    # --------------------------- Decorators ---------------------------

    @property
    def event(self):
        """
        Use like @bot.event on async functions (same as nextcord.Bot.event).
        """
        return self._bot.event

    def command(self, name: Optional[str] = None, **kwargs):
        """
        Register a prefix command. Usage:
            @bot.command("ping")
            async def ping(ctx): ...
        """
        def decorator(func):
            self._bot.command(name=name, **kwargs)(func)
            return func
        return decorator

    def slash(self, name: Optional[str] = None, description: str = "A command"):
        """
        Register a simple slash command without complex options.
        Usage:
            @bot.slash("hello", "Says hi")
            async def hello(interaction):
                await interaction.response.send_message("Hi!")
        """
        app_cmds = self._bot.application_command

        def decorator(func):
            cmd_name = name or func.__name__
            @app_cmds(name=cmd_name, description=description)
            async def _wrapped(interaction: nextcord.Interaction):
                return await func(interaction)
            return _wrapped
        return decorator

    # --------------------------- Helpers -----------------------------

    async def reply(self, ctx: commands.Context, content: str = None, **kwargs) -> nextcord.Message:
        """Reply helper for prefix commands."""
        if hasattr(ctx, "reply"):
            return await ctx.reply(content, **kwargs)
        return await ctx.send(content, **kwargs)

    def log(self, *args, **kwargs) -> None:
        print(*args, **kwargs)

    # --------------------------- Lifecycle ---------------------------

    def run(self) -> None:
        """Run the bot (blocks)."""
        self._bot.run(self._token)

    # Expose underlying nextcord bot for power users
    @property
    def raw(self) -> commands.Bot:
        return self._bot
