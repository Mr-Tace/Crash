import discord
from discord.ext import commands, tasks
from discord.utils import get
import asyncio
import os
from dotenv import load_dotenv

load_dotenv("bot_token.env")
TOKEN = os.getenv("TOKEN")

# Intents are required for managing reactions and roles
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.members = True

reaction_timers = {}

bot = commands.Bot(command_prefix='!', intents=intents)

# Role-reaction mapping
reaction_roles = {
    "💬": "Want to Chat",
    "🎮": "Want to Play",
    "<:Valorant:1315005904411693076>": "Want to Play Valorant",
    "<:LeagueofLegends:1315005449413722122>": "Want to Play League of Legends",
    "<:diamond:1285018724277162067>": "Want to Play Minecraft",
    "<:MonsterHunter:1315007368005816392>": "Want to Play Monster Hunter",
    "<:Rainbow6Siege:1316748311452979290>": "Want to Play Rainbow 6 Siege",
    "<:Gmod:1318524287988142102>":"Want to Play Gmod"
}

user_roles = {
    "Want to Chat", "Want to Play", "Want to Play Valorant", 
    "Want to Play League of Legends", "Want to Play Minecraft", 
    "Want to Play Monster Hunter", "Want to Play Rainbow 6 Siege", 
    "Want to Play Gmod"
}

TARGET_CHANNEL_ID = 881630803069653042
TARGET_MESSAGE_ID = 1320788515793014937

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')


@bot.command()
async def crping(ctx):
    reactions = [
        "💬", "🎮", "<:Valorant:1315005904411693076>", "<:LeagueofLegends:1315005449413722122>", "<:diamond:1285018724277162067>", 
        "<:MonsterHunter:1315007368005816392>", "<:Rainbow6Siege:1316748311452979290>", "<:Gmod:1318524287988142102>"
    ]  
    description = (
        "Ειδικοί ρόλοι για να δείξεις στον server ότι ψάχνεις κόσμο για games.\n\n"
        "Ψάχνω για:\n\n"
        ":speech_balloon: **Κόσμο για παρέα**\n"
        ":video_game: **Γενικά, ότι game θέλετε**\n"
        "<:Valorant:1315005904411693076> **Valorant**\n"
        "<:LeagueofLegends:1315005449413722122> **League of Legends**\n"
        "<:diamond:1285018724277162067> **Minecraft**\n"
        "<:MonsterHunter:1315007368005816392> **Monster Hunter**\n"
        "<:Rainbow6Siege:1316748311452979290> **Rainbow 6 Siege**\n"
        "<:Gmod:1318524287988142102> **Garry's Mod**\n\n"
        "Για να αφαιρέσεις το ρόλο, ξαναπάτα το reaction emoji."
    )

    embed = discord.Embed(
        colour=discord.Colour.blue(),
        description=description,
    )
    message = await ctx.send(embed=embed)

    for reaction in reactions:
        await message.add_reaction(reaction)

    await ctx.message.delete()


@bot.event
async def on_raw_reaction_add(payload):
    if payload.message_id == TARGET_MESSAGE_ID:
        guild = bot.get_guild(payload.guild_id)
        
        # Handling custom emoji
        if payload.emoji.is_custom_emoji(): emoji_identifier = f"<:{payload.emoji.name}:{payload.emoji.id}>"
        else: emoji_identifier = payload.emoji.name

        role_name = reaction_roles.get(emoji_identifier) # Fetch the role name using the emoji identifier

        if role_name:
            role = discord.utils.get(guild.roles, name=role_name)
            if role:
                member = guild.get_member(payload.user_id) 
                
                for other_role in reaction_roles.values(): # Remove other roles before adding the new one
                    if other_role != role_name:
                        other_role_obj = discord.utils.get(member.guild.roles, name=other_role)
                        if other_role_obj in member.roles:
                            await member.remove_roles(other_role_obj)
                            print(f"Removed {other_role} from {member.name}")

            if payload.user_id in reaction_timers:
                    # If the user has a timer, remove their current role and reset the timer
                    existing_role = reaction_timers[payload.user_id]['role']
                    if existing_role in member.roles:
                        await member.remove_roles(existing_role)
                        print(f"Removed {existing_role.name} from {member.name} due to new role")
                        del reaction_timers[payload.user_id] 
                           
            await member.add_roles(role)
            print(f"Added {role_name} to {member.name}")

            reaction_timers[payload.user_id] = {
                    'role': role,
                    'timestamp': asyncio.get_event_loop().time()  # Store the time of reaction
            }
            
            await asyncio.sleep(3600)  # 1 hour in seconds

            # After 1 hour, remove the reaction and role
            if payload.user_id in reaction_timers:
                # Check if the user still has the role after the time has passed
                if role in member.roles:
                    await member.remove_roles(role)
                    print(f"Removed {role_name} from {member.name} after 1 hour")
                        
                # Remove the user from the dictionary
                del reaction_timers[payload.user_id]



@bot.event
async def on_raw_reaction_remove(payload):
    if payload.message_id == TARGET_MESSAGE_ID:
        guild = bot.get_guild(payload.guild_id)

    if payload.emoji.is_custom_emoji(): emoji_identifier = f"<:{payload.emoji.name}:{payload.emoji.id}>"
    else: emoji_identifier = payload.emoji.name

    role_name = reaction_roles.get(emoji_identifier) # Fetch the role name using the emoji identifier

    if role_name:
            role = discord.utils.get(guild.roles, name=role_name)
            if role:
                member = guild.get_member(payload.user_id) 
                await member.remove_roles(role)
                if role in member.roles:
                    await member.remove_roles(role)
                    print(f"Removed {role_name} from {member.name} after 1 hour")
                    del reaction_timers[payload.user_id]
                print(f"Removed {role_name} from {member.name}")


bot.run(TOKEN)