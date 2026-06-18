# 🚗 최근 자동차 구매 및 등록 트렌드


 ## 1. 👨‍💻 팀원 소개 및 역할 (Team)
 팀명 : 

| 이름 | 담당 역할 (Role) | GitHub |
|:---:|:---|:---|
| **김문규** | 📊 **차량 데이터 분석 및 UI/UX 총괄**<br> • 자동차 현황 DB 아키텍처 설계<br> • Streamlit 대시보드 전체 UI 기획 및 구현<br> • Pydeck/Plotly 기반 핵심 지표 시각화 | [@tender0602](https://github.com/tender0602) |
| **김성훈** | ⚙️ **데이터 파이프라인 및 프론트엔드 지원**<br> • 브랜드별 FAQ 데이터 수집 자동화<br> • 공간/통계 데이터 렌더링 및 시각화<br> • Streamlit UI 컴포넌트 개발 | [@tjdgns8343](https://github.com/tjdgns8343) |
| **김영석** | 🛠️ **데이터 엔지니어링 및 외부 API 연동**<br> • 유가/연료 핵심 DB 설계 및 구축<br> • 공공데이터 전처리 파이프라인 개발<br> • 구글 뉴스 RSS API 연동 및 실시간 트렌드 구현 | [@golddragon0926](https://github.com/golddragon0926) |
| **송지섭** | 📈 **데이터 전처리 및 백엔드 지원**<br> • 유가/연료 데이터 통계 분석 및 정제<br> • FAQ 웹 스크래핑 및 텍스트 데이터 추출<br> • 대시보드 UI/UX 기능 개선 및 지원 | [@sji21](https://github.com/sji21) |
| **최경돈** | ⚡ **공공데이터 API 및 크롤링 로직 구현**<br> • 전기차 보조금 API 연동 및 맞춤형 로직 개발<br> • 전기차 데이터(Raw Data) 추출 <br> • 브랜드별 FAQ 데이터 수집 및 정제 | [@dony6366](https://github.com/dony6366) |

## 2. 📖 프로젝트 소개
"고유가 시대, 내 차 마련을 위한 가장 스마트한 데이터 가이드"

최근 불안정한 유가 흐름과 친환경차 보급 정책이 맞물리면서, 예비 자동차 구매자들의 고민이 그 어느 때보다 깊어지고 있습니다.
본 프로젝트는 거시적인 유가 변동이 실제 자동차 시장(내연기관 vs 친환경차)의 소비 트렌드에 미치는 영향을 데이터로 입증하고, 
나아가 개인의 합리적인 차량 구매 의사결정을 돕기 위해 기획된 통합 웹 대시보드입니다.

공공데이터(오피넷, 국토교통부)와 자체 구축한 데이터 파이프라인(전기차 보조금, 브랜드 FAQ 크롤링, 실시간 뉴스 RSS)을 결합하여 다음과 같은 입체적인 인사이트를 제공합니다.

## 3. 📊 데이터 출처 (Data Sources)

본 프로젝트는 아래의 공공 데이터 및 API를 활용하여 구축되었습니다.
- **[오피넷 (Opinet)](https://www.opinet.co.kr/)**: 지역별/기간별 실시간 유가 정보 데이터
- **[e-나라지표 (지표누리)](https://www.index.go.kr/)**: 자동차 등록 현황 및 수송 관련 통계 데이터
- **[뉴스 API 출처명](https://www.naver.com/)**: 실시간 자동차 및 경제 관련 뉴스 수집
- **[환경부 무공해차 통합누리집](https://ev.or.kr/)**: 전기차 보조금 데이터

## 4. 🗄️ 데이터베이스 구조 (Database Schema)

| 테이블명 (Table) | 주요 컬럼 (Columns) | 설명 (Description) |
| :--- | :--- | :--- |
| **Region** | `region_id` (PK), `region_code`, `region_name` | 전국 17개 시도 |
| **Fuel_Type** | `fuel_id` (PK), `fuel_code`, `fuel_name` | GAS/DSL/ELC/HEV/HYD 등 5종 연료 |
| **Oil_price** | `id` (PK), `region_id` (FK), `price_date`, `fuel_code`, `price` | 지역별 유가 시계열 데이터 |
| **New_Registration** | `id` (PK), `region_id` (FK), `fuel_id` (FK), `reg_year`, `reg_month`, `vehicle_type`, `count` | 연료별 차량 신규 등록 대수 |
| **Subsidy** | `id` (PK), `region_id` (FK), `year`, `sigungu`, `vehicle_type`, `manufacturer`, `model_name`, `national_subsidy`, `local_subsidy`, `total_subsidy` | 시군구 단위/차종별 전기차 보조금 |
| **FAQ** | `id` (PK), `brand`, `title`, `content`, `category` | 자동차 브랜드별 통합 FAQ 데이터 |

## 5. 🚀 주요 기능 (Features)
- **📈 종합 트렌드 분석:** 전국 월별 평균 유가 추이와 연료별(휘발유, 경유, 전기, 하이브리드 등) 신규 차량 등록 대수 상관관계 시각화
- **🗺️ 지역별 비교:** 전국 17개 시도의 평균 유가와 친환경차(EV/HEV/FCEV) 선택 비율의 지역별 차이 및 상관관계 분석
- **💰 유류비 시뮬레이터:** 현재 전국 평균 유가를 반영하여 사용자의 주행 조건에 맞는 내연기관차 vs 전기차 연간 유지비 비교
- **📰 실시간 뉴스 연동:** 구글 뉴스 RSS 피드를 활용한 자동차/유가 관련 실시간 트렌드 기사 제공


## 📁 디렉토리 구조 (Directory Structure)

```
📦 _02_team_project_car
├── ⚙️ config/                    # 환경 설정 폴더
│   ├── db_config.py             # DB 접속 정보 및 전역 변수 설정
│   └── __init__.py
│
├── 🕷️ crawling/                  # 데이터 수집 및 스크래핑 모듈
│   ├── bmw_faq_crawler.py       # BMW FAQ 크롤러
│   ├── hyundai_faq_crawler.py   # 현대차 FAQ 크롤러
│   ├── kgm_faq_crawler.py       # KGM FAQ 크롤러
│   ├── kia_faq_crawler.py       # 기아차 FAQ 크롤러
│   ├── car_registeration_api.py # 교통안전공단 차량 등록 현황 API
│   ├── ev_crawler.py            # 전기차 관련 데이터 수집
│   ├── news_api.py              # 구글 실시간 뉴스 RSS 파싱
│   ├── opinet_api.py            # 오피넷 유가 API 연동
│   ├── opinet_crawler.py        # 오피넷 사이트 크롤러
│   ├── oil_price_csv.py         # 유가 데이터 전처리 스크립트
│   ├── subsidy_scrap.py         # 전기차 보조금 데이터 스크래핑
│   └── insert_subsidy.py        # 보조금 데이터 처리 및 전송
│
├── 🗂️ data/                      # 원본 및 정제된 데이터 보관소
│   ├── faq.csv                  # 통합 FAQ 데이터
│   ├── new_registration.csv     # 신규 차량 등록 정제 데이터
│   ├── oil_price.csv            # 전국 유가 정제 데이터
│   ├── region.csv               # 지역 코드 맵핑 데이터
│   ├── subsidy.csv              # 보조금 정제 데이터
│   │
│   ├── faq/                     # 브랜드별 개별 FAQ 원본 데이터
│   │   ├── bmw_faq_data.csv
│   │   ├── hyundai_faq_data.csv
│   │   ├── kgm_faq_data.csv
│   │   ├── kia_faq_data.csv
│   │   └── opinet_faq_data.csv
│   │
│   └── raw/                     # API/크롤링으로 수집한 순수 로우 데이터
│       ├── ev_charger.json
│       ├── 보조금데이터.csv
│       └── 주유소_지역별_평균판매가격_*.csv
│
├── 🗄️ DB/                        # 데이터베이스 구축 및 적재 모듈
│   ├── create_db.sql            # DB 및 전체 테이블 구조(ERD) 생성 SQL
│   ├── load_all_data.py         # 정제 데이터를 DB로 일괄 적재(INSERT)
│   ├── load_faq_to_db.py        # FAQ 데이터 전용 DB 적재 스크립트
│   └── export_csv.py            # DB 데이터를 다시 CSV로 백업하는 스크립트
│
└── 💻 streamlit_app/             # 웹 대시보드 애플리케이션 (UI/UX)
    ├── app.py                   # Streamlit 메인 실행 파일 (레이아웃 구성)
    ├── db_queries.py            # 대시보드 전용 DB SELECT 쿼리 모음
    ├── korea.geojson            # 지역별 지도 시각화를 위한 공간 데이터
    ├── tab1_trend.py            # [탭 1] 월별 유가 및 등록 트렌드 차트
    ├── tab2_map.py              # [탭 2] 전국 지역별 유가/친환경차 맵
    ├── tab3_news.py             # [탭 3] 실시간 뉴스 및 트렌드
    ├── tab4_sim.py              # [탭 4] 유류비 vs 충전비 시뮬레이터
    ├── tab5_faq.py              # [탭 5] 자동차 브랜드별 FAQ 검색 기능
    └── tab6_subsidy.py          # [탭 6] 지역/차종별 전기차 보조금 안내
 ```

## 6. ⚙️ 설치 및 실행 방법 (Getting Started)

이 프로젝트를 로컬 환경에서 실행하기 위한 방법입니다.

1. 레포지토리 클론
```
Bash

git clone https://github.com/golddragon0926/_02_team_project_car.git
cd _02_team_project_car
```

2. 가상환경 생성 및 패키지 설치
Python 3.10+ 환경에서 프로젝트에 필요한 라이브러리를 설치합니다.
```
Bash

# 가상환경 생성
python -m venv venv

# 가상환경 활성화 (Windows)
venv\Scripts\activate
# 가상환경 활성화 (Mac/Linux)
source venv/bin/activate

# 패키지 설치
pip install -r requirements.txt
```

3. 환경 변수 설정
.env.example 파일을 복사하여 .env 파일을 생성하고, 본인의 데이터베이스 접속 정보 및 API 키를 입력합니다.

```
Bash

cp .env.example .env
# 생성된 .env 파일 내의 DB_USER, DB_PASSWORD 등을 본인 환경에 맞게 수정
```

4. 데이터베이스 초기 세팅
로컬 DB 환경에 테이블 스키마를 생성합니다.

```
Bash

# DB 폴더 내의 create_db.sql 스크립트를 사용하여 테이블 생성
# (MySQL Workbench나 DBeaver에서 해당 sql 파일 실행)
```

5. Streamlit 대시보드 실행
모든 세팅이 완료되면 아래 명령어를 통해 웹 애플리케이션을 실행합니다.
```
Bash

streamlit run streamlit_app/app.py
```

## 7. 수행 화면 캡처
<img width="2127" height="901" alt="Image" src="https://github.com/user-attachments/assets/6bae3989-1ea2-447e-848f-5b054ff0170d" />
<img width="2135" height="901" alt="Image" src="https://github.com/user-attachments/assets/a88b4a92-38a3-4f87-a1f7-5da6e20f2d35" />

## 8. 회고