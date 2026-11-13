# 병원 찾기 (6조)

## 1. 설치
```
pip install -r requirements.txt
```

## 2. DB 복원
```
mysql -u root -p -e "CREATE DATABASE hospital_db DEFAULT CHARACTER SET utf8mb4"
mysql -u root -p hospital_db < hospital_db.sql
```

## 3. 접속 설정
`app/config_example.py`를 복사해 `app/config.py`로 만들고 `password`에 자기 MySQL 비밀번호를 넣는다.

## 4. 실행
```
cd app
python main.py
```
메뉴 번호를 고르고 조건을 입력한다. 선택 조건은 Enter로 건너뛰고, `?`를 입력하면 입력 가능한 시도·종별·진료과목 목록이 나온다. 0을 누르면 종료한다.
