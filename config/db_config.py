from dotenv import load_dotenv
import os

load_dotenv()

OPINET_API_KEY      = os.getenv('OPINET_API_KEY')
PUBLIC_API_KEY      = os.getenv('PUBLIC_API_KEY')
NAVER_CLIENT_ID     = os.getenv('NAVER_CLIENT_ID')
NAVER_CLIENT_SECRET = os.getenv('NAVER_CLIENT_SECRET')

# DB는 데이터 수집할 때만 필요 (CSV 배포 시 불필요)
DB_CONFIG = {
    "host"    : os.getenv('DB_HOST', 'localhost'),
    "port"    : int(os.getenv('DB_PORT', 3306)),
    "user"    : os.getenv('DB_USER', 'root'),
    "password": os.getenv('DB_PASSWORD'),
    "database": os.getenv('DB_NAME', 'car_oil_db'),
    "charset" : "utf8mb4",
}