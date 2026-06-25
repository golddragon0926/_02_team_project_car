from dotenv import load_dotenv
import os

load_dotenv()

OPINET_API_KEY      = os.getenv('OPINET_API_KEY')
PUBLIC_API_KEY      = os.getenv('PUBLIC_API_KEY')
NAVER_CLIENT_ID     = os.getenv('NAVER_CLIENT_ID')
NAVER_CLIENT_SECRET = os.getenv('NAVER_CLIENT_SECRET')

# DB는 데이터 수집할 때만 필요 (CSV 배포 시 불필요)
DB_CONFIG = {
    "host"    : "localhost",
    "user"    : "skn_ai",
    "password": "1234",
    "port"    : 3306,
    "db"      : "car_project",
    "charset" : "utf8mb4"
}