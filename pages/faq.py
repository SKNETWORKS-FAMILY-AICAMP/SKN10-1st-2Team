import streamlit as st
import pandas as pd
import pymysql

st.set_page_config(page_title="브랜드별 FAQ", page_icon="📠")
st.title("브랜드별 FAQ")

data = {
    'id': [],
    'question': [],
    'answer': []
}
# 출력 옵션 변경
pd.set_option('display.max_colwidth', None)  # 열 너비 제한 해제
pd.set_option('display.width', 1000)         # 전체 출력 너비를 1000으로 설정
pd.set_option('display.max_rows', 1000)      # 최대 1000행 출력
pd.set_option('display.max_columns', 100)    # 최대 100열 출력

conn = pymysql.connect( 
    host = 'localhost',
    user = 'car',
    password = 'test1234',
    database = 'vehicle'
)
cur = conn.cursor()

#select해서 faq의 id, 질문, 답변 가져오기기
sql = """select id,question,answer from faq"""
cur.execute(sql)
results =  cur.fetchall()

for i in range(len(results)) :
    with st.expander(str(results[i][0]) +". "+results[i][1]):
        st.write(results[i][2])



