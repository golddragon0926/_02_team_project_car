-- =============================================
-- 전국 유가 및 차량 등록 현황 분석 시스템
-- DB 생성 SQL
-- =============================================

CREATE DATABASE IF NOT EXISTS car_oil_db
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE car_oil_db;

-- =============================================
-- 1. 지역 테이블 (시도 단위)
-- =============================================
CREATE TABLE IF NOT EXISTS region (
  region_id    INT           NOT NULL AUTO_INCREMENT,
  region_code  VARCHAR(10)   NOT NULL COMMENT '시도 코드 (예: 11=서울, 41=경기)',
  region_name  VARCHAR(20)   NOT NULL COMMENT '시도명 (예: 서울특별시)',
  created_at   DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (region_id),
  UNIQUE KEY uq_region_code (region_code)
) COMMENT='시도 지역 코드 테이블';

-- 기본 데이터 삽입
INSERT INTO region (region_code, region_name) VALUES
  ('11', '서울특별시'),
  ('26', '부산광역시'),
  ('27', '대구광역시'),
  ('28', '인천광역시'),
  ('29', '광주광역시'),
  ('30', '대전광역시'),
  ('31', '울산광역시'),
  ('36', '세종특별자치시'),
  ('41', '경기도'),
  ('42', '강원도'),
  ('43', '충청북도'),
  ('44', '충청남도'),
  ('45', '전라북도'),
  ('46', '전라남도'),
  ('47', '경상북도'),
  ('48', '경상남도'),
  ('50', '제주특별자치도');


-- =============================================
-- 2. 연료 유형 테이블
-- =============================================
CREATE TABLE IF NOT EXISTS fuel_type (
  fuel_id    INT          NOT NULL AUTO_INCREMENT,
  fuel_code  VARCHAR(10)  NOT NULL COMMENT 'API 연료 코드 (예: GAS, DSL, ELC)',
  fuel_name  VARCHAR(20)  NOT NULL COMMENT '연료명 (예: 휘발유, 경유, 전기)',
  created_at DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (fuel_id),
  UNIQUE KEY uq_fuel_code (fuel_code)
) COMMENT='연료 유형 코드 테이블';

-- 기본 데이터 삽입
INSERT INTO fuel_type (fuel_code, fuel_name) VALUES
  ('GAS', '휘발유'),
  ('DSL', '경유'),
  ('LPG', 'LPG'),
  ('ELC', '전기'),
  ('HEV', '하이브리드'),
  ('HYD', '수소'),
  ('CNG', 'CNG');


-- =============================================
-- 3. 유가 시계열 테이블 (오피넷 API)
-- =============================================
CREATE TABLE IF NOT EXISTS oil_price (
  id          INT           NOT NULL AUTO_INCREMENT,
  price_date  DATE          NOT NULL COMMENT '기준 날짜',
  region_id   INT           NOT NULL COMMENT '지역 (전국=0 별도처리)',
  fuel_code   VARCHAR(10)   NOT NULL COMMENT '유종 (휘발유/경유/LPG)',
  price       DECIMAL(7,2)  NOT NULL COMMENT '평균 판매가격 (원/리터)',
  created_at  DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_price (price_date, region_id, fuel_code),
  KEY idx_price_date (price_date),
  KEY idx_region (region_id),
  CONSTRAINT fk_oil_region FOREIGN KEY (region_id) REFERENCES region (region_id)
) COMMENT='유가 시계열 데이터 (오피넷 API)';


-- =============================================
-- 4. 신규 등록 테이블 (교통안전공단 API)
-- =============================================
CREATE TABLE IF NOT EXISTS new_registration (
  id            INT          NOT NULL AUTO_INCREMENT,
  reg_year      YEAR         NOT NULL COMMENT '등록 연도',
  reg_month     TINYINT      NOT NULL COMMENT '등록 월 (1~12)',
  region_id     INT          NOT NULL COMMENT '등록 지역',
  fuel_id       INT          NOT NULL COMMENT '사용 연료',
  vehicle_type  VARCHAR(10)  NOT NULL COMMENT '차종 (승용/승합/화물/특수)',
  count         INT          NOT NULL DEFAULT 0 COMMENT '신규 등록 대수',
  created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_new_reg (reg_year, reg_month, region_id, fuel_id, vehicle_type),
  KEY idx_new_year (reg_year),
  KEY idx_new_region (region_id),
  KEY idx_new_fuel (fuel_id),
  CONSTRAINT fk_new_region FOREIGN KEY (region_id) REFERENCES region (region_id),
  CONSTRAINT fk_new_fuel   FOREIGN KEY (fuel_id)   REFERENCES fuel_type (fuel_id)
) COMMENT='연료별 차량 신규 등록 현황 (교통안전공단 API)';


-- =============================================
-- 5. 누적 등록 테이블 (국토교통부 CSV)
-- =============================================
CREATE TABLE IF NOT EXISTS cumulative_registration (
  id            INT          NOT NULL AUTO_INCREMENT,
  reg_year      YEAR         NOT NULL COMMENT '기준 연도',
  region_id     INT          NOT NULL COMMENT '등록 지역',
  fuel_id       INT          NOT NULL COMMENT '사용 연료',
  vehicle_type  VARCHAR(10)  NOT NULL COMMENT '차종 (승용/승합/화물/특수)',
  total_count   INT          NOT NULL DEFAULT 0 COMMENT '누적 등록 대수',
  created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_cum_reg (reg_year, region_id, fuel_id, vehicle_type),
  KEY idx_cum_year (reg_year),
  KEY idx_cum_region (region_id),
  KEY idx_cum_fuel (fuel_id),
  CONSTRAINT fk_cum_region FOREIGN KEY (region_id) REFERENCES region (region_id),
  CONSTRAINT fk_cum_fuel   FOREIGN KEY (fuel_id)   REFERENCES fuel_type (fuel_id)
) COMMENT='연료별 차량 누적 등록 현황 (국토교통부 CSV)';


-- =============================================
-- 확인 쿼리
-- =============================================
SELECT '=== 테이블 생성 완료 ===' AS status;
SHOW TABLES;
SELECT * FROM region;
SELECT * FROM fuel_type;

