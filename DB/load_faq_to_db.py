"""
5개 FAQ CSV(bmw, hyundai, kgm, kia, opinet)를 합쳐서
MySQL car_oil_db.FAQ 테이블에 적재하는 스크립트

사용법:
    python load_faq_to_db.py
"""

import os
import re
import pandas as pd
import pymysql
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME", "car_oil_db"),
    "charset": "utf8mb4",
}

BASE_PATH = os.getcwd()

# brand별 원본 CSV 경로 (raw 파일 위치는 환경에 맞게 수정하세요)
FAQ_SOURCES = {
    "현대자동차": os.path.join(BASE_PATH, "../data", "faq", "hyundai_faq_data.csv"),
    "기아자동차": os.path.join(BASE_PATH, "../data", "faq", "kia_faq_data.csv"),
    "오피넷": os.path.join(BASE_PATH, "../data", "faq", "opinet_faq_data.csv"),
    "BMW": os.path.join(BASE_PATH, "../data", "faq", "bmw_faq_data.csv"),
    "KGM": os.path.join(BASE_PATH, "../data", "faq", "kgm_faq_data.csv"),
}


def clean_text(text):
    if pd.isna(text):
        return ""
    return re.sub(r"\s+", " ", str(text)).strip()


def load_and_merge():
    combined = []
    for brand, path in FAQ_SOURCES.items():
        if not os.path.exists(path):
            print(f"⚠️ 파일 없음, 스킵: {path}")
            continue

        df = pd.read_csv(path, encoding="utf-8-sig", on_bad_lines="skip")

        # 컬럼명 표준화
        rename_dict = {}
        for col in df.columns:
            if col in ["질문", "질문(Question)", "Title"]:
                rename_dict[col] = "title"
            elif col in ["답변", "답변(Answer)", "Content"]:
                rename_dict[col] = "content"
            elif col == "분류":
                rename_dict[col] = "category"
        if rename_dict:
            df = df.rename(columns=rename_dict)

        df["title"] = df["title"].apply(clean_text)
        df["content"] = df["content"].apply(clean_text)

        if "category" not in df.columns:
            df["category"] = None
        else:
            df["category"] = df["category"].apply(
                lambda x: None if pd.isna(x) else clean_text(x)
            )

        df["brand"] = brand
        combined.append(df[["brand", "title", "content", "category"]])

        print(f"✅ {brand}: {len(df)}건 로드")

    merged = pd.concat(combined, ignore_index=True)
    merged = merged.drop_duplicates(subset=["title", "brand"])
    print(f"\n총 병합 건수: {len(merged)}건")
    return merged


def insert_to_db(df):
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # 기존 FAQ 데이터 초기화 (재실행 대비)
    cursor.execute("TRUNCATE TABLE FAQ")

    insert_sql = """
        INSERT INTO FAQ (brand, title, content, category)
        VALUES (%s, %s, %s, %s)
    """

    rows = [
        (row.brand, row.title, row.content, row.category)
        for row in df.itertuples(index=False)
    ]

    cursor.executemany(insert_sql, rows)
    conn.commit()

    print(f"✅ DB 적재 완료: {cursor.rowcount}건")

    cursor.close()
    conn.close()


if __name__ == "__main__":
    merged_df = load_and_merge()
    insert_to_db(merged_df)
