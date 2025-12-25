import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime
import time

load_dotenv()

class Database:
    def __init__(self, max_retries=5, retry_delay=5):
        self.conn = None
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.connect()

    def connect(self):
        """PostgreSQL 데이터베이스에 연결 (재시도 로직 포함)"""
        for attempt in range(self.max_retries):
            try:
                self.conn = psycopg2.connect(
                    host=os.getenv('DB_HOST', 'localhost'),
                    port=os.getenv('DB_PORT', '5432'),
                    database=os.getenv('DB_NAME'),
                    user=os.getenv('DB_USER'),
                    password=os.getenv('DB_PASSWORD')
                )
                print("데이터베이스 연결 성공")
                return
            except Exception as e:
                if attempt < self.max_retries - 1:
                    print(f"데이터베이스 연결 실패 (시도 {attempt + 1}/{self.max_retries}): {e}")
                    print(f"{self.retry_delay}초 후 재시도...")
                    time.sleep(self.retry_delay)
                else:
                    print(f"데이터베이스 연결 최종 실패: {e}")
                    raise

    def close(self):
        """데이터베이스 연결 종료"""
        if self.conn:
            self.conn.close()
            print("데이터베이스 연결 종료")

    def save_chat_message(self, message_content, author, channel_name, message_id, message_url=None, published_at=None):
        """
        Discord 메시지를 news_articles 테이블에 저장
        
        Args:
            message_content: 메시지 내용
            author: 메시지 작성자
            channel_name: 채널 이름
            message_id: 메시지 ID
            message_url: 메시지 URL (선택)
            published_at: 메시지 생성 시간 (선택)
        """
        try:
            # URL이 제공되지 않으면 고유 URL 생성
            if not message_url:
                # 메시지 ID와 채널을 기반으로 고유 URL 생성
                unique_id = f"discord_{channel_name}_{message_id}"
                message_url = f"https://discord.com/channels/{channel_name}/{message_id}"
            
            # 메시지 내용을 title과 content로 분리
            # 첫 줄을 title로, 나머지를 content로 사용
            lines = message_content.strip().split('\n', 1)
            title = lines[0] if lines else message_content  # title은 text 타입이므로 제한 없음
            content = lines[1] if len(lines) > 1 else message_content
            
            # 스키마 제약 조건에 맞게 데이터 길이 제한
            # url: character varying(1000)
            if len(message_url) > 1000:
                message_url = message_url[:1000]
            
            # author: character varying(255)
            # Discord User 객체에서 이름 추출
            if hasattr(author, 'name'):
                author_name = author.name
            elif hasattr(author, 'display_name'):
                author_name = author.display_name
            else:
                author_name = str(author)
            author_name = author_name[:255] if len(author_name) > 255 else author_name
            
            # source: character varying(255)
            source = f"discord_{channel_name}"[:255]
            
            # published_at이 없으면 현재 시간 사용
            if not published_at:
                published_at = datetime.now()
            
            with self.conn.cursor() as cur:
                # 중복 체크 (url이 UNIQUE이므로)
                cur.execute(
                    "SELECT id FROM news_articles WHERE url = %s",
                    (message_url,)
                )
                if cur.fetchone():
                    print(f"이미 존재하는 메시지: {message_url}")
                    return False
                
                # 데이터 삽입
                cur.execute("""
                    INSERT INTO news_articles (
                        url, title, content, author, source, 
                        published_at, collected_at, updated_at, status
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (url) DO NOTHING
                    RETURNING id
                """, (
                    message_url,
                    title,
                    content,
                    author_name,
                    source,
                    published_at,
                    datetime.now(),
                    datetime.now(),
                    'active'
                ))
                
                result = cur.fetchone()
                self.conn.commit()
                
                if result:
                    print(f"메시지 저장 성공: ID {result[0]}")
                    return True
                else:
                    print("메시지 저장 실패 (중복 또는 오류)")
                    return False
                    
        except psycopg2.IntegrityError as e:
            # UNIQUE 제약 조건 위반 (이미 존재하는 URL)
            self.conn.rollback()
            print(f"중복된 메시지: {message_url}")
            return False
        except Exception as e:
            self.conn.rollback()
            print(f"메시지 저장 중 오류 발생: {e}")
            return False

    def __del__(self):
        """소멸자에서 연결 종료"""
        self.close()

