# coding=utf-8
"""
    DecoraterBot's source is protected by Cheese.lab industries Inc. Even though it is Open Source
    any and all users waive the right to say that this bot's code was stolen when it really was not.
    Me @Decorater the only core developer of this bot do not take kindly to those false Allegations.
    it would piss any DEVELOPER OFF WHEN THEY SPEND ABOUT A YEAR CODING STUFF FROM SCRATCH AND THEN BE ACCUSED OF
    SHIT LIKE THIS.
    
    So, do not do it. If you do Cheese.lab Industries Inc. Can and Will do after you for such cliams that it deems
    untrue.
    
    Cheese.lab industries Inc. Belieces in the rights of Original Developers of bots. They do not take kindly to
    BULLSHIT.
    
    Any and all Developers work all the time, many of them do not get paid for their hard work.
    
    I am one of those who did not get paid even though I am the original Developer I coded this bot from the bottom
    with no lines of code at all.
    
    And how much money did I get from it for my 11 months or so of working on it? None, yeah thats right 0$ how
    pissed can someone get?
    Exactly I have over stretched my relatives money that they paid for Internet and power for my computer so that
    way I can code my bot.
    
    However shit does go out of the Fan with a possible 600$ or more that my Laptop Drastically needs to Repairs as
    it is 10 years old and is falling apart
    
    I am half tempted myself to pulling this bot from github and making it on patrion that boobot was on to help me
    with my development needs.
    
    So, as such I accept issue requests, but please do not give me bullshit I hate it as it makes everything worse
    than the way it is.
    
    You do have the right however to:
        --> Contribute to the bot's development.
        --> fix bugs.
        --> add commands.
        --> help finish the per server config (has issues)
        --> update the Voice commands to be better (and not use globals which is 1 big thing that kills it).
        --> Use the code for your own bot. Put Please give me the Credits for at least mot of the code. And Yes you can
                bug fix all you like.
                But Please try to share your bug fixes with me (if stable) I would gladly Accept bug fixes that fixes
                any and/or all issues.
                (There are times when I am so busy that I do not see or even notice some bugs for a few weeks or more)

    But keep in mind any and all Changes you make can and will be property of Cheese.lab Industries Inc.
"""
import discord
import asyncio
import io
import sys
import subprocess
import os
import traceback
from discord.ext import commands


@asyncio.coroutine
def _resolve_send_message_error(client, message):
    svr_name = message.channel.server.name
    cnl_name = message.channel.name
    msginfo = 'Missing the Send Message Permssions in the {0} server on the {1} channel.'
    unabletosendmessageerror = msginfo.format(svr_name, cnl_name)
    try:
        yield from client.send_message(message.channel.server.owner, unabletosendmessageerror)
    except discord.errors.Forbidden:
        return


@asyncio.coroutine
def _resolve_unloaded_commands_error(client, message):
    msgdata = 'Sorry, Commands was unloaded by my owner for now (He might be updating them).'
    try:
        yield from client.send_message(message.channel, msgdata)
    except discord.errors.Forbidden:
        _resolve_send_message_error(client, message)
