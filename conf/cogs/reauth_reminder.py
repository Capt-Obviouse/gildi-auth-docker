"""
Reauth Reminder Cog

Sends monthly reminders to a Discord channel prompting users to re-authorize
their ESI tokens for corp/alliance services.

Configuration (in local.py):
    REAUTH_REMINDER_CHANNEL_ID: Discord channel ID to send reminders to
    REAUTH_REMINDER_ROLE_ID: (Optional) Role ID to ping
    REAUTH_REMINDER_DAY: Day of month to send reminder (default: 1)
    REAUTH_REMINDER_HOUR: Hour to send reminder in UTC (default: 12)
"""

import logging
from datetime import datetime

import discord
from discord.ext import commands, tasks
from django.conf import settings

logger = logging.getLogger(__name__)


class ReauthButtons(discord.ui.View):
    """A view containing buttons that link to the auth pages."""

    def __init__(self, site_url: str):
        super().__init__(timeout=None)
        self.add_item(
            discord.ui.Button(
                label="Corp Audit Tokens",
                style=discord.ButtonStyle.link,
                url=f"{site_url}/audit/r/corp",
                emoji="\U0001F4CA",  # Chart emoji
            )
        )
        self.add_item(
            discord.ui.Button(
                label="Structure Owners",
                style=discord.ButtonStyle.link,
                url=f"{site_url}/structures/",
                emoji="\U0001F3D7",  # Building emoji
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

        return {
            "channel_id": getattr(settings, "REAUTH_REMINDER_CHANNEL_ID", None),
            "role_id": getattr(settings, "REAUTH_REMINDER_ROLE_ID", None),
            "day": getattr(settings, "REAUTH_REMINDER_DAY", 1),
            "hour": getattr(settings, "REAUTH_REMINDER_HOUR", 12),
            "site_url": site_url,
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
            title="\U0001F514 Monthly Director/CEO Token Reminder",
            description=(
                "If you have **director** or **CEO** roles in-game, please ensure "
                "your ESI tokens are up to date to keep our corp tools working!\n\n"
            ),
            color=discord.Color.gold(),
        )
        embed.add_field(
            name="\U0001F4CA Corp Audit Tokens",
            value=(
                "Click **Add Token** and select your director character.\n"
                "Enable: Structures, Starbases, Assets, Moons, Wallets, "
                "Member Tracking, Contracts, Industry Jobs"
            ),
            inline=False,
        )
        embed.add_field(
            name="\U0001F3D7 Structure Owners",
            value=(
                "Click **Add Owner** and select your director/CEO character "
                "to enable structure tracking and notifications."
            ),
            inline=False,
        )
        embed.set_footer(text="This is an automated monthly reminder")

        try:
            await channel.send(
                content=role_ping if role_ping else None,
                embed=embed,
                view=ReauthButtons(config["site_url"]),
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
            title="\U0001F514 Monthly Director/CEO Token Reminder (TEST)",
            description=(
                "If you have **director** or **CEO** roles in-game, please ensure "
                "your ESI tokens are up to date to keep our corp tools working!\n\n"
            ),
            color=discord.Color.gold(),
        )
        embed.add_field(
            name="\U0001F4CA Corp Audit Tokens",
            value=(
                "Click **Add Token** and select your director character.\n"
                "Enable: Structures, Starbases, Assets, Moons, Wallets, "
                "Member Tracking, Contracts, Industry Jobs"
            ),
            inline=False,
        )
        embed.add_field(
            name="\U0001F3D7 Structure Owners",
            value=(
                "Click **Add Owner** and select your director/CEO character "
                "to enable structure tracking and notifications."
            ),
            inline=False,
        )
        embed.set_footer(text="This is a TEST message - not a real reminder")

        await channel.send(
            embed=embed,
            view=ReauthButtons(config["site_url"]),
        )
        await ctx.send(f"Test reminder sent to <#{config['channel_id']}>")


def setup(bot):
    """Standard setup function for discord.py cogs."""
    bot.add_cog(ReauthReminder(bot))
