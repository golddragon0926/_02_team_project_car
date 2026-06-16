import pandas as pd

df = pd.read_csv("보조금데이터.csv", encoding="utf-8-sig")

print("=== 수집된 시도 목록 ===")
sido_list = sorted(df["시도"].unique().tolist())
print(sido_list)
print(f"\n총 {len(sido_list)}개 시도")

print("\n=== 빠진 시도 확인 ===")
all_sido = ["서울", "부산", "대구", "인천", "광주", "대전", "울산",
            "세종", "경기", "강원", "충북", "충남", "전북", "전남",
            "경북", "경남", "제주"]

missing = [s for s in all_sido if s not in sido_list]
print(f"빠진 시도: {missing}")

print("\n=== 시도별 데이터 수 ===")
print(df["시도"].value_counts())