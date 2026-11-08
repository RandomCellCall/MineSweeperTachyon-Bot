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

bomb_pool = [
    {"rate": 1.0, "duration": 5}
]

bomb_leaderboard = {}

GIF_BOOM = "https://cdn.discordapp.com/attachments/1568209853644808284/1568576458555920504/twitter-gif-2012951877365731428_6aedcee94dc3c.gif?ex=6af0faea&is=6aefa96a&hm=d917a2dac868309bc8b8bc59b9a312a6bdb69884acd6b16851ed8e93a5f9fbf0&"
GIF_SAFE = "https://cdn.discordapp.com/attachments/1568209853644808284/1568576458023112774/FHd3gGzeCQAV2e5H3J.gif?ex=6af0faea&is=6aefa96a&hm=8a6751135168051c4ec36490da0deb5bf4b01f21122211754fd1feb55dbabc26&"
GIF_ADMIN = "https://cdn.discordapp.com/attachments/1568209853644808284/1568576457398034543/GDMVHQ9mFLCPUuNiPZop.gif?ex=6af0faea&is=6aefa96a&hm=436dc2da900fbf85432eb21c8c2dedb1f898afcbebd2c0cb1800d6a3ca938f2f&"
GIF_LEADERBOARD = "https://cdn.discordapp.com/attachments/1568209853644808284/1568914176494149682/kvG34LTIqAuTuZ8q39D.gif?ex=6af18cb0&is=6af03b30&hm=93214d8b4c65e4418f9aee024080a6c6e26fac25a0a1e1097eb63256ffcd1d3f&"

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

@bot.command(name='addbomb')
@commands.has_permissions(administrator=True)
async def add_bomb(ctx, rate: float, duration: int):
    global bomb_pool
    bomb_pool.append({"rate": rate, "duration": duration})
    
    total_rate = sum(b["rate"] for b in bomb_pool)
    await ctx.send(f"✅ Đã thêm loại mìn mới: Tỉ lệ `{rate * 100}%`, Timeout `{duration}s`. (Tổng tỉ lệ pool hiện tại: `{total_rate * 100}%`).")

@bot.command(name='removebomb')
@commands.has_permissions(administrator=True)
async def remove_bomb(ctx, rate: float, duration: int):
    global bomb_pool
    target = {"rate": rate, "duration": duration}
    if target in bomb_pool:
        if len(bomb_pool) == 1:
            await ctx.send("⚠️ Không thể xóa hết tất cả các loại mìn trong pool! Phải giữ lại ít nhất 1 loại (Đừng mang hết đi chứ!).")
            return
        bomb_pool.remove(target)
        total_rate = sum(b["rate"] for b in bomb_pool)
        await ctx.send(f"🗑️ Đã xóa mìn (Tỉ lệ: `{rate * 100}%`, Timeout: `{duration}s`). (Tổng tỉ lệ pool hiện tại: `{total_rate * 100}%`).")
    else:
        await ctx.send("❌ Loại mìn này chưa được chôn xuống!.")

@bot.command(name='bomblist')
async def bomb_list(ctx):
    total_rate = sum(b["rate"] for b in bomb_pool)
    embed = discord.Embed(
        title="💣 Danh Sách số lượng bomb đã chôn (Đừng báo Tazuna biết).",
        description=f"Tổng tỉ lệ cấu hình: **{total_rate * 100}%**",
        color=discord.Color.blue()
    )
    
    for idx, bomb in enumerate(bomb_pool, 1):
        embed.add_field(
            name=f"Loại mìn #{idx}",
            value=f"• Tỉ lệ dẫm: **{bomb['rate'] * 100}%**\n• Thời gian phạt: **{bomb['duration']} giây**",
            inline=False
        )
    await ctx.send(embed=embed)

@bot.command(name='bombleaderboard')
async def bomb_leaderboard_cmd(ctx):
    embed = discord.Embed(
        title="🏆 Bảng Xếp Hạng Dẫm Mìn",
        description="Các chuột lang giẫm nhiều thật đấy. Cố gắng thêm đi nhé.",
        color=discord.Color.gold()
    )
    
    if not bomb_leaderboard:
        embed.add_field(name="Chưa có dữ liệu", value="Chưa có ai dẫm phải mìn cả! (Chán thật)", inline=False)
    else:
        sorted_lb = sorted(bomb_leaderboard.items(), key=lambda item: item[1], reverse=True)[:10]
        lb_text = ""
        for rank, (user_id, count) in enumerate(sorted_lb, 1):
            user = ctx.guild.get_member(user_id)
            name = user.mention if user else f"User ID: {user_id}"
            lb_text += f"**#{rank}** - {name}: **{count}** lần\n"
        embed.add_field(name="Thành tích", value=lb_text, inline=False)
        
    if GIF_LEADERBOARD and GIF_LEADERBOARD != "https://cdn.discordapp.com/attachments/1568209853644808284/1568914176494149682/kvG34LTIqAuTuZ8q39D.gif?ex=6af18cb0&is=6af03b30&hm=93214d8b4c65e4418f9aee024080a6c6e26fac25a0a1e1097eb63256ffcd1d3f&":
        embed.set_image(url=GIF_LEADERBOARD)
        
    await ctx.send(embed=embed)

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

    rand_val = random.random()
    cumulative = 0.0
    triggered_bomb = None

    for bomb in bomb_pool:
        cumulative += bomb["rate"]
        if rand_val <= cumulative:
            triggered_bomb = bomb
            break
    
    if not triggered_bomb:
        return

    if has_safe_role:
        embed_safe = discord.Embed(
            description=f"Chuột lang {message.author.mention}! Đó là vị trí tôi đặt bo- Không nổ à?",
            color=discord.Color.green()
        )
        embed_safe.set_image(url=GIF_SAFE)
        await message.channel.send(embed=embed_safe)
        
    elif is_admin:
        embed_boom = discord.Embed(
            description=f"Chuột lang {message.author.mention}! Cậu giẫm phải mìn nghiên cứu loại **{triggered_bomb['duration']}s** rồi! Ủa...là Cafe đấy à? Không có gì đâuuuu!",
            color=discord.Color.red()
        )
        embed_boom.set_image(url=GIF_ADMIN)
        await message.channel.send(embed=embed_boom)
        
    else:
        user_id = message.author.id
        bomb_leaderboard[user_id] = bomb_leaderboard.get(user_id, 0) + 1
        
        timeout_duration = triggered_bomb["duration"]
        try:
            duration = timedelta(seconds=timeout_duration)
            await message.author.timeout(duration, reason=f"Dẫm phải mìn {timeout_duration}s do Tachyon đặt!")
            
            embed_boom = discord.Embed(
                description=f"Chuột lang {message.author.mention}! Cậu giẫm phải mìn nghiên cứu loại **{timeout_duration} giây** rồi, phải mang cậu đi chữa trị thôi!",
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