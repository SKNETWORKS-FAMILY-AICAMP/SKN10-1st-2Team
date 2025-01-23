import pymysql
import pandas as pd
import streamlit as st
import openpyxl
#DB 연결 user, password, db 변경할것
conn = pymysql.connect( 
    host = 'localhost',
    user = 'car',
    password = 'test1234',
    database = 'vehicle'
)

cur = conn.cursor()
file_name = r'C:/Users/tnstn/Downloads/자동차등록현황보고_자동차등록대수현황 시도별 (201101 ~ 202412).xlsx'
# openpyxl 엔진을 명시적으로 지정하여 엑셀 파일 읽기
df = pd.read_excel(file_name, header=[0, 1],skiprows=4)
commit_interval = 1000

for i in range(len(df)) :
    try :
        row = list(df.loc[i])
        # 추출할 열 이름 (뒤에서 1번째, 5번째, 9번째, 13번째, 17번째)
        indices = [-1, -5, -9, -13, -17]
        extracted = [row[col] for col in indices]

        # 결측치 및 데이터 변환
        data = [
            int(str(val).replace(',', '')) if pd.notnull(val) and isinstance(val, str) else int(val)
            for val in extracted
        ]
        data += [row[2],row[1],row[0]]
        
        sql = f"""insert vehicle_registration (total_count,special_count,truck_count
        ,van_count,sedan_count,city,state,registration_date)
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