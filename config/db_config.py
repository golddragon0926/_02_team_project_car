from dotenv import load_dotenv
import os

load_dotenv()

OPINET_API_KEY = os.getenv('OPINET_API_KEY')
PUBLIC_API_KEY = os.getenv('PUBLIC_API_KEY')

DB_CONFIG = {
    "host"    : os.getenv('DB_HOST', 'localhost'),
    "port"    : int(os.getenv('DB_PORT', 3306)),
    "user"    : os.getenv('DB_USER', 'root'),
    "password": os.getenv('DB_PASSWORD'),
    "database": os.getenv('DB_NAME', 'car_oil_db'),
    "charset" : "utf8mb4"
}