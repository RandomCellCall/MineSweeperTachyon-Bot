import os
import random
import discord
from discord.ext import commands
from dotenv import load_dotenv
from datetime import timedelta
from flask import Flask
from threading import Thread

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

app = Flask('')

@app.route('/')
def home():
    return "Bot is running 24/7!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

bomb_channels = set()
safe_roles = set()
MINE_CHANCE = 0.05
TIMEOUT_DURATION = 5

GIF_BOOM = "https://cdn.discordapp.com/attachments/1568209853644808284/1568576458555920504/twitter-gif-2012951877365731428_6aedcee94dc3c.gif?ex=6af0522a&is=6aef00aa&hm=565720bad624beeaa974a353d3681d740a00ccb5d958d71263dc4c6a7ad2a740&"
GIF_SAFE = "https://cdn.discordapp.com/attachments/1568209853644808284/1568576458023112774/FHd3gGzeCQAV2e5H3J.gif?ex=6af0522a&is=6aef00aa&hm=39dbcbb29b963c86a17a351e6479599b5212eaa4f803dc3289415c0a42a5c0bb&"
GIF_ADMIN = "https://cdn.discordapp.com/attachments/1568209853644808284/1568576457398034543/GDMVHQ9mFLCPUuNiPZop.gif?ex=6af0522a&is=6aef00aa&hm=c171c4b927d99d4c8e19f892d8ec0ea0aebea0736e977ed40cfe4d2641c24600&"

@bot.event
async def on_ready():
    print(f'Bot {bot.user.name} đã sẵn sàng hoạt động!')

@bot.command(name='enablebomb')
@commands.has_permissions(administrator=True)
async def enable_bomb(ctx, channel: discord.TextChannel = None):
    target_channel = channel or ctx.channel
    bomb_channels.add(target_channel.id)
    await ctx.send(f"⚠️ Đã đặt mìn tại kênh {target_channel.mention}. Mong không có chuột lang nào dẫm phải!")

@bot.command(name='disablebomb')
@commands.has_permissions(administrator=True)
async def disable_bomb(ctx, channel: discord.TextChannel = None):
    target_channel = channel or ctx.channel
    if target_channel.id in bomb_channels:
        bomb_channels.remove(target_channel.id)
        await ctx.send(f"🛡️ Kênh {target_channel.mention} đã được Tazuna bốc sạch mìn mang đi.")
    else:
        await ctx.send("Kênh này không có tý mìn nào.")

@bot.command(name='setunbombrole')
@commands.has_permissions(administrator=True)
async def set_safe_role(ctx, role: discord.Role):
    safe_roles.add(role.id)
    await ctx.send(f"Role {role.mention} đã được cấp khiên chống mìn.")

@bot.command(name='removeunbombrole')
@commands.has_permissions(administrator=True)
async def remove_safe_role(ctx, role: discord.Role):
    if role.id in safe_roles:
        safe_roles.remove(role.id)
        await ctx.send(f"Role {role.mention} đã bị hủy khiên chống mìn.")
    else:
        await ctx.send("Role này hiện tại chưa an toàn.")

@bot.command(name='setbomb')
@commands.has_permissions(administrator=True)
async def set_bomb(ctx, chance: float, seconds: int):
    global MINE_CHANCE, TIMEOUT_DURATION
    MINE_CHANCE = chance
    TIMEOUT_DURATION = seconds
    await ctx.send(f"Đã cập nhật thông số mìn: Tỉ lệ nổ {chance * 100}%, Thời gian timeout {seconds} giây.")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    await bot.process_commands(message)

    if message.channel.id not in bomb_channels:
        return

    user_role_ids = [role.id for role in message.author.roles]
    
    has_safe_role = any(role_id in safe_roles for role_id in user_role_ids)
    is_admin = message.author.guild_permissions.administrator

    has_hit_mine = random.random() < MINE_CHANCE

    if has_hit_mine:
        if has_safe_role:
            embed_safe = discord.Embed(
                description=f"Chuột lang {message.author.mention}! Đó là vị trí tôi đặt bo- Không nổ à?",
                color=discord.Color.green()
            )
            embed_safe.set_image(url=GIF_SAFE)
            await message.channel.send(embed=embed_safe)
            
        elif is_admin:
            embed_boom = discord.Embed(
                description=f"Chuột lang {message.author.mention}! Cậu giẫm phải mìn nghiên cứu rồi! Ủa, Cafe đấy đấy à? Không có gì đâuuu.",
                color=discord.Color.red()
            )
            embed_boom.set_image(url=GIF_ADMIN)
            await message.channel.send(embed=embed_boom)
            
        else:
            try:
                duration = timedelta(seconds=TIMEOUT_DURATION)
                await message.author.timeout(duration, reason="Dẫm phải mìn do Tachyon đặt!")
                
                embed_boom = discord.Embed(
                    description=f"Chuột lang {message.author.mention}! Cậu giẫm phải mìn nghiên cứu rồi! Tazuna bảo cậu phải đi chữa trị trong {TIMEOUT_DURATION} giây đấy, nằm im nào!",
                    color=discord.Color.red()
                )
                embed_boom.set_image(url=GIF_BOOM)
                
                await message.channel.send(embed=embed_boom)
            except discord.Forbidden:
                pass
            except Exception:
                pass

if __name__ == "__main__":
    keep_alive()
    bot.run(TOKEN)