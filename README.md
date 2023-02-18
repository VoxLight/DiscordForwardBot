# DiscordForwardBot
A very easy to use bot with simple commands to copy channel message history between servers.

<br>

## Install
---
First is downloading the latest version of the bot:
```bash
git clone https://github.com/VoxLight/DiscordForwardBot
cd DiscordForwardBot
pip install -r requirements.txt
```
Once you have downloaded the latest version of the bot
and installed the requirements, we can setup the config

```bash
cp config_template.ini ./ForwardBot/config.ini
nano ./ForwardBot/config.ini
```
You need to replace a few settings in the config file
in order for the bot to work properly.

<br>

## Config
---
APP.token and SLASHCOMMANDS.guilds are the only required fields
that MUST be set in your config for the bot to work, however,
you can customize this to your liking.
```md
# This config file MUST be located at
# ForwardBot/config.ini. Once you modify
# this file, you will need to copy it, move
# it into the ForwardBot directory, and
# rename it to "config.ini".

[APP]
    # The discord bot token
    token=YOUR_TOKEN_HERE

    # This is found on the General Information page
    # of the developer portal for your App
    id=APP_ID_HERE

    # These are the required permissions for the bot
    # To invite it, copy this line and replace client_id
    # with the id used above. However, don't modify this line!
    scope=https://discord.com/api/oauth2/authorize?client_id={client_id}&permissions=68608&scope=bot


[LOGGING]
    # set level to the integer value of the log level
    # DEBUG: 10, INFO:20, WARN:30, ERROR:40, FATAL:50

    bot_log_path=./logs/forward.log
    bot_log_level=10

    nextcord_log_path=./logs/nextcord.log
    nextcord_log_level=30

[STORAGE]
    # Where to store the sqlite file
    # this path is relative without
    db_location=./storage/forwards.db


[SLASHCOMMANDS]
    # You can seperate the guild ids with commands (,)
    # or, leave this empty to run in global mode.
    # example: [775724065708048455,875804565708640856]
    guilds=[]
```

<br>

## Usage
---
Once you have installed the bot and edited the config, 
you can then use the APP.scope to invite the bot to join 
all of the guilds which the messages will be forwaded to.

The bot MUST be in the sending and recieving server for this to work.
You will also need to be running discord in developer mode in order to copy
the channel_id's more easily.

<br>

### `/forwards`
This command will display a list of all channels that the bot is forwarding
from and to in this format: `name:id -> name:id (active/paused)`. This
command will be useful for getting the list of channel ids that you need for
some of the other commands

### `/pause <channel_id>`
This command will pause the forwarding process to another channel.

### `/resume_forwarding <channel_id>`
This command will resume the forwarding process to another channel.
If the channel was paused, it will unpause the forwarding process.
If the bot crashed/disconnected, this will pick back up where it left off.

### `/end <channel_id>`
This will stop the forwarding process of one channel, and completely
remove it from the database. You CANNOT resume forwarding after using
this command, and it should only be used for debugging because the bot
will automatically remove channels that have had all their messages send.

### `/forwarder <from_> <to> (optional)<after_message>`
This will forward messages from the "from_" channel, to the "to" channel.
If you want to only forward messages after a specific message, you can
then specify the "after_message" parameter as a snowflake to the message.

<br>

## Contact
---
If you need any help, please contact me. Discord: VoxLight#7224