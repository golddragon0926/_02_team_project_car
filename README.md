# 🚗 자동차 및 유가 데이터 통합 분석 대시보드

## 📖 프로젝트 소개
이 프로젝트는 **오피넷(Opinet)**의 유가 데이터와 **e-나라지표(지표누리)**의 자동차 등록 및 수송 관련 데이터를 크롤링하여
 MySQL 데이터베이스에 적재하고, **Streamlit**을 활용하여 사용자에게 유가 트렌드 및 자동차 시장 동향을 직관적인 대시보드로 제공하는 웹 애플리케이션입니다.

## 🚀 주요 기능 (Features)
- **자동화된 크롤링**: 오피넷 및 e-나라지표에서 지역별 유가 정보와 자동차 등록 현황 데이터를 주기적으로 수집.
- **데이터베이스 연동**: MySQL을 연동하여 수집된 시계열 데이터를 안정적으로 저장하고 인덱싱을 통해 조회 성능 최적화.
- **웹 대시보드 (Streamlit)**: 
  - 지역별/기간별 유가 변동 추이 차트 시각화.
  - 자동차 등록 대수 변화와 유가 간의 상관관계 분석 대시보드.
  - 조건별 데이터 필터링 및 조회 기능.
- **데이터 추출**: DB에 축적된 데이터를 CSV 파일로 추출하여 추가적인 데이터 분석 가능 (`export_csv.py`).

## 📊 데이터 출처 (Data Sources)

