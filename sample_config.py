import irc.bot

# Sample config
# Rename to config.py and edit as desired

# server settings
servers    = [irc.bot.ServerSpec('irc.freenode.org', 6667)]
nick       = 'rehaiku'
name       = 'Rehaiku IRC Bot'
channel    = '#rehaiku'
ssl        = False

# bot settings
cmd_prefix = '@'
