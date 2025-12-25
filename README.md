# Discord 봇 - PostgreSQL 연동

Discord 메시지를 PostgreSQL 데이터베이스에 저장하는 봇입니다.

## Docker 환경에서 실행

### 1. 환경 변수 설정

`.env` 파일을 생성하고 다음 내용을 입력하세요:

```env
# PostgreSQL 설정 (외부 데이터베이스)
DB_HOST=your_db_host
DB_PORT=5432
DB_NAME=your_database_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password

# Discord 봇 토큰
DISCORD_BOT_TOKEN=your_discord_bot_token_here
```

### 2. Docker Compose로 실행

```bash
# 서비스 빌드 및 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f bot

# 서비스 중지
docker-compose down
```

### 3. 서비스 관리

```bash
# 봇 재시작
docker-compose restart bot

# 봇 로그 확인
docker-compose logs -f bot
```

## 로컬 환경에서 실행

### 1. 패키지 설치

```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env` 파일을 생성하고 다음 내용을 입력하세요:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=fnnews
DB_USER=postgres
DB_PASSWORD=postgres
DISCORD_BOT_TOKEN=your_discord_bot_token_here
```

### 3. 봇 실행

```bash
python src/main.py
```
