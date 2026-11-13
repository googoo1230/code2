# 이 파일을 복사해서 config.py로 만든 뒤 자기 MySQL 비밀번호를 넣는다.
# config.py는 .gitignore에 있으므로 GitHub과 제출 파일에 올라가지 않는다.
DB = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "",          # 제출 시 빈칸 유지
    "database": "hospital_db",
    "charset": "utf8mb4",
}
