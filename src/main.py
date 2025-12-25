import discord
from discord.ext import commands
import datetime
import os
from dotenv import load_dotenv
from db import Database

# 환경 변수 로드
load_dotenv()

# 봇의 설정
intents = discord.Intents.default()
intents.message_content = True  # 메시지 내용을 읽기 위한 설정
bot = commands.Bot(command_prefix='!', intents=intents)

# 데이터베이스 인스턴스 생성
db = Database()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.event
async def on_message(message):
    print(f"새 메시지 감지됨: {message.author} - {message.content}")

    # 봇이 쓴 메시지는 무시 (무한 루프 방지)
    if message.author == bot.user:
        return

    # PostgreSQL 데이터베이스에 저장
    try:
        # 메시지 URL 생성
        message_url = f"https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}"
        
        # 메시지 생성 시간
        published_at = message.created_at.replace(tzinfo=None)
        
        # 데이터베이스에 저장
        db.save_chat_message(
            message_content=message.content,
            author=message.author,
            channel_name=message.channel.name,
            message_id=message.id,
            message_url=message_url,
            published_at=published_at
        )
    except Exception as e:
        print(f"데이터베이스 저장 중 오류: {e}")

    # 이 코드가 있어야 다른 봇 명령어들이 정상 작동함
    await bot.process_commands(message)

@bot.event
async def on_disconnect():
    """봇이 종료될 때 데이터베이스 연결 종료"""
    db.close()

# 환경 변수에서 봇 토큰 가져오기
bot_token = os.getenv('DISCORD_BOT_TOKEN')
if not bot_token:
    print("오류: DISCORD_BOT_TOKEN 환경 변수가 설정되지 않았습니다.")
    exit(1)

bot.run(bot_token)

