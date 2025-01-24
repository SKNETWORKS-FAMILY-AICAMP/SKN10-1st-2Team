import pandas as pd
import pymysql

# 파일 경로 설정
input_file = "C:/dev/SKN10-1st-2Team/onnajul/data/car_data.xlsx"  # 원본 파일 경로

# MySQL 연결 정보 설정
conn = pymysql.connect(
    host='localhost',
    user='SKN_10_2',
    password='s1234',
    database='car_db',
    charset='utf8mb4'
)

# Excel 파일 읽기
df = pd.read_excel(input_file)

# 결측값 처리
# 문자열 컬럼: NaN을 빈 문자열로 대체
string_columns = ["월(Monthly)", "시도명", "시군구"]
df[string_columns] = df[string_columns].fillna("")

# 숫자 컬럼: NaN을 0으로 대체
numeric_columns = ["승용", "승합", "화물", "특수", "총계"]
df[numeric_columns] = df[numeric_columns].replace(",", "", regex=True).fillna(0).astype(int)

# 테이블 이름과 컬럼명 설정
table_name = "car_registration2"  # 테이블 이름
columns = ["month", "province", "district", "passenger", "bus", "truck", "special", "total"]  # 컬럼명

# 데이터 삽입
with conn.cursor() as cursor:
    # 데이터프레임의 각 행을 순회하며 INSERT 문 실행
    for _, row in df.iterrows():
        values = (
            row["월(Monthly)"],  # 월(Monthly)
            row["시도명"],       # 시도명
            row["시군구"],       # 시군구
            row["승용"],         # 승용 (쉼표 제거 후 정수형 변환된 값)
            row["승합"],         # 승합 (쉼표 제거 후 정수형 변환된 값)
            row["화물"],         # 화물 (쉼표 제거 후 정수형 변환된 값)
            row["특수"],         # 특수 (쉼표 제거 후 정수형 변환된 값)
            row["총계"],         # 총계 (쉼표 제거 후 정수형 변환된 값)
        )
        # INSERT SQL 문
        sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(sql, values)

# 변경 사항 커밋 및 연결 종료
conn.commit()
conn.close()

print(f"데이터가 MySQL 데이터베이스 '{table_name}' 테이블에 성공적으로 삽입되었습니다.")
