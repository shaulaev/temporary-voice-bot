import discord
from discord.ext import commands

import os
from dotenv import load_dotenv
load_dotenv()

token = os.getenv("BOT_TOKEN")

intents = discord.Intents.default()
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ID голосового канала-триггера (создаёшь вручную в Discord)
TRIGGER_CHANNEL_ID = 1374469123798597745  # ← замени на свой ID

# Словарь для отслеживания созданных каналов
user_temp_channels = {}

@bot.event
async def on_voice_state_update(member, before, after):
    guild = member.guild

    # Если пользователь вошёл в триггер-канал
    if after.channel and after.channel.id == TRIGGER_CHANNEL_ID:
        # Создание временного канала
        channel_name = f"🔊 Комната {member.display_name}"

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(connect=True, view_channel=True),
            member: discord.PermissionOverwrite(manage_channels=True, connect=True, speak=True)
        }

        temp_channel = await guild.create_voice_channel(
            name=channel_name,
            overwrites=overwrites,
            category=after.channel.category  # чтобы было в той же категории
        )

        user_temp_channels[member.id] = temp_channel.id

        # Переместим пользователя в новый канал
        await member.move_to(temp_channel)

    # Проверка: если пользователь покинул свой временный канал — удалить его, если он пуст
    for user_id, channel_id in list(user_temp_channels.items()):
        channel = guild.get_channel(channel_id)
        if channel and len(channel.members) == 0:
            await channel.delete()
            del user_temp_channels[user_id]

bot.run(token)
