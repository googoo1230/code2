-- 6조 병원 찾기 DB 구조
-- 생성 순서: region → department → hospital → hospital_dept (참조되는 테이블이 먼저)

SET NAMES utf8mb4;
DROP DATABASE IF EXISTS hospital_db;
CREATE DATABASE hospital_db DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE hospital_db;

-- 지역: 시군구코드(sgg_code)가 원본에서 중복되는 경우가 있어(전남/전남광주 등)
--       별도 식별자 region_id를 기본키로 쓴다.
CREATE TABLE region (
  region_id CHAR(24)     PRIMARY KEY,
  sgg_code  VARCHAR(10)  NOT NULL,
  sido      VARCHAR(20)  NOT NULL,
  sgg       VARCHAR(30)  NOT NULL,
  UNIQUE (sido, sgg),
  INDEX idx_region_sido (sido)
);

CREATE TABLE department (
  dept_code VARCHAR(5)   PRIMARY KEY,       -- '01'처럼 앞자리 0이 있으므로 문자형
  dept_name VARCHAR(50)  NOT NULL UNIQUE
);

CREATE TABLE hospital (
  ykiho     VARCHAR(100) PRIMARY KEY,       -- 암호화된 요양기호 (최대 80자)
  name      VARCHAR(100) NOT NULL,
  type      VARCHAR(20)  NOT NULL,          -- 의원, 치과의원, 한의원, 병원, 종합병원, 상급종합 등
  address   VARCHAR(200),
  tel       VARCHAR(20),                    -- 원본에 빈 값 있음 → NULL
  region_id CHAR(24)     NOT NULL,
  FOREIGN KEY (region_id) REFERENCES region(region_id),
  INDEX idx_hospital_name (name),
  INDEX idx_hospital_type (type)
);

CREATE TABLE hospital_dept (
  ykiho          VARCHAR(100),
  dept_code      VARCHAR(5),
  specialist_cnt INT NOT NULL DEFAULT 0 CHECK (specialist_cnt >= 0),
  PRIMARY KEY (ykiho, dept_code),
  FOREIGN KEY (ykiho)     REFERENCES hospital(ykiho),
  FOREIGN KEY (dept_code) REFERENCES department(dept_code)
);
