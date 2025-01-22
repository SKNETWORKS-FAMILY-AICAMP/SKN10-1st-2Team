import streamlit as st
import pandas as pd

st.set_page_config(page_title="브랜드별 FAQ", page_icon="📠")
st.title("브랜드별 FAQ")

data = {
    'Name': ['기아', '현대'],
    'Age': [25,30],
    'City': ['Seoul', 'Seoul']
}

df = pd.DataFrame(data)

# 데이터프레임을 Streamlit에서 표시
st.dataframe(df)  # 상호작용 가능한 표
