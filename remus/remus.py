"""
A discord bot implemented via the discord.py libraries that allows the client to facilitate
an online game of One Night Werewolf.

Disclaimer: The game itself is a social deduction game from Bezier Games.
This bot is not officially licensed or affiliated with Bezier Games in any way.
I only made this bot to play over discord with my friends during the COVID-19 pandemic.
I am not profiting off of this in any way.

Author: Aryan Agrawal

Questions or Concerns? Contact me at agrawalaryanm@gmail.com
"""
import os
import discord
import json
from discord.ext import commands as cmd

remus = cmd.Bot(command_prefix='$')
authorized = [#ENTER A DISCORD MEMBER ID HERE]
test_channels = [#USED FOR AUTHORIZATION. ENTER A VALID CHANNEL NAME HERE.]
story_teller_id = #ENTER THE DISCORD MEMBER ID OF THE GAME MASTER/STORYTELLER HERE

guild_to_id = {#INSERT A MAP OF SERVER NAME TO SERVER ID HERE.}
player_info = {}
curr_game = 'default'

def read_vars(guild):
    if not(os.path.isdir('./.remus')):
        return;
    if guild is None:
        gID = guild_to_id[#INSERT SERVER NAME HERE]
    else:
        gID = guild.id
    with open('./.remus/' + str(gID) + '/curr.txt', 'r') as curr_file:
        global curr_game
        curr_game = curr_file.read()
    with open('./.remus/' + str(gID) + '/game' + curr_game + '.txt', 'r') as game_file:
        global player_info
        temp = json.load(game_file)
        if temp is None:
            player_info = {}
        else:
            player_info = temp


def write_vars(guild, game, info):
    if guild is None:
        gID = guild_to_id[#INSERT SERVER NAME HERE]
    else :
        gID = guild.id
    if not(os.path.isdir('./.remus')):
        os.mkdir('./.remus')
        os.mkdir('./.remus/' + str(gID))
    elif not(os.path.isdir('./.remus/' + str(gID))):
        os.mkdir('./.remus/' + str(gID))
    curr_file = open('./.remus/' + str(gID) + '/curr.txt', 'w')
    curr_file.write(str(game))
    curr_file.close()
    with open('./.remus/' + str(gID) + '/game' + str(game) + '.txt', 'w') as gamefile:
        json.dump(info, gamefile)

def write_curr_game(guild, game):
    if guild is None:
        gID = guild_to_id[#INSERT SERVER NAME HERE]
    else :
        gID = guild.id
    if not(os.path.isdir('./.remus')):
        os.mkdir('./.remus')
        os.mkdir('./.remus/' + str(gID))
    elif not(os.path.isdir('./.remus/' + str(gID))):
        os.mkdir('./.remus/' + str(gID))
    curr_file = open('./.remus/' + str(gID) + '/curr.txt', 'w')
    curr_file.write(str(game))
    curr_file.close()

@remus.event
async def on_ready():
    print('We have logged in as {0.user}'.format(remus))

def admin_perms():
    def perms(ctx):
        return ctx.message.author.id in authorized and ctx.channel.name in test_channels
    return cmd.check(perms)

def private_admin_perms():
    def perms(ctx):
        return ctx.message.author.id in authorized and ctx.channel.type == discord.ChannelType.private
    return cmd.check(perms)

def admin_perms_guild():
    def perms(ctx):
        return ctx.message.author.id in authorized and ctx.channel.type == discord.ChannelType.text and ctx.channel.name in test_channels
    return cmd.check(perms)

def wolf_perms():
    def perms(ctx):
        read_vars(ctx.guild)
        id = ctx.message.author.id
        return ctx.channel.type == discord.ChannelType.private and (player_info[str(id)][1] == 'wolf' or player_info[str(id)][1] == 'cub')
    return cmd.check(perms)

def sk_perms():
    def perms(ctx):
        read_vars(ctx.guild)
        id = ctx.message.author.id
        return player_info[str(id)][1] == 'serial killer' and player_info[str(id)][2] == 'alive' and ctx.channel.type == discord.ChannelType.private
    return cmd.check(perms)

def bodyguard_perms():
    def perms(ctx):
        read_vars(ctx.guild)
        id = ctx.message.author.id
        return player_info[str(id)][1] == 'bodyguard' and player_info[str(id)][2] == 'alive' and ctx.channel.type == discord.ChannelType.private
    return cmd.check(perms)

def seer_perms():
    def perms(ctx):
        read_vars(ctx.guild)
        id = ctx.message.author.id
        return player_info[str(id)][1] == 'seer' and player_info[str(id)][2] == 'alive' and ctx.channel.type == discord.ChannelType.private
    return cmd.check(perms)

@remus.command(name='members', help='Lists all members of the server.')
@admin_perms_guild()
async def member_list(ctx):
    curr_guild = ctx.guild
    msg = 'Members of ' + curr_guild.name + ': '
    for m in curr_guild.members:
        if not(m.bot):
            msg += '\n' + m.name
            if m.name != m.nick and m.nick != None:
                msg += ' (' + m.nick + ') '
    await ctx.send('For you, ' + ctx.author.mention + ':\n' + msg)

@remus.command(name='players-show', help='Lists all players in the current game.')
@admin_perms()
async def players_list(ctx):
    read_vars(ctx.guild)
    if len(player_info) == 0:
        await ctx.send('No players detected. Start a new game and add players first!')
        return
    msg = 'Players in the current game: '
    for playerID in player_info:
        msg += '\n' + player_info[playerID][0] + ': '
        if player_info[playerID][2] == 'alive':
            msg += 'alive'
        else:
            msg += 'dead (killed by ' + player_info[playerID][3] + ')'
    await ctx.send('For you, ' + ctx.author.mention + ':\n' + msg)

@remus.command(name='players-show-roles', help='Lists all players in the current game w/ roles.')
@private_admin_perms()
async def players_list_detailed(ctx):
    read_vars(ctx.guild)
    if len(player_info) == 0:
        await ctx.send('No players detected. Start a new game and add players first!')
    else:
        msg = 'Players in the current game: '
        for playerID in player_info:
            msg += '\n' + player_info[playerID][0] + ': '
            if player_info[playerID][2] == 'alive':
                msg += 'alive'
            else:
                msg += 'dead (killed by ' + player_info[playerID][3] + ')'
            if len(player_info[playerID][1]) == 0:
                msg += ' role: unassigned'
            else:
                msg += ' role: ' + player_info[playerID][1]
        await ctx.send('For you, ' + ctx.author.mention + ':\n' + msg)

@remus.command(name='game-deliver-roles', help='DMs each player their role.')
@admin_perms()
async def deliver_roles(ctx):
    read_vars(ctx.guild)
    wolf_ids = []
    wolf_names = []
    wolf_members = []
    minion_id = 0
    for memberID in player_info.keys():
        memb = discord.utils.find(lambda m: str(m.id) == memberID, ctx.guild.members)
        if memb is None:
            await ctx.send('Could not deliver role to ' + player_info[memberID][0])
        elif len(player_info[memberID][1]) == 0:
            await ctx.send('Did not deliver role to ' + player_info[memberID][0] + ' because there is no role assigned.')
        else:
            msg = 'You are a ' + player_info[memberID][1] + '. Good luck!'
            if player_info[memberID][1] == 'mason':
                other_masons = [player_info[id][0] for id in player_info.keys() if player_info[id][1] == 'mason' and id != memberID]
                if len(other_masons) != 0:
                    msg += ' Your fellow mason is ' + other_masons[0] + '.'
            if player_info[memberID][1] == 'wolf' or player_info[memberID][1] == 'cub':
                wolf_ids.append(memberID)
                wolf_members.append(memb)
                wolf_names.append(player_info[memberID][0])
            if player_info[memberID][1] == 'minion':
                minion_id = memberID
            await memb.send(content=msg)
            await ctx.send('Delivered role to ' + player_info[memberID][0] + '.')
    if minion_id != 0:
        minion = discord.utils.find(lambda m: str(m.id) == minion_id, ctx.guild.members)
        minion_msg = ''
        for name in wolf_names:
            minion_msg += name + " "
        await minion.send('The wolves are: ' + minion_msg)
    if len(wolf_members) > 1:
        wolf_msg = ''
        for name in wolf_names:
            wolf_msg += name + " "
        for wolfmemb in wolf_members:
            await wolfmemb.send('The wolves are: ' + wolf_msg)


@remus.command(name='players-add', help='*admin command* Adds a player to the game.')
@admin_perms()
async def add_player(ctx, username, game_nickname):
    read_vars(ctx.guild)
    member_val = discord.utils.get(ctx.guild.members, name=username)
    if member_val is None:
        await ctx.send('Could not find a user with that username in this server.')
    elif member_val.id in player_info:
        await ctx.send('That player is already in the game.')
    elif game_nickname in [info[0] for info in player_info.values()]:
        await ctx.send('Some other player in this game already has that nickname.')
    else:
        player_info[member_val.id] = (game_nickname, '', 'alive', '')
        write_vars(ctx.guild, curr_game, player_info)
        await ctx.send('Successfully added ' + game_nickname + ' to the current game' )

@remus.command(name='players-remove', help='*admin command* Removes a player from the current game.')
@admin_perms()
async def remove_player(ctx, game_nickname):
    read_vars(ctx.guild)
    wantedID = [key for key in player_info.keys() if player_info[key][0] == game_nickname]
    if len(str(wantedID)) == 0:
        await ctx.send("Could not find a player with that nickname in the current game.")
    else:
        wantedID = wantedID[0]
        del player_info[wantedID]
        write_vars(ctx.guild, curr_game, player_info)
        await ctx.send('Successfully removed ' + game_nickname + ' from the current game.')

@remus.command(name='games-new', help='*admin command* Creates a new game!')
@admin_perms()
async def new_game(ctx, name):
    read_vars(ctx.guild)
    if os.path.isfile('./.remus/' + str(ctx.guild.id) + '/game' + name + '.txt'):
        await ctx.send('A game of that name already exists.')
    else:
        curr_game = name
        temp = {}
        write_vars(ctx.guild, name, temp)
        await ctx.send('Successfully created new game: ' + name)

@remus.command(name='games-remove', help='*admin command* Dangerous! Removes the given game.')
@admin_perms()
async def rem_game(ctx, name):
    read_vars(ctx.guild)
    if not(os.path.isfile('./.remus/' + str(ctx.guild.id) + '/game' + name + '.txt')):
        await ctx.send('A game of that name does not exist.')
    else:
        os.remove('./.remus/' + str(ctx.guild.id) + '/game' + name + '.txt')
        game_change = ''
        global curr_game
        if curr_game == name:
            for file_name in os.listdir('./.remus/' + str(ctx.guild.id) + '/'):
                if os.path.isfile('./.remus/' + str(ctx.guild.id) + '/' + file_name) and 'game' in file_name:
                    game_change = file_name[4:len(file_name) - 4]
                    break
            if game_change == '':
                curr_game = "default"
            else:
                curr_game = game_change
        write_curr_game(ctx.guild, curr_game)
        await ctx.send('Successfully removed ' + name + '.')

@remus.command(name='games-list', help='Lists all games!')
@admin_perms()
async def list_games(ctx):
    read_vars(ctx.guild)
    if not(os.path.isdir('./.remus')):
        await ctx.send('No games yet! Make a game first.');
    else:
        msg = 'All games: '
        for file_name in os.listdir('./.remus/' + str(ctx.guild.id) + '/'):
            if os.path.isfile('./.remus/' + str(ctx.guild.id) + '/' + file_name) and 'game' in file_name:
                msg += '\n' + file_name[4:len(file_name) - 4]
                if file_name[4:len(file_name) - 4] == curr_game:
                    msg += ' (current game)'
        await ctx.send(msg)

@remus.command(name='games-set', help='*admin command* Sets the current game!')
@admin_perms()
async def set_game(ctx, name):
    read_vars(ctx.guild)
    if not(os.path.isfile('./.remus/' + str(ctx.guild.id) + '/game' + name + '.txt')):
        await ctx.send('A game of that name does not exist.')
    else:
        curr_game = name
        write_curr_game(ctx.guild, curr_game)
        await ctx.send('Successfully set the current game to ' + curr_game + '.')

@remus.command(name='game-assign-role', help='*admin command* Assigns a role to a player. Choose from: wolf, villager, cub, serial killer, hunter, bodyguard, knight, seer, mason, minion, cursed')
@private_admin_perms()
async def assign_roles(ctx, name, role):
    read_vars(ctx.guild)
    roles = ['wolf', 'villager', 'cub', 'serial killer', 'hunter', 'bodyguard', 'knight', 'seer', 'mason', 'minion', 'cursed']
    if role.lower() not in roles:
        await ctx.send('Not a valid role!')
    else:
        IDs = [id for id in player_info.keys() if player_info[id][0] == name]
        if len(IDs) == 0:
            await ctx.send('Could not find a player with that name.')
        else:
            id = IDs[0]
            player_info[id][1] = role.lower()
            write_vars(ctx.guild, curr_game, player_info)
            await ctx.send('Successfully set ' + name + ' to role ' + role.lower() + '.')

@remus.command(name='game-night-wolf-kill', help='Wolves can use this once a night to choose a player to target.')
@wolf_perms()
async def wolf_kill(ctx, name):
    read_vars(ctx.guild)
    guild_wanted = discord.utils.get(remus.guilds, id=guild_to_id[#INSERT SERVER NAME HERE])
    if guild_wanted is None:
        print('Could not find the guild.')
    else:
        storyteller = discord.utils.get(guild_wanted.members, id=story_teller_id)
        await storyteller.send(content='The wolves have elected to target ' + name + '.')

@remus.command(name='game-night-sk-kill', help='The serial killer can use this once a night to choose a player to target.')
@sk_perms()
async def sk_kill(ctx, name):
    read_vars(ctx.guild)
    guild_wanted = discord.utils.get(remus.guilds, id=guild_to_id[#INSERT SERVER NAME HERE])
    if guild_wanted is None:
        print('Could not find the guild.')
    else:
        storyteller = discord.utils.get(guild_wanted.members, id=story_teller_id)
        await storyteller.send(content='The serial killer has elected to target ' + name + '.')

@remus.command(name='game-night-bodyguard', help='The bodyguard can use this once a night to choose a player to protect.')
@bodyguard_perms()
async def bodyguard_protect(ctx, name):
    read_vars(ctx.guild)
    guild_wanted = discord.utils.get(remus.guilds, id=guild_to_id[#INSERT SERVER NAME HERE])
    if guild_wanted is None:
        print('Could not find the guild.')
    else:
        storyteller = discord.utils.get(guild_wanted.members, id=story_teller_id)
        await storyteller.send(content='The bodyguard has elected to protect ' + name + '.')

@remus.command(name='game-night-seer', help='The seer can use this once a night to choose a player to see the role of.')
@seer_perms()
async def seer(ctx, name):
    read_vars(ctx.guild)
    guild_wanted = discord.utils.get(remus.guilds, id=guild_to_id[#INSERT SERVER NAME HERE])
    if guild_wanted is None:
        print('Could not find the guild.')
    else:
        storyteller = discord.utils.get(guild_wanted.members, id=story_teller_id)
        await storyteller.send(content='The seer has elected to see the role of  ' + name + '. Please dm them the role.')

@remus.command(name='game-kill', help='*admin command* Allows the admin to exectute a character in the game.')
@private_admin_perms()
async def execute_player(ctx, name, cause):
    read_vars(ctx.guild)
    IDs = [ide for ide in player_info.keys() if player_info[ide][0] == name]
    if len(IDs) == 0:
        await ctx.send('Could not find a player of that name.')
    else:
        id_wanted = IDs[0]
        player_info[id_wanted][2] = 'dead'
        player_info[id_wanted][3] = cause
        write_vars(ctx.guild, curr_game, player_info)
        await ctx.send(name + '\'s character has been executed. You can confirm this with *$players-show*.')

@remus.command(name='game-revive', help='*admin command* Allows the admin to revive a character in the game.')
@private_admin_perms()
async def revive_player(ctx, name):
    read_vars(ctx.guild)
    IDs = [ide for ide in player_info.keys() if player_info[ide][0] == name]
    if len(IDs) == 0:
        await ctx.send('Could not find a player of that name.')
    else:
        id_wanted = IDs[0]
        player_info[id_wanted][2] = 'alive'
        write_vars(ctx.guild, curr_game, player_info)
        await ctx.send(name + '\'s character has been revived. You can confirm this with *$players-show*.')


@remus.command(name='game-send-story', help='*admin command* Sends the given story to the werewolf chat.')
@private_admin_perms()
async def send_story(ctx, story):
    guild_wanted = discord.utils.get(remus.guilds, id=guild_to_id[#INSERT SERVER NAME HERE])
    channel_wanted = discord.utils.get(guild_wanted.channels, name='werewolf')
    await channel_wanted.send(story)

remus.run(#INSERT BOT TOKEN HERE)
