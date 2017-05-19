# coding=utf-8
"""
DecoraterBotCore
~~~~~~~~~~~~~~~~~~~

Core to DecoraterBot

:copyright: (c) 2015-2017 Decorater
:license: MIT, see LICENSE for more details.

"""
import os
import ctypes
import sys
import time
import json
import asyncio

import aiohttp
import discord
from discord.ext import commands
import consolechange
import dbapi
from BotErrors import *
try:
    import TinyURL
    disabletinyurl = False
except ImportError:
    print_data_001 = 'TinyURL for Python 3.x was not installed.\n' \
                     'It can be installed by running: pip install' \
                     ' --upgrade TinyURL3\nDisabled the tinyurl ' \
                     'command for now.'
    print(print_data_001)
    disabletinyurl = True
    TinyURL = None

try:
    from . import BotPMError
except ImportError:
    print('Some Unknown thing happened which made a critical bot c'
          'ode file unable to be found.')
    BotPMError = None
from . import BotConfigReader


__all__ = ['main', 'BotClient']

config = BotConfigReader.BotCredentialsVars()


def get_plugin_full_name(plugin_name):
    """
    returns the plugin's full name.
    """
    if plugin_name is not '':
        return 'DecoraterBotCore.plugins.' + plugin_name
    return None


class GitHubRoute:
    """gets the route information to the an github resource/file."""
    HEAD = "https://raw.githubusercontent.com/"

    def __init__(self, user : str, repo : str,
                 branch : str, filename : str):
        self.url = (self.HEAD + user + "/" +
                    repo + "/" + branch + "/" +
                    filename)


class PluginData:
    """
    Stores the data to plugins.
    """
    def __init__(self, plugincode=None, version=None,
                 textjson=None):
        self.plugincode = plugincode
        self.version = version
        self.textjson = textjson


class YTDLLogger(object):
    """
    Class for Silencing all of the Youtube_DL Logging stuff that defaults to
    console.
    """
    def __init__(self, bot):
        self.bot = bot

    def log_file_code(self, meth, msg):
        """
        Logs data to file (if set).
        :param meth: Method name.
        :param msg: message.
        :return: Nothing.
        """
        if meth is not '':
            if meth == 'ytdl_debug':
                logfile = os.path.join(
                    sys.path[0], 'resources', 'Logs',
                    'ytdl_debug_logs.log')
                try:
                    self.bot.DBLogs.log_writter(logfile, msg + '\n')
                except PermissionError:
                    return
            elif meth == 'ytdl_warning':
                logfile2 = os.path.join(
                    sys.path[0], 'resources', 'Logs',
                    'ytdl_warning_logs.log')
                try:
                    self.bot.DBLogs.log_writter(logfile2, msg + '\n')
                except PermissionError:
                    return
            elif meth == 'ytdl_error':
                logfile3 = os.path.join(
                    sys.path[0], 'resources', 'Logs',
                    'ytdl_error_logs.log')
                try:
                    self.bot.DBLogs.log_writter(logfile3, msg + '\n')
                except PermissionError:
                    return
            elif meth == 'ytdl_info':
                logfile4 = os.path.join(
                    sys.path[0], 'resources', 'Logs',
                    'ytdl_info_logs.log')
                try:
                    self.bot.DBLogs.log_writter(logfile4, msg + '\n')
                except PermissionError:
                    return
        else:
            return

    def log_setting_check(self, meth, msg):
        """
        checks the log youtube_dl setting.
        """
        if self.bot.BotConfig.log_ytdl:
            self.log_file_code(meth, msg)

    def info(self, msg):
        """
        Reroutes the Youtube_DL Messages of this type to teither a file or
        silences them.
        :param msg: Message.
        :return: Nothing.
        """
        self.log_setting_check('ytdl_info', msg)

    def debug(self, msg):
        """
        Reroutes the Youtube_DL Messages of this type to teither a file or
        silences them.
        :param msg: Message.
        :return: Nothing.
        """
        self.log_setting_check('ytdl_debug', msg)

    def warning(self, msg):
        """
        Reroutes the Youtube_DL Messages of this type to teither a file or
        silences them.
        :param msg: Message.
        :return: Nothing.
        """
        self.log_setting_check('ytdl_warning', msg)

    def error(self, msg):
        """
        Reroutes the Youtube_DL Messages of this type to teither a file or
        silences them.
        :param msg: Message.
        :return: Nothing.
        """
        self.log_setting_check('ytdl_error', msg)


class BotClient(commands.Bot):
    """
    Bot Main client Class.
    This is where the Events are Registered.
    """
    logged_in = False

    def __init__(self, **kwargs):
        # for the bot's plugins to be able to read their text json files.
        self.PluginConfigReader = BotConfigReader.PluginConfigReader
        self.PluginTextReader = BotConfigReader.PluginTextReader
        self.BotConfig = config
        self.BotPMError = BotPMError.BotPMError(self)
        self.sepa = os.sep
        self.bits = ctypes.sizeof(ctypes.c_voidp)
        self.commands_list = []
        self.YTDLLogger = YTDLLogger
        self.platform = None
        if self.bits == 4:
            self.platform = 'x86'
        elif self.bits == 8:
            self.platform = 'x64'
        self.path = sys.path[0]
        self.botbanslist = open(os.path.join(
            sys.path[0], 'resources', 'ConfigData', 'BotBanned.json'))
        self.banlist = json.load(self.botbanslist)
        self.botbanslist.close()
        self.consoledatafile = open(os.path.join(
            sys.path[0], 'resources', 'ConfigData', 'ConsoleWindow.json'))
        self.consoletext = json.load(self.consoledatafile)
        self.consoletext = self.consoletext[self.BotConfig.language]
        self.consoledatafile.close()
        try:
            self.ignoreslistfile = open(os.path.join(
                sys.path[0], 'resources', 'ConfigData', 'IgnoreList.json'))
            self.ignoreslist = json.load(self.ignoreslistfile)
            self.ignoreslistfile.close()
        except FileNotFoundError:
            print(str(self.consoletext['Missing_JSON_Errors'][0]))
            sys.exit(2)
        self.version = str(self.consoletext['WindowVersion'][0])
        self.start = time.time()
        # Bool to help let the bot know weather or not to actually print
        # the logged in stuff.
        self.logged_in_ = BotClient.logged_in
        # default to True in case options are not present in Credentials.json
        self.reconnects = 0
        # Will Always be True to prevent the Error Handler from Causing Issues
        # later.
        # Well only if the PM Error handler is False.
        self.enable_error_handler = True
        self.PATH = os.path.join(
            sys.path[0], 'resources', 'ConfigData', 'Credentials.json')
        self.somebool = False
        self.reload_normal_commands = False
        self.reload_voice_commands = False
        self.reload_reason = None
        self.initial_rejoin_voice_channel = True
        self.desmod = None
        self.desmod_new = None
        self.rejoin_after_reload = False
        super(BotClient, self).__init__(**kwargs)
        self.initial_plugins_cogs = self.BotConfig.default_plugins
        self.dbapi = dbapi.DBAPI(self, self.BotConfig.api_token)
        self.disabletinyurl = disabletinyurl
        self.TinyURL = TinyURL
        self.sent_prune_error_message = False
        self.tinyurlerror = False
        self.link = None
        self.member_list = []
        self.hook_url = None
        self.payload = {}
        self.header = {}
        self.resolve_send_message_error = (
            self.BotPMError.resolve_send_message_error)
        self.credits = BotConfigReader.CreditsReader(file="credits.json")
        self.is_bot_logged_in = False
        self.call_all()

    def call_all(self):
        """
        calls all functions that __init__ used to
        call except for super.
        """
        # DecoraterBot Necessities.
        self.asyncio_logger()
        self.discord_logger()
        self.changewindowtitle()
        # self.changewindowsize()
        self.remove_command("help")
        self.load_all_default_plugins()
        self.variable()
        self.login_helper()  # handles login.

    def load_all_default_plugins(self):
        """
        Handles loading all plugins that __init__
        used to load up.
        """
        for plugins_cog in self.initial_plugins_cogs:
            ret = self.load_plugin(plugins_cog)
            if isinstance(ret, str):
                print(ret)

    def load_bot_extension(self, extension_full_name):
        """
        loads an bot extension module.
        """
        try:
            self.load_extension(extension_full_name)
        except Exception:
            return str(traceback.format_exc())

    def unload_bot_extension(self, extension_full_name):
        """
        unloads an bot extension module.
        """
        self.unload_extension(extension_full_name)

    def load_plugin(self, plugin_name, raiseexec=True):
        """
        Loads up a plugin in the plugins folder in DecoraterBotCore.
        """
        pluginfullname = get_plugin_full_name(plugin_name)
        if pluginfullname is None:
            if raiseexec:
                raise ImportError(
                    "Plugin Name cannot be empty.")
        err = self.load_bot_extension(pluginfullname)
        if err is not None:
            return err

    def unload_plugin(self, plugin_name, raiseexec=True):
        """
        Unloads a plugin in the plugins folder in DecoraterBotCore.
        """
        pluginfullname = get_plugin_full_name(plugin_name)
        if pluginfullname is None:
            if raiseexec:
                raise CogUnloadError(
                    "Plugin Name cannot be empty.")
        self.unload_bot_extension(pluginfullname)

    def reload_plugin(self, plugin_name):
        """
        Reloads a plugin in the plugins folder in DecoraterBotCore.
        """
        self.unload_plugin(plugin_name, raiseexec=False)
        err = self.load_plugin(plugin_name)
        if err is not None:
            return err

    def add_commands(self, data):
        """Adds commands to commands_list."""
        for command in data:
            self.commands_list.append(command)

    def remove_commands(self, data):
        """Removes commands from commands_list."""
        for command in data:
            self.commands_list.remove(command)

    def changewindowtitle(self):
        """
        Changes the console's window Title.
        :return: Nothing.
        """
        consolechange.consoletitle(str(self.consoletext['WindowName'][0]) + self.version)

    @staticmethod
    def make_version(pluginname, pluginversion,
                     version=None):
        """
        Makes or remakes the contents to the plugin list
        json that stores the installed versions.

        Used for installing / updating plugins.
        """
        if version is None:
            version = {}
        version[pluginname] = {}
        version[pluginname]['version'] = pluginversion
        return version

    async def request_repo(self, pluginname):
        """
        requests the bot's plugin
        repository for an particualar plugin.
        """
        url = (
            GitHubRoute(
                "DecoraterBot-devs", "DecoraterBot-cogs",
                "master", "cogslist.json")).url
        data = await self.http.session.get(url)
        resp1 = await data.json(content_type='text/plain')
        version = resp1[pluginname]['version']
        url2 = resp1[pluginname]['downloadurl']
        url3 = resp1[pluginname]['textjson']
        data2 = await self.http.session.get(url2)
        data3 = await self.http.session.get(url3)
        plugincode = await data2.text()
        textjson = await data3.text()
        return PluginData(plugincode=plugincode,
                          version=version,
                          textjson=textjson)

    async def checkupdate(self, pluginname):
        """
        checks a plugin provided for updates.
        :returns: string considing of plugin's name
        and plugin's current version.
        """
        pluginversion = None  # for now until this is complete.
        requestrepo = await self.request_repo(pluginname)
        if requestrepo.version != pluginversion:
            # return every instance of 'PluginData'.
            return requestrepo

    async def checkupdates(self, pluginlist):
       """
       Checks for updates for plugins
       in the plugin list.
       """
       update_list = []
       for plugin in pluginlist:
           update_list.append(await self.checkupdate(plugin))
       # so bot can know which plugins have updates.
       return update_list

    async def install_plugin(self, pluginname):
        """
        installs a plugin provided.
        Also gets and sets an cached
        version of them too.
        """
        # TODO: Finish this.
        pass

    async def install_plugins(self, pluginnames):
        """
        installs all the plugins listed.
        """
        for pluginname in pluginnames:
            # install each plugin individually.
            self.install_plugin(pluginname)

    @staticmethod
    def changewindowsize():
        """
        Changes the Console's size.
        :return: Nothing.
        """
        consolechange.consolesize(80, 23)

    def discord_logger(self):
        """
        Logger Data.
        :return: Nothing.
        """
        if self.BotConfig.discord_logger:
            self.set_up_discord_logger()

    def asyncio_logger(self):
        """
        Asyncio Logger.
        :return: Nothing.
        """
        if self.BotConfig.asyncio_logger:
            self.set_up_asyncio_logger()

    def set_up_loggers(self, loggers=None):
        """
        Logs Events from discord and/or asyncio stuff.
        :param loggers: Name of the logger(s) to use.
        :return: Nothing.
        """
        if loggers is not None:
            if loggers == 'discord':
                logger = logging.getLogger('discord')
                logger.setLevel(logging.DEBUG)
                handler = logging.FileHandler(
                    filename=os.path.join(
                        sys.path[0], 'resources', 'Logs', 'discordpy.log'),
                    encoding='utf-8', mode='w')
                handler.setFormatter(logging.Formatter(
                    '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
                logger.addHandler(handler)
            elif loggers == 'asyncio' and self.bot is not None:
                self.bot.loop.set_debug(True)
                asynciologger = logging.getLogger('asyncio')
                asynciologger.setLevel(logging.DEBUG)
                asynciologgerhandler = logging.FileHandler(
                    filename=os.path.join(
                        sys.path[0], 'resources', 'Logs', 'asyncio.log'),
                        encoding='utf-8', mode='w')
                asynciologgerhandler.setFormatter(logging.Formatter(
                    '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
                asynciologger.addHandler(asynciologgerhandler)

    def set_up_discord_logger(self):
        """
        Sets up the Discord Logger.
        :return: Nothing.
        """
        self.set_up_loggers(loggers='discord')

    def set_up_asyncio_logger(self):
        """
        Sets up the asyncio Logger.
        :return: Nothing.
        """
        self.set_up_loggers(loggers='asyncio')

    # Helpers.

    def login_helper(self):
        """
        Bot Login Helper.
        :return: Nothing.
        """
        while True:
            ret = self.login_info()
            if ret is not None and ret is not -1:
                break

    # Login stuff.

    async def __ffs__(self, *args, **kwargs):
        """
        same as Client.run except this does not
        close the asyncio event loop.
        """
        await self.login(*args, **kwargs)
        await self.connect()

    def login_info(self):
        """
        Allows the bot to Connect / Reconnect.
        :return: Nothing.
        """
        if os.path.isfile(self.PATH) and os.access(self.PATH, os.R_OK):
            try:
                if self.BotConfig.bot_token is not None:
                    self.is_bot_logged_in = True
                    self.loop.run_until_complete(self.__ffs__(
                        self.BotConfig.bot_token))
            except discord.errors.GatewayNotFound:
                print(str(self.consoletext['Login_Gateway_No_Find'][0]))
                return -2
            except discord.errors.LoginFailure as e:
                if str(e) == "Improper credentials have been passed.":
                    print(str(self.consoletext['Login_Failure'][0]))
                    return -2
                elif str(e) == "Improper token has been passed.":
                    print(str(self.consoletext['Invalid_Token'][0]))
                    sys.exit(2)
            except TypeError:
                pass
            except KeyboardInterrupt:
                pass
            except asyncio.futures.InvalidStateError:
                return self.reconnect_helper()
            except aiohttp.ClientResponseError:
                return self.reconnect_helper()
            except aiohttp.ClientOSError:
                return self.reconnect_helper()
            if self.is_bot_logged_in:
                if not self.is_logged_in:
                    pass
                else:
                    return self.reconnect_helper()
        else:
            print(str(self.consoletext['Credentials_Not_Found'][0]))
            sys.exit(2)

    # used for the reconnection.

    def reconnect_helper(self):
        """
        helps make the bot reconnect.
        """
        self.reconnects += 1
        if self.reconnects != 0:
            print(
                'Bot is currently reconnecting for ' +
                str(self.reconnects) + 'times.')
        return -1

    def variable(self):
        """
        Function that makes Certain things on the
        on_ready event only happen 1
        time only. (e.g. the logged in printing stuff)
        :return: Nothing.
        """
        if not BotClient.logged_in:
            BotClient.logged_in = True
            self.logged_in_ = True


def main():
    """
    EntryPoint to DecoraterBot.
    :return: Nothing.
    """
    if config.shards > 0:
        BotClient(command_prefix=config.bot_prefix,
                  shard_id=config.run_on_shard,
                  shard_count=config.shards,
                  description=config.description,
                  pm_help=False)
    else:
        BotClient(command_prefix=config.bot_prefix,
                  description=config.description,
                  pm_help=False)
