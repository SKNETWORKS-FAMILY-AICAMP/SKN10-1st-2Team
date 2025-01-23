import streamlit as st
import pandas as pd
import numpy as np
import pymysql
import streamlit as st
import matplotlib.pyplot as plt
import streamlit as st
from matplotlib import font_manager

# 한글 폰트 설정 (Windows의 경우)
font_path = 'C:/Windows/Fonts/malgun.ttf'  # 윈도우에서는 'malgun.ttf' 폰트를 사용
font_prop = font_manager.FontProperties(fname=font_path)
plt.rcParams['font.family'] = font_prop.get_name()

#탭 표시 꾸미기
st.set_page_config(page_title="전국 자동차 현황", page_icon="🚗")
st.title("전국 자동차 현황")

option = st.radio(
    "",  # 라디오 버튼의 질문
    ("연도별", "시/군별", "용도별")  # 선택 가능한 옵션들
)

conn = pymysql.connect( 
    host = 'localhost',
    user = 'car',
    password = 'test1234',
    database = 'vehicle'
)
cur = conn.cursor()



if option == "시/군별" :
    #matplotlib은 한국어 라벨을 지원하지 않기 때문에 한글폰트 설정을 따로 해야된다.
    #9줄에 한글 폰트 설정 참고

    sql = f"""select state,total_count from vehicle_registration 
            where 1=1 and city = '계' and registration_date= '2024-01'"""
    cur.execute(sql)  # sql문 실행
    results = cur.fetchall()
    
    data = {'region' : [], 'count' : []}
    for i in range(17) :
        data['region'].append(results[i][0])
        data['count'].append(results[i][1])
    
    # 데이터프레임 생성
    df = pd.DataFrame(data)

    # x축: year, y축: 승용, 승합, 화물, 특수
    st.bar_chart(df.set_index('region')['count'])

elif option == "용도별" :
    data = {
    'year': [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024],
    '승용': [500000, 550000, 600000, 650000, 700000, 750000, 800000, 850000, 900000, 950000],
    '승합': [100000, 110000, 120000, 130000, 140000, 150000, 160000, 170000, 180000, 190000],
    '화물': [200000, 210000, 220000, 230000, 240000, 250000, 260000, 270000, 280000, 290000],
    '특수': [50000, 60000, 70000, 80000, 90000, 100000, 110000, 120000, 130000, 140000]
    }

    # 데이터프레임 생성
    df = pd.DataFrame(data)

    # x축: year, y축: 승용, 승합, 화물, 특수
    st.bar_chart(df.set_index('year'))

elif option == "연도별" :
    pass






