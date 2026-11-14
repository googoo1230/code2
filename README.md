# 병원 찾기 (6조)

## 1. 설치
```
pip install -r requirements.txt
```

## 2. DB 만들기

### 방법 A. 덤프 파일로 복원 (최종 제출용)
```
mysql -u root -p -e "CREATE DATABASE hospital_db DEFAULT CHARACTER SET utf8mb4"
mysql -u root -p hospital_db < hospital_db.sql
```

### 방법 B. CSV에서 직접 만들기 (개발용)
1. 드라이브에서 CSV를 받아 `data/` 폴더에 넣는다: `region.csv`, `department.csv`, `hospital.csv` (+ `hospital_dept.csv`)
2. 저장소 최상위 폴더에서 실행
```
mysql -u root -p < sql/schema.sql
mysql --local-infile=1 -u root -p hospital_db < sql/load_data.sql
```
마지막에 행 수가 나온다: region 262, department 47, hospital 79,899.
"Loading local data is disabled" 오류가 나면 MySQL에서 `SET GLOBAL local_infile = 1;` 을 한 번 실행한 뒤 다시 한다.

## 3. 접속 설정
`app/config_example.py`를 복사해 `app/config.py`로 만들고 `password`에 자기 MySQL 비밀번호를 넣는다.

## 4. 실행
```
cd app
python main.py
```
메뉴 번호를 고르고 조건을 입력한다. 선택 조건은 Enter로 건너뛰고, `?`를 입력하면 입력 가능한 시도·시군구·종별·진료과목 목록이 나온다 (시군구는 앞에서 고른 시도 기준). 0을 누르면 종료한다.