본 프로젝트는 아래의 공공 데이터 및 API를 활용하여 구축되었습니다.
- **[오피넷 (Opinet)](https://www.opinet.co.kr/)**: 지역별/기간별 실시간 유가 정보 데이터
- **[e-나라지표 (지표누리)](https://www.index.go.kr/)**: 자동차 등록 현황 및 수송 관련 통계 데이터
- **[뉴스 API 출처명](https://www.naver.com)**: 실시간 자동차 및 경제 관련 뉴스 수집

## 🛠 기술 스택 (Tech Stack)
- **Language**: Python 3.10
- **Web Application (Frontend)**: Streamlit
- **Data Analysis & Statistics**: Pandas, NumPy, SciPy, Statsmodels
- **Data Visualization**: Plotly, Altair, Matplotlib, Pydeck
- **Database & Server**: MySQL
- **Data Collection**: Requests, urllib3
- **Configuration & Tools**: python-dotenv

## 📁 디렉토리 구조 (Directory Structure)

```
📦 _02_team_project_car
 ┣ 📂 DB                          # 데이터베이스 및 원본 데이터 관리
 ┃ ┣ 📜 car_project.db            # 로컬 데이터베이스 파일 (SQLite)
 ┃ ┣ 📜 create_db.sql             # DB 테이블 스키마 초기 생성 SQL 스크립트
 ┃ ┣ 📜 ev_charger.json           # 전기차 충전소 위치 및 관련 JSON 데이터
 ┃ ┣ 📜 주유소_지역별_평균판매가격26경유.csv   # 특정 연도(26년 등) 지역별 경유 평균가 데이터
 ┃ ┣ 📜 주유소_지역별_평균판매가격26휘발유.csv # 특정 연도(26년 등) 지역별 휘발유 평균가 데이터
 ┃ ┣ 📜 주유소_지역별_평균판매가격_경유.csv    # 전체 지역별 경유 평균가 통합 데이터
 ┃ ┗ 📜 주유소_지역별_평균판매가격_휘발유.csv  # 전체 지역별 휘발유 평균가 통합 데이터
 ┣ 📂 config                      # 프로젝트 환경 및 구성 설정
 ┃ ┗ 📜 db_config.py              # 데이터베이스 연결 정보 및 세션 관리 로직
 ┣ 📂 crawling                    # 웹 크롤링 및 API 데이터 수집 스크립트
 ┃ ┣ 📜 car_registeration_api.py  # 지표누리 등 자동차 등록 현황 API 연동 스크립트
 ┃ ┣ 📜 create_db.sql             # 수집 데이터 적재를 위한 쿼리문 (DB 폴더와 연동)
 ┃ ┣ 📜 faq_crawler.py            # 자동차 및 유가 관련 FAQ 정보 웹 크롤러
 ┃ ┣ 📜 news_api.py               # 실시간 자동차/경제 관련 뉴스 API 수집 스크립트
 ┃ ┣ 📜 oil_price_csv.py          # 유가 관련 CSV 데이터를 처리 및 가공하는 스크립트
 ┃ ┗ 📜 opinet_api.py             # 오피넷 API를 통한 실시간 유가 데이터 수집 스크립트
 ┣ 📂 data                        # 수집 및 전처리가 완료된 분석용 데이터셋 보관
 ┃ ┣ 📜 new_registration.csv      # 신규 자동차 등록 데이터
 ┃ ┣ 📜 oil_price.csv             # 유가 변동 추이 데이터
 ┃ ┗ 📜 region.csv                # 지역별 매핑 및 분류 기준 데이터
 ┣ 📂 streamlit_app               # Streamlit 프론트엔드 웹 대시보드
 ┃ ┣ 📜 app.py                    # Streamlit 메인 실행 파일 (앱 진입점)
 ┃ ┣ 📜 db_queries.py             # 대시보드 내에서 사용되는 데이터베이스 조회용 쿼리 함수 모음
 ┃ ┣ 📜 korea.geojson             # Pydeck 등을 활용한 대한민국 지역별 지도 시각화용 폴리곤 데이터
 ┃ ┣ 📜 tab1_trend.py             # [탭 1] 차량 등록 및 유가 변동 트렌드 분석 화면
 ┃ ┣ 📜 tab2_map.py               # [탭 2] 지도 기반(GeoJSON) 지역별 데이터 시각화 화면
 ┃ ┣ 📜 tab3_news.py              # [탭 3] 수집된 관련 뉴스 헤드라인 제공 및 검색 화면
 ┃ ┣ 📜 tab4_sim.py               # [탭 4] 조건별 유가/차량 관련 시뮬레이터 및 분석 화면
 ┃ ┗ 📜 tab5_faq.py               # [탭 5] 사용자 편의를 위한 FAQ 제공 화면
 ┣ 📜 .env.example                # 환경 변수 템플릿 (DB 정보, API 키 등 민감정보 양식)
 ┣ 📜 .gitignore                  # Git 버전 관리에서 제외할 파일 및 폴더 목록
 ┣ 📜 export_csv.py               # DB에 적재된 데이터를 CSV 형태로 일괄 추출하는 스크립트
 ┣ 📜 requirements.txt            # 프로젝트 실행에 필요한 파이썬 패키지 의존성 목록
 ┗ 📜 test.py                     # 각 모듈(크롤링, DB 연동 등)의 정상 작동 여부를 확인하는 테스트 스크립트
 ```

## ⚙️ 설치 및 실행 방법 (Getting Started)

이 프로젝트를 로컬 환경에서 실행하기 위한 방법입니다.

### 1. 레포지토리 클론
```bash
git clone https://github.com/golddragon0926/_02_team_project_car.git
cd _02_team_project_car
```

2. 가상환경 생성 및 패키지 설치
Python 3.x 환경에서 필요한 라이브러리를 설치합니다.
```bash
# 가상환경 생성 및 활성화 (선택)
python -m venv venv
source venv/bin/activate

# 패키지 설치
pip install -r requirements.txt
```

3. 환경 변수 설정
.env.example 파일을 복사하여 .env 파일을 생성하고, 본인의 데이터베이스 접속 정보 및 API 키를 입력합니다.

```
cp .env.example .env
# 생성된 .env 파일 내의 DB_USER, DB_PASSWORD 등을 환경에 맞게 수정
```

4. 데이터베이스 초기 세팅
로컬 DB 환경에 테이블 스키마를 생성합니다.

```Bash
# DB 폴더 내의 create_db.sql 스크립트를 사용하여 테이블 생성
# (MySQL 워크벤치나 CLI에서 해당 sql 파일 실행)
```

5. Streamlit 대시보드 실행
모든 세팅이 완료되면 아래 명령어를 통해 웹 애플리케이션을 실행합니다.
```
Bash
streamlit run streamlit_app/app.py
```

 ## 👨‍💻 팀원 소개 및 역할 (Team)

| 이름 | 담당 역할 (Role) | GitHub |
|:---:|:---|:---|
| **[김문규]** | **Frontend & Data Analysis**<br>- 자동차 현황 DB설계<br> - Streamlit 대시보드 전체적인 UI 설계<br>- Pydeck 및 Plotly를 활용한 데이터 시각화 | [@github_id](https://github.com/github_id) |
| **[김성훈]** | **Backend & Data Pipeline**<br>- FAQ 크롤링 및 csv파일 저장<br> - Streamlit 대시보드(tab5) UI 설계<br> | [@github_id](https://github.com/github_id) |
| **[김영석]** | **Data Engineering & Crawling**<br>- 실시간 뉴스 API 설계 및 구현 (`news_api.py`, `tab3_news.py`)<br>- 전처리 및 데이터 추출 로직 작성 | [@github_id](https://github.com/github_id) |
| **[송지섭]** | **Data Engineering & Crawling**<br>- 연료 가격 DB데이터 설계 및 구현(`db_config.py`, `opinet_api.py`)<br>- 전처리 및 통계 데이터 추출 로직 작성 (`export_csv.py`) | [@github_id](https://github.com/github_id) |
| **[최경돈]** | **Data Engineering & Crawling**<br>- DB데이터 설계 및 정제  (`news_api.py`)<br>- 전처리 및 통계 데이터 추출 로직 작성 (`export_csv.py`) | [@github_id](https://github.com/github_id) |