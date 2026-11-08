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

GLOBAL_HIT_CHANCE = 0.05

bomb_pool = [
    {"weight": 50.0, "duration": 5},
    {"weight": 50.0, "duration": 30}
]

bomb_leaderboard = {}

GIF_BOOM = "https://cdn.discordapp.com/attachments/1568209853644808284/1568576458555920504/twitter-gif-2012951877365731428_6aedcee94dc3c.gif?ex=6af1a3aa&is=6af0522a&hm=83dc4154c3c5c642bc5a5a049e5807d2a05d85c18c4c9c1dbd0d7794faed3b89&"
GIF_SAFE = "https://cdn.discordapp.com/attachments/1568209853644808284/1568576458023112774/FHd3gGzeCQAV2e5H3J.gif?ex=6af1a3aa&is=6af0522a&hm=93b279c299daf782ce941a86674ac6d82d3d5c4f0b118a188c144236e213726a&"
GIF_ADMIN = "https://cdn.discordapp.com/attachments/1568209853644808284/1568576457398034543/GDMVHQ9mFLCPUuNiPZop.gif?ex=6af1a3aa&is=6af0522a&hm=41eeb29a556cdb04d83bcf2cb5e312ee31570e8115084686153870d64650155c&"
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

@bot.command(name='bombrateset')
@commands.has_permissions(administrator=True)
async def bomb_rate_set(ctx, chance: float):
    global GLOBAL_HIT_CHANCE
    GLOBAL_HIT_CHANCE = chance
    await ctx.send(f"⚙️ Đã đặt tỉ lệ dẫm phải mìn thành: **{chance * 100}%**")

@bot.command(name='addbomb')
@commands.has_permissions(administrator=True)
async def add_bomb(ctx, weight: float, duration: int):
    global bomb_pool
    bomb_pool.append({"weight": weight, "duration": duration})
    await ctx.send(f"✅ Đã thêm loại mìn: Trọng số/Tỉ lệ pool `{weight}%`, Timeout `{duration}s`.")

@bot.command(name='removebomb')
@commands.has_permissions(administrator=True)
async def remove_bomb(ctx, weight: float, duration: int):
    global bomb_pool
    target = {"weight": weight, "duration": duration}
    if target in bomb_pool:
        if len(bomb_pool) == 1:
            await ctx.send("⚠️ Phải giữ lại ít nhất 1 loại mìn trong pool (Đừng gỡ hết chúng chứ)!")
            return
        bomb_pool.remove(target)
        await ctx.send(f"🗑️ Đã xóa mìn (Trọng số: `{weight}%`, Timeout: `{duration}s`).")
    else:
        await ctx.send("❌ Loại mìn này chưa từng được chôn xuống (Sai thông số).")

@bot.command(name='bomblist')
async def bomb_list(ctx):
    total_weight = sum(b["weight"] for b in bomb_pool)
    embed = discord.Embed(
        title="💣 Danh Sách Các Phân Loại Mìn",
        description=f"Tỉ lệ dẫm mìn tổng cấu hình (`!bombrateset`): **{GLOBAL_HIT_CHANCE * 100}%**",
        color=discord.Color.blue()
    )
    embed.add_field(name="Tỉ lệ tổng dẫm mìn", value=f"{GLOBAL_HIT_CHANCE * 100}%", inline=False)
    
    for idx, bomb in enumerate(bomb_pool, 1):
        actual_chance = (bomb["weight"] / total_weight) * 100 if total_weight > 0 else 0
        embed.add_field(
            name=f"Loại mìn #{idx}",
            value=f"• Trọng số pool: **{bomb['weight']}** (~**{actual_chance:.1f}%** khi dẫm)\n• Thời gian phạt: **{bomb['duration']} giây**",
            inline=False
        )
    await ctx.send(embed=embed)

@bot.command(name='bombleaderboard')
async def bomb_leaderboard_cmd(ctx):
    embed = discord.Embed(
        title="🏆 Bảng Xếp Hạng Dẫm Mìn",
        description="Vinh danh những 'chuột lang' cống hiến nhất cho Tachyon!",
        color=discord.Color.gold()
    )
    
    if not bomb_leaderboard:
        embed.add_field(name="Chưa có dữ liệu", value="Chưa có ai dẫm phải mìn cả!", inline=False)
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

    # CHU KÌ 1: Roll tỉ lệ dẫm phải mìn chung của user
    has_hit_mine = random.random() < GLOBAL_HIT_CHANCE

    if not has_hit_mine:
        return

    # CHU KÌ 2: Random loại bomb user sẽ mắc phải dựa vào pool bomb (dùng random.choices theo trọng số weight)
    weights = [b["weight"] for b in bomb_pool]
    triggered_bomb = random.choices(bomb_pool, weights=weights, k=1)[0]

    if has_safe_role:
        embed_safe = discord.Embed(
            description=f"Chuột lang {message.author.mention}! Đó là vị trí tôi đặt bo- Không nổ à? Sao lại thế nhỉ...? (Do có role an toàn.)",
            color=discord.Color.green()
        )
        embed_safe.set_image(url=GIF_SAFE)
        await message.channel.send(embed=embed_safe)
        
    elif is_admin:
        embed_boom = discord.Embed(
            description=f"Chuột lang {message.author.mention}! Cậu giẫm phải mìn nghiên cứu loại **{triggered_bomb['duration']}s** rồi. Ủa? Cafe đấy à? Không có gì đâuuu. (Do quyền hạn nên không thể timeout)",
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
                description=f"Chuột lang {message.author.mention}! Cậu giẫm phải mìn nghiên cứu loại **{timeout_duration} giây** rồi! Phải mang cậu đi chữa trị thôi!",
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