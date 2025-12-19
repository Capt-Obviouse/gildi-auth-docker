"""
Reauth Reminder Cog

Sends monthly reminders to a Discord channel prompting users to re-authorize
their ESI tokens for corp/alliance services.

Configuration (in local.py):
    REAUTH_REMINDER_CHANNEL_ID: Discord channel ID to send reminders to
    REAUTH_REMINDER_ROLE_ID: (Optional) Role ID to ping
    REAUTH_REMINDER_DAY: Day of month to send reminder (default: 1)
    REAUTH_REMINDER_HOUR: Hour to send reminder in UTC (default: 12)
    REAUTH_REMINDER_URL: URL path for reauth (default: /corptools/)
"""

import logging
from datetime import datetime

import discord
from discord.ext import commands, tasks
from django.conf import settings

logger = logging.getLogger(__name__)


class ReauthButton(discord.ui.View):
    """A view containing a button that links to the auth page."""

    def __init__(self, auth_url: str):
        super().__init__(timeout=None)
        self.add_item(
            discord.ui.Button(
                label="Re-authorize Characters",
                style=discord.ButtonStyle.link,
                url=auth_url,
                emoji="\U0001F510",  # Lock emoji
            )
        )


class ReauthReminder(commands.Cog):
    """Cog that sends monthly reminders to re-authorize ESI tokens."""

    def __init__(self, bot):
        self.bot = bot
        self.monthly_reminder.start()
        logger.info("ReauthReminder cog loaded")

    def cog_unload(self):
        self.monthly_reminder.cancel()
        logger.info("ReauthReminder cog unloaded")

    def get_config(self):
        """Get configuration from Django settings with defaults."""
        site_url = getattr(settings, "SITE_URL", "https://auth.example.com")
        reauth_path = getattr(settings, "REAUTH_REMINDER_URL", "/corptools/")

        return {
            "channel_id": getattr(settings, "REAUTH_REMINDER_CHANNEL_ID", None),
            "role_id": getattr(settings, "REAUTH_REMINDER_ROLE_ID", None),
            "day": getattr(settings, "REAUTH_REMINDER_DAY", 1),
            "hour": getattr(settings, "REAUTH_REMINDER_HOUR", 12),
            "auth_url": f"{site_url}{reauth_path}",
        }

    @tasks.loop(hours=1)
    async def monthly_reminder(self):
        """Check every hour if it's time to send the monthly reminder."""
        config = self.get_config()

        if not config["channel_id"]:
            return

        now = datetime.utcnow()

        # Only run on the configured day and hour
        if now.day != config["day"] or now.hour != config["hour"]:
            return

        channel = self.bot.get_channel(int(config["channel_id"]))
        if not channel:
            logger.warning(
                f"ReauthReminder: Could not find channel {config['channel_id']}"
            )
            return

        # Build the message
        role_ping = f"<@&{config['role_id']}>" if config["role_id"] else ""

        embed = discord.Embed(
            title="\U0001F514 Monthly Token Reminder",
            description=(
                "Please ensure your ESI tokens are up to date!\n\n"
                "If you have **director** or **CEO** roles, your tokens may need "
                "re-authorization to keep corp auditing and tracking tools working properly.\n\n"
                "Click the button below to check and refresh your character authorizations."
            ),
            color=discord.Color.gold(),
        )
        embed.set_footer(text="This is an automated monthly reminder")

        try:
            await channel.send(
                content=role_ping if role_ping else None,
                embed=embed,
                view=ReauthButton(config["auth_url"]),
            )
            logger.info(f"ReauthReminder: Sent monthly reminder to channel {config['channel_id']}")
        except discord.DiscordException as e:
            logger.error(f"ReauthReminder: Failed to send reminder: {e}")

    @monthly_reminder.before_loop
    async def before_reminder(self):
        """Wait for the bot to be ready before starting the loop."""
        await self.bot.wait_until_ready()
        logger.info("ReauthReminder: Task loop ready")

    @commands.command(name="testreauth", hidden=True)
    @commands.has_permissions(administrator=True)
    async def test_reauth(self, ctx):
        """Test command to manually trigger the reauth reminder (admin only)."""
        config = self.get_config()

        if not config["channel_id"]:
            await ctx.send("Error: REAUTH_REMINDER_CHANNEL_ID is not configured.")
            return

        channel = self.bot.get_channel(int(config["channel_id"]))
        if not channel:
            await ctx.send(f"Error: Could not find channel {config['channel_id']}")
            return

        embed = discord.Embed(
            title="\U0001F514 Monthly Token Reminder (TEST)",
            description=(
                "Please ensure your ESI tokens are up to date!\n\n"
                "If you have **director** or **CEO** roles, your tokens may need "
                "re-authorization to keep corp auditing and tracking tools working properly.\n\n"
                "Click the button below to check and refresh your character authorizations."
            ),
            color=discord.Color.gold(),
        )
        embed.set_footer(text="This is a TEST message - not a real reminder")

        await channel.send(
            embed=embed,
            view=ReauthButton(config["auth_url"]),
        )
        await ctx.send(f"Test reminder sent to <#{config['channel_id']}>")


def setup(bot):
    """Standard setup function for discord.py cogs."""
    bot.add_cog(ReauthReminder(bot))
