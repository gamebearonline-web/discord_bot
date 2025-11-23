import os
import threading
from flask import Flask
import discord
from discord.ext import commands
import requests
import io
import time
from datetime import datetime
import pytz   # ← JST 取得に必要

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
BASE_IMAGE_URL = "https://raw.githubusercontent.com/gamebearonline-web/spl3_X_Bot/main/Thumbnail/Thumbnail.png"

# ==============================
# Discord BOT の設定
# ==============================
intents = discord.Intents.default()
intents.message_content = True  # 必須！
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.tree.command(
    name="schedule",
    description="最新のスケジュール画像を送信します（日時入り）"
)
async def schedule(interaction: discord.Interaction):
    await interaction.response.defer()

    # JST 現在時刻（正確版）
    jst = pytz.timezone("Asia/Tokyo")
    now = datetime.now(jst)
    time_str = now.strftime("🗓️ %Y年%-m月%-d日　🕛 %-H時更新")

    # キャッシュ防止（最新画像確実取得）
    image_url = f"{BASE_IMAGE_URL}?t={int(time.time())}"

    try:
        img_bytes = requests.get(image_url, timeout=10).content
        file = discord.File(io.BytesIO(img_bytes), filename="schedule.png")
    except Exception as e:
        await interaction.followup.send(f"画像取得に失敗：{e}")
        return

    await interaction.followup.send(content=time_str, file=file)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await bot.tree.sync()   # Slash commands 同期
    print("Slash commands synced")


# ==============================
# Flask（Railway Ping / ヘルスチェック）
# ==============================
app = Flask(__name__)

@app.route("/")
def home():
    return "Running OK"


# ==============================
# Discord BOT（別スレッド起動）
# ==============================
def run_discord_bot():
    bot.run(TOKEN)


if __name__ == "__main__":
    # Discord bot スレッド起動
    thread = threading.Thread(target=run_discord_bot)
    thread.start()

    # Railway が要求する PORT で Flask 起動
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
