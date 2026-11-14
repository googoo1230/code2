-- CSV 적재 (저장소 최상위 폴더에서 실행)
--   mysql --local-infile=1 -u root -p hospital_db < sql/load_data.sql
-- MySQL 8에서 "Loading local data is disabled" 오류가 나면 root로 한 번 실행:
--   SET GLOBAL local_infile = 1;
-- CSV는 data/ 폴더에 둔다 (용량 때문에 GitHub에는 올리지 않음, 드라이브 공유)

USE hospital_db;
SET NAMES utf8mb4;

LOAD DATA LOCAL INFILE 'data/region.csv' INTO TABLE region
  CHARACTER SET utf8mb4 FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
  LINES TERMINATED BY '\n' IGNORE 1 LINES
  (region_id, sgg_code, sido, sgg);

LOAD DATA LOCAL INFILE 'data/department.csv' INTO TABLE department
  CHARACTER SET utf8mb4 FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
  LINES TERMINATED BY '\n' IGNORE 1 LINES
  (dept_code, dept_name);

LOAD DATA LOCAL INFILE 'data/hospital.csv' INTO TABLE hospital
  CHARACTER SET utf8mb4 FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
  LINES TERMINATED BY '\n' IGNORE 1 LINES
  (ykiho, name, type, address, @tel, region_id)
  SET tel = NULLIF(@tel, '');

-- hospital_dept.csv가 준비되면 주석 해제 (컬럼: ykiho, dept_code, specialist_cnt)
-- LOAD DATA LOCAL INFILE 'data/hospital_dept.csv' INTO TABLE hospital_dept
--   CHARACTER SET utf8mb4 FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
--   LINES TERMINATED BY '\n' IGNORE 1 LINES
--   (ykiho, dept_code, specialist_cnt);

-- 적재 검증: 행 수 (region 262, department 47, hospital 79,899 이어야 함)
SELECT 'region' AS 테이블, COUNT(*) AS 행수 FROM region
UNION ALL SELECT 'department', COUNT(*) FROM department
UNION ALL SELECT 'hospital', COUNT(*) FROM hospital
UNION ALL SELECT 'hospital_dept', COUNT(*) FROM hospital_dept;
