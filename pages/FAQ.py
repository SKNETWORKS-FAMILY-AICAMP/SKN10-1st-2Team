import streamlit as st
import pandas as pd
import pymysql

st.set_page_config(page_title="브랜드별 FAQ", page_icon="📠")
st.title("브랜드별 FAQ")

# DB 연결
conn = pymysql.connect( 
    host = 'localhost',
    user = 'SKN_10_2',
    password = 's1234',
    database = 'car_db'
)
cur = conn.cursor()

# 드롭다운 메뉴 생성 
col1, col2 = st.columns([5,1]) 

with col1:
    st.write("")

with col2:
    option = st.radio(
        "",  
        ("기아", "현대") 
)

# <br> 태그를 사용해 줄 바꿈
st.markdown("<br>", unsafe_allow_html=True)

# 옵션에 따라 faq 출력!
sql = f"""select id,question,answer from faq where company = '{option}'"""
cur.execute(sql)
results =  cur.fetchall()

for i in range(len(results)) :
    with st.expander(str(results[i][0]) +". "+results[i][1]):
        st.write(results[i][2])



