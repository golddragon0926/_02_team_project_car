# 🚗 자동차 데이터 수집 및 시각화 웹 서비스

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

## 🛠 기술 스택 (Tech Stack)
** Language**: Python 3.x
** Web Application (Frontend)**: Streamlit
** Data Analysis & Statistics**: Pandas, NumPy, SciPy, Statsmodels
** Data Visualization**: Plotly, Altair, Matplotlib, Pydeck
** Database & Server**: MySQL
** Data Collection**: Requests, urllib3
** Configuration & Tools**: python-dotenv

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
