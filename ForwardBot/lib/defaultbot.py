from nextcord.ext import commands
import nextcord
import configparser
import logging
import logging.handlers
from . import configdataclass as cfg
from . import utils
from os import listdir



class DefaultBot(commands.Bot):
    CONFIG_LOCATION = "./config.ini"
    DEFAULT_CONFIG_LOCATION = "../config_template.ini"


    def __init__(self, *args, **kwargs):
        super().__init__(
            default_guild_ids=self.config.guilds,
            *args, 
            **kwargs
        )
        self._logger = None

    def _setup_forwardbot_logging(self):
        logger = logging.getLogger(__name__)
        logger.setLevel(self.config.bot_log_level)

        utils.make_path(self.config.bot_log_path)
        handler = logging.handlers.RotatingFileHandler(
            filename=self.config.bot_log_path,
            encoding='utf-8',
            maxBytes=1 * 1024 * 1024,  # 1 MiB
            backupCount=5,  # Rotate through 5 files
        )
        dt_fmt = '%Y-%m-%d %H:%M:%S'
        formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        self._logger = logger
        self.logger.info(f"Logging started in {handler.baseFilename}") 

    def _setup_nextcord_logging(self):
        logger = logging.getLogger("nextcord")
        logger.setLevel(self.config.nextcord_log_level)

        utils.make_path(self.config.nextcord_log_path)
        handler = logging.handlers.RotatingFileHandler(
            filename=self.config.nextcord_log_path,
            encoding='utf-8',
            maxBytes=5 * 1024 * 1024,  # 32 MiB
            backupCount=5,  # Rotate through 5 files
        )
        dt_fmt = '%Y-%m-%d %H:%M:%S'
        formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    @property
    def logger(self):
        if not self._logger:
            self._setup_forwardbot_logging()
            self._setup_nextcord_logging()
        return self._logger

    @property
    def config(self) -> cfg.ConfigDataClass:
        return utils.get_config()

    def load_cogs(self):
        self.logger.info("Loading cogs...")
        count = 0
        for filename in listdir("./cogs"):
            if filename.endswith(".py") and not filename.startswith("_"):
                self.logger.debug(f"Attempting to load cog './cogs/{filename}'")
                # cut off the .py from the file name
                self.load_extension(f"cogs.{filename[:-3]}")
                count += 1
        self.logger.info(f"{count} Cogs loaded.")

    async def on_ready(self):
        self.logger.info(f"{'#'*10} Starting {self.user.name} {'#'*10}")
        await self.change_presence(activity=nextcord.Game(name="Welcome to FC!"), status=nextcord.Status.online)
        self.logger.info(f"Startup complete.")
        print(f"Logged in as {self.user.name}:{self.user.id}")

    async def on_close(self):
        self.logger.info(f"{'#'*10} Closing {self.user.name} {'#'*10}")

    def activate(self):
        self.load_cogs()
        self.run(self.config.token)

