import pymysql
import pandas as pd
import streamlit as st
import openpyxl
#DB 연결 user, password, db 변경할것
conn = pymysql.connect(
    host='localhost',
    user='SKN_10_2',
    password='s1234',
    database='car_db',
    charset='utf8mb4'
)

cur = conn.cursor()
file_name = "C:/Users/sue01/Downloads/자동차등록현황보고_자동차등록대수현황 시도별 (201101 ~ 202412).xlsx"

# openpyxl 엔진을 명시적으로 지정하여 엑셀 파일 읽기
df = pd.read_excel(file_name, header=[0, 1],skiprows=4)
commit_interval = 1000

for i in range(len(df)) :
    try :
        row = list(df.loc[i])
        # 추출할 열 이름 (뒤에서 1번째, 5번째, 9번째, 13번째, 17번째)
        indices = [-1, -5, -9, -13, -17]
        extracted = [row[col] for col in indices]

        # 결측치 및 데이터 변환 처리
        data = []
        for val in extracted:
            if pd.notnull(val):
                # 숫자형 문자열을 정수로 변환
                data.append(int(str(val).replace(',', '')))
            else:
                # 결측치일 경우 기본값 0으로 처리
                data.append(0)

        data += [row[2],row[1],row[0]]

        sql = f"""insert car_registration3 (total,special,truck
        ,bus,passenger,district,province,month)
        values ({data[0]},{data[1]},{data[2]},{data[3]},{data[4]},'{data[5]}','{data[6]}','{data[7]}')"""
        cur.execute(sql)  # sql문 실행
        if i % commit_interval == 0:
            conn.commit()  # 1000번마다 커밋
    except Exception as e:
        print(f"Error at row {i}: {e}")
        conn.rollback()  # 예외 발생 시 롤백
        
# 트랜잭션 커밋
conn.commit()

# 연결 종료
cur.close()
conn.close()