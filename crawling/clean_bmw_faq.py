import pandas as pd
import re
import os

# ① CSV 읽기
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
csv_path = os.path.join(BASE_DIR, "data", "bmw_faq_data.csv")
df = pd.read_csv(csv_path, encoding="utf-8-sig")

print("=== 정리 전 ===")
print(df["content"].head(5))

# ② 앞에 붙은 숫자 제거 (점/공백 없이 바로 붙은 것도 제거)
def remove_leading_numbers(text):
    text = str(text).strip()
    # 앞에 있는 숫자 전부 제거 (점, 공백 유무 상관없이)
    text = re.sub(r'^\d+', '', text)
    # 제거 후 앞에 남은 공백/점 제거
    text = text.lstrip('.\s ')
    return text.strip()

df["content"] = df["content"].apply(remove_leading_numbers)

# ③ 0번 행 (Skip to AI...) 제거
df = df[~df["content"].str.startswith("Skip to")]
df = df.reset_index(drop=True)

# ④ title == category인 잘못된 행 제거 (카테고리명이 타이틀로 들어간 중복 행)
df = df[df["title"] != df["category"]]
df = df.reset_index(drop=True)

# ⑤ 중복 제거
df = df.drop_duplicates()
df = df.reset_index(drop=True)

print("\n=== 정리 후 ===")
print(df["content"].head(5))
print(f"\n총 {len(df)}개")

# ⑤ 저장
df.to_csv(csv_path, index=False, encoding="utf-8-sig")
print("저장 완료! ✅")