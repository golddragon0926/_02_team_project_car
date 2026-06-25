#---------------------------
#CSV 확인 코드
#---------------------------

import pandas as pd

df = pd.read_csv("data/보조금데이터.csv", encoding="cp949")

# ① 컬럼 목록
print("=== 컬럼 목록 ===")
print(df.columns.tolist())

# ② 상위 5개 데이터
print("\n=== 상위 5개 데이터 ===")
print(df.head())

# ③ 총 데이터 수
print("\n=== 총 데이터 수 ===")
print(f"행: {df.shape[0]}개 / 열: {df.shape[1]}개")

# ④ 시도 목록
print("\n=== 수집된 시도 목록 ===")
sido_list = sorted(df["시도"].unique().tolist())
print(sido_list)
print(f"총 {len(sido_list)}개 시도")

# ⑤ 빠진 시도 확인
print("\n=== 빠진 시도 확인 ===")
all_sido = ["서울", "부산", "대구", "인천", "광주", "대전", "울산",
            "세종", "경기", "강원", "충북", "충남", "전북", "전남",
            "경북", "경남", "제주"]
missing = [s for s in all_sido if s not in sido_list]
print(f"빠진 시도: {missing}" if missing else "빠진 시도 없음 ✅")

# ⑥ 시도별 데이터 수
print("\n=== 시도별 데이터 수 ===")
print(df["시도"].value_counts())

# ⑦ 결측값 확인
print("\n=== 결측값 확인 ===")
print(df.isnull().sum())

# 연도별 데이터 수 확인
print("\n=== 연도별 데이터 수 ===")
print(df["연도"].value_counts())
