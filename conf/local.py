# Every setting in base.py can be overloaded by redefining it here.
from .base import *

import environ
import os

env = environ.Env(
        DEBUG=(bool, False)
)


environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

SECRET_KEY = os.environ.get("AA_SECRET_KEY")
SITE_NAME = os.environ.get("AA_SITENAME")
SITE_URL = (
    f"{os.environ.get('PROTOCOL')}"
    f"{os.environ.get('AUTH_SUBDOMAIN')}."
    f"{os.environ.get('DOMAIN')}"
)
CSRF_TRUSTED_ORIGINS = [SITE_URL]
DEBUG = os.environ.get("AA_DEBUG", False)
DATABASES["default"] = {
    "ENGINE": "django.db.backends.mysql",
    "NAME": os.environ.get("AA_DB_NAME"),
    "USER": os.environ.get("AA_DB_USER"),
    "PASSWORD": os.environ.get("AA_DB_PASSWORD"),
    "HOST": os.environ.get("AA_DB_HOST"),
    "PORT": os.environ.get("AA_DB_PORT", "3306"),
    "OPTIONS": {
        "charset": os.environ.get("AA_DB_CHARSET", "utf8mb4")
    }
}

# Register an application at https://developers.eveonline.com for Authentication
# & API Access and fill out these settings. Be sure to set the callback URL
# to https://example.com/sso/callback substituting your domain for example.com
# Logging in to auth requires the publicData scope (can be overridden through the
# LOGIN_TOKEN_SCOPES setting). Other apps may require more (see their docs).

ESI_SSO_CLIENT_ID = os.environ.get("ESI_SSO_CLIENT_ID")
ESI_SSO_CLIENT_SECRET = os.environ.get("ESI_SSO_CLIENT_SECRET")
ESI_SSO_CALLBACK_URL = f"{SITE_URL}/sso/callback"
ESI_USER_CONTACT_EMAIL = os.environ.get(
    "ESI_USER_CONTACT_EMAIL"
)  # A server maintainer that CCP can contact in case of issues.

# By default emails are validated before new users can log in.
# It's recommended to use a free service like SparkPost or Elastic Email to send email.
# https://www.sparkpost.com/docs/integrations/django/
# https://elasticemail.com/resources/settings/smtp-api/
# Set the default from email to something like 'noreply@example.com'
# Email validation can be turned off by uncommenting the line below. This can break some services.
REGISTRATION_VERIFY_EMAIL = False
EMAIL_HOST = os.environ.get("AA_EMAIL_HOST", "")
EMAIL_PORT = os.environ.get("AA_EMAIL_PORT", 587)
EMAIL_HOST_USER = os.environ.get("AA_EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("AA_EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = os.environ.get("AA_EMAIL_USE_TLS", True)
DEFAULT_FROM_EMAIL = os.environ.get("AA_DEFAULT_FROM_EMAIL", "")

ROOT_URLCONF = "myauth.urls"
WSGI_APPLICATION = "myauth.wsgi.application"
STATIC_ROOT = "/var/www/myauth/static/"
BROKER_URL = f"redis://{os.environ.get('AA_REDIS', 'redis:6379')}/0"
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{os.environ.get('AA_REDIS', 'redis:6379')}/1",  # change the 1 here to change the database used
    }
}

HEALTH_CHECK = {
        "REDIS_URL": f"redis://{os.environ.get('AA_REDIS', 'redis:6379')}/0"
}



# Add any additional apps to this list.
INSTALLED_APPS += [
        'allianceauth.services.modules.discord',
        'allianceauth.hrapplications',
        'allianceauth.corputils',
        'allianceauth.permissions_tool',
        # 'allianceauth.fleetactivitytracking',
        'timezones',
        'eveuniverse',
        # 'moonstuff',
        'securegroups',
        'corptools',
        'aastatistics',
        'structuretimers',
        'structures',
        'moons',
        'invoices',
        'taskmonitor',
        'aadiscordbot',
        'fittings',
        'memberaudit',
        # 'memberaudit_securegroups',
        # 'wikijs',
        'inactivity',
        'buybackprogram',
        'afat',
        'charlink',
        'ravworks_exporter',
        'package_monitor',
        'killtracker',
        'health_check',
        'health_check.db',                          # stock Django health checkers
        'health_check.cache',
        'health_check.storage',
        'health_check.contrib.migrations',
        'health_check.contrib.psutil',              # disk and memory utilization; requires psutil
        'health_check.contrib.redis',               # requires Redis broker
]

#######################################
# Add any custom settings below here. #
#######################################
DISCORD_GUILD_ID = env('DISCORD_GUILD_ID')
DISCORD_CALLBACK_URL = f"{SITE_URL}/discord/callback/"
DISCORD_APP_ID = env('DISCORD_APP_ID')
DISCORD_APP_SECRET = env('DISCORD_APP_SECRET')
DISCORD_BOT_TOKEN = env('DISCORD_BOT_TOKEN')
DISCORD_SYNC_NAMES = env.bool('DISCORD_SYNC_NAMES', False)

CELERYBEAT_SCHEDULE['discord.update_all_usernames'] = {
    'task': 'discord.update_all_usernames',
    'schedule': crontab(minute=0, hour='*/12'),
}

## Corp Tools
CORPTOOLS_APP_NAME = "Character Audit"

## AA-Statistics
MEMBER_ALLIANCES = ["1900696668"] # Alliances you care about statistics for
CELERYBEAT_SCHEDULE['aastatistics.tasks.run_stat_model_update'] = {
    'task': 'aastatistics.tasks.run_stat_model_update',
    'schedule': crontab(minute=0, hour=0,)
}

## Structure Timers
CELERYBEAT_SCHEDULE['structuretimers_housekeeping'] = {
    'task': 'structuretimers.tasks.housekeeping',
    'schedule': crontab(minute=0, hour=3),
}

## Structures
CELERYBEAT_SCHEDULE['structures_update_all_structures'] = {
    'task': 'structures.tasks.update_all_structures',
    'schedule': crontab(minute='*/30'),
}

CELERYBEAT_SCHEDULE['structures_fetch_all_notifications'] = {
    'task': 'structures.tasks.fetch_all_notifications',
    'schedule': crontab(minute='*/5'),
}

## Invoice Manager
PAYMENT_CORP = 98596560
INVOICES_APP_NAME = "Invoices"

# Moons
PUBLIC_MOON_CORPS = [98596560]

## Allianceauth-Discordbot
# Admin Commands
ADMIN_DISCORD_BOT_CHANNELS = env.list('ADMIN_DISCORD_BOT_CHANNELS')

# Sov Commands
SOV_DISCORD_BOT_CHANNELS = env.list('SOV_DISCORD_BOT_CHANNELS')

# Adm Commands
ADM_DISCORD_BOT_CHANNELS = env.list('ADM_DISCORD_BOT_CHANNELS')
DISCORD_BOT_SOV_STRUCTURE_OWNER_IDS = [98596560] # Centre for Advanced Studies example
DISCORD_BOT_MEMBER_ALLIANCES = [1900696668] # A list of alliances to be considered "Mains"
DISCORD_BOT_ADM_REGIONS = [10000058] # The Forge Example
DISCORD_BOT_ADM_SYSTEMS = [30004576] # Jita Example
DISCORD_BOT_ADM_CONSTELLATIONS = [20000668] # Kimitoro Example

LOGGING['handlers']['bot_log_file']= {
    'level': os.environ.get('AA_LOG_LEVEL', 'INFO'),
    'class': 'logging.handlers.RotatingFileHandler',
    'filename': os.path.join(BASE_DIR, 'log/discord_bot.log'),
    'formatter': 'verbose',
    'maxBytes': 1024 * 1024 * 5,
    'backupCount': 5,
}
LOGGING['loggers']['aadiscordbot'] = {'handlers': ['bot_log_file'],'level': os.environ.get('AA_LOG_LEVEL', 'INFO')}

DISCORD_BOT_COGS = [
 "aadiscordbot.cogs.about", # about the bot
 "aadiscordbot.cogs.admin", # Discord server admin helpers
 "aadiscordbot.cogs.members", # Member lookup commands
 "aadiscordbot.cogs.timers", # timer board integration
 "aadiscordbot.cogs.auth", # return auth url
 "aadiscordbot.cogs.sov", # some sov helpers
 "aadiscordbot.cogs.time", # whats the time Mr Eve Server
 "aadiscordbot.cogs.eastereggs", # some "fun" commands from ariel...
 "aadiscordbot.cogs.remind", # very Basic in memory reminder tool
 "aadiscordbot.cogs.reaction_roles", # auth group integrated reaction roles
 "aadiscordbot.cogs.services", # service activation data
 "aadiscordbot.cogs.price_check", # Price Checks
 "aadiscordbot.cogs.eightball", # 8ball should i install this cog
 "aadiscordbot.cogs.welcomegoodbye", # Customizable user join/leave messages
 "aadiscordbot.cogs.models", # Populate and Maintain Django Models for Channels and Servers
 "aadiscordbot.cogs.quote", # Save and recall messages
 ]

DISCORD_BOT_TASK_RATE_LIMITS = {
    "send_channel_message_by_discord_id": "100/s",
    "send_direct_message_by_discord_id": "1/s",
    "send_direct_message_by_user_id": "1/s"
}

# Fittings Module
CELERYBEAT_SCHEDULE['fittings_update_types'] = {
    'task': 'fittings.tasks.verify_server_version_and_update_types',
    'schedule': crontab(minute=0, hour='12'),
}

# Update Discord Nicknames
CELERYBEAT_SCHEDULE['discord_update_nicknames'] = {
        'task': 'discord.update_all_nicknames',
        'scshedule': crontab(minute=30),
}

# Wiki Stuff
WIKIJS_API_KEY = env('WIKIJS_API_KEY')
WIKIJS_URL = env('WIKIJS_URL')
WIKIJS_AADISCORDBOT_INTEGRATION = True
WIKIJS_API_URL = env('WIKIJS_API_URL')

# Buybackprogram
CELERYBEAT_SCHEDULE['buybackprogram_update_all_prices'] = {
    'task': 'buybackprogram.tasks.update_all_prices',
    'schedule': crontab(minute=0, hour='0'),
}
CELERYBEAT_SCHEDULE['buybackprogram_update_all_contracts'] = {
    'task': 'buybackprogram.tasks.update_all_contracts',
    'schedule': crontab(minute='*/15'),
}

BUYBACKPROGRAM_TRACKING_PREFILL = "gildi-bbp"

# Afat
CELERYBEAT_SCHEDULE["afat_update_esi_fatlinks"] = {
    "task": "afat.tasks.update_esi_fatlinks",
    "schedule": crontab(minute="*/1"),
}

CELERYBEAT_SCHEDULE["afat_logrotate"] = {
    "task": "afat.tasks.logrotate",
    "schedule": crontab(minute="0", hour="1"),
}

# Memberaudit
CELERYBEAT_SCHEDULE['memberaudit_run_regular_updates'] = {
    'task': 'memberaudit.tasks.run_regular_updates',
    'schedule': crontab(minute=0, hour='*/1'),
}

# Inactivity
CELERYBEAT_SCHEDULE['inactivity_check_inactivity'] = {
    'task': 'inactivity.tasks.check_inactivity',
    'schedule': crontab(minute=0, hour=0),
}

# Package Monitor
CELERYBEAT_SCHEDULE['package_monitor_update_distributions'] = {
    'task': 'package_monitor.tasks.update_distributions',
    'schedule': crontab(minute='*/60'),
}

# Killtracker
# aa-killtracker
CELERYBEAT_SCHEDULE['killtracker_run_killtracker'] = {
    'task': 'killtracker.tasks.run_killtracker',
    'schedule': crontab(minute='*/1'),
}
KILLTRACKER_QUEUE_ID = "GILDI2750"  # Put your unique queue ID here



SHELL_PLUS = "ipython"
HEALTH_TOKEN = env('HEALTH_TOKEN')
LOGGING['handlers']['log_file']['level'] = os.environ.get('AA_LOG_LEVEL', 'INFO')


# Temp Fix
CT_CHAR_ACTIVE_IGNORE_NOTIFICATIONS_MODULE=True
