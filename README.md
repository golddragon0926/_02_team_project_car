# 🚗 유가 변동에 따른 자동차 트렌드 분석 대시보드

<br>## 📖 프로젝트 소개
"고유가 시대, 내 차 마련을 위한 가장 스마트한 데이터 가이드"

최근 불안정한 유가 흐름과 친환경차 보급 정책이 맞물리면서, 예비 자동차 구매자들의 고민이 그 어느 때보다 깊어지고 있습니다.<br>
본 프로젝트는 거시적인 유가 변동이 실제 자동차 시장(내연기관 vs 친환경차)의 소비 트렌드에 미치는 영향을 데이터로 입증하고, 
나아가 개인의 합리적인 차량 구매 의사결정을 돕기 위해 기획된 통합 웹 대시보드입니다.

공공데이터(오피넷, 국토교통부)와 자체 구축한 데이터 파이프라인(전기차 보조금, 브랜드 FAQ 크롤링, 실시간 뉴스 RSS)을 결합하여 다음과 같은 입체적인 인사이트를 제공합니다.


<br>## 🚀 주요 기능 (Features)
- **📈 종합 트렌드 분석:** 전국 월별 평균 유가 추이와 연료별(휘발유, 경유, 전기, 하이브리드 등) 신규 차량 등록 대수 상관관계 시각화
- **🗺️ 지역별 비교:** 전국 17개 시도의 평균 유가와 친환경차(EV/HEV/FCEV) 선택 비율의 지역별 차이 및 상관관계 분석
- **💰 유류비 시뮬레이터:** 현재 전국 평균 유가를 반영하여 사용자의 주행 조건에 맞는 내연기관차 vs 전기차 연간 유지비 비교
- **📰 실시간 뉴스 연동:** 구글 뉴스 RSS 피드를 활용한 자동차/유가 관련 실시간 트렌드 기사 제공


<br>## 📊 데이터 출처 (Data Sources)

본 프로젝트는 아래의 공공 데이터 및 API를 활용하여 구축되었습니다.
- **[오피넷 (Opinet)](https://www.opinet.co.kr/)**: 지역별/기간별 실시간 유가 정보 데이터
- **[e-나라지표 (지표누리)](https://www.index.go.kr/)**: 자동차 등록 현황 및 수송 관련 통계 데이터
- **[뉴스 API 출처명](https://www.naver.com/)**: 실시간 자동차 및 경제 관련 뉴스 수집
- **[환경부 무공해차 통합누리집](https://ev.or.kr/)**: 전기차 보조금 데이터


<br>## 🛠 기술 스택 (Tech Stack)
- **Language:** Python 3.10+
- **Frontend / Dashboard:** Streamlit, Plotly
- **Database:** MySQL
- **Data Collection:** Pandas, Requests, XML Parsing (Google News RSS)
- **Version Control:** Git, GitHub


<br>## 📁 디렉토리 구조 (Directory Structure)

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


<br>## ⚙️ 설치 및 실행 방법 (Getting Started)

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

 <br>## 👨‍💻 팀원 소개 및 역할 (Team)

| 이름 | 담당 역할 (Role) | GitHub |
|:---:|:---|:---|
| **[김문규]** | **Frontend & Data Analysis**<br>- 자동차 현황 DB설계<br> - Streamlit 대시보드 전체적인 UI 설계<br>- Pydeck 및 Plotly를 활용한 데이터 시각화 | [@github_id](https://github.com/github_id) |
| **[김성훈]** | **Backend & Data Pipeline**<br>- FAQ 크롤링 및 csv파일 저장<br> - Streamlit 대시보드(tab5) UI 설계<br> | [@github_id](https://github.com/github_id) |
| **[김영석]** | **Data Engineering & Crawling**<br>- 실시간 뉴스 API 설계 및 구현 (`news_api.py`, `tab3_news.py`)<br>- 전처리 및 데이터 추출 로직 작성 | [@github_id](https://github.com/github_id) |
| **[송지섭]** | **Data Engineering & Crawling**<br>- 연료 가격 DB데이터 설계 및 구현(`db_config.py`, `opinet_api.py`)<br>- 전처리 및 통계 데이터 추출 로직 작성 (`export_csv.py`) | [@github_id](https://github.com/github_id) |
| **[최경돈]** | **Data Engineering & Crawling**<br>- DB데이터 설계 및 정제  (`news_api.py`)<br>- 전처리 및 통계 데이터 추출 로직 작성 (`export_csv.py`) | [@github_id](https://github.com/github_id) |
