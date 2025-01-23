import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
from sklearn.linear_model import LinearRegression
import numpy as np

# SQLAlchemy 연결 설정
def get_engine():
    return create_engine("mysql+pymysql://SKN_10_2:s1234@localhost/car_db")

# 데이터 가져오기
def get_data(month):
    query = f"""
    SELECT province, 
           SUM(passenger) AS 총_승용차, 
           SUM(bus) AS 총_승합차,
           SUM(truck) AS 총_화물차,
           SUM(special) AS 총_특수차
    FROM car_registration
    WHERE `month` = '{month}'
    GROUP BY province;
    """
    engine = get_engine()
    return pd.read_sql(query, con=engine)

def get_monthly_data(province):
    query = f"""
    SELECT `month` AS 월,
           SUM(passenger) AS 총_승용차, 
           SUM(bus) AS 총_승합차,
           SUM(truck) AS 총_화물차,
           SUM(special) AS 총_특수차
    FROM car_registration
    WHERE province = '{province}'
    GROUP BY `month`
    ORDER BY `month`;
    """
    engine = get_engine()
    return pd.read_sql(query, con=engine)

# 페이지 구조
st.set_page_config(page_title="차량 등록 데이터 분석", layout="wide")
st.sidebar.title("🚗 페이지 탐색")

# 페이지 이름 설정
pages = ["데이터 테이블과 분석", "지역별 데이터 트렌드", "두 지역 비교", "데이터 예측"]
page = st.sidebar.radio("페이지를 선택하세요:", pages)

# 공통 데이터
engine = get_engine()
months_query = "SELECT DISTINCT `month` FROM car_registration ORDER BY `month`;"
available_months = pd.read_sql(months_query, con=engine)['month'].tolist()

month = st.sidebar.selectbox("분석할 월을 선택하세요:", available_months)

if month:
    st.sidebar.write(f"선택한 월: **{month}**")
    df = get_data(month)

    if df.empty:
        st.warning("선택한 월에 대한 데이터가 없습니다.")
    else:
        # 데이터 테이블과 분석
        if page == "데이터 테이블과 분석":
            st.title("📊 데이터 테이블과 분석")
            df['총_등록대수'] = df[['총_승용차', '총_승합차', '총_화물차', '총_특수차']].sum(axis=1)
            df['승용차_비율'] = df['총_승용차'] / df['총_등록대수'] * 100
            df['승합차_비율'] = df['총_승합차'] / df['총_등록대수'] * 100
            df['화물차_비율'] = df['총_화물차'] / df['총_등록대수'] * 100
            df['특수차_비율'] = df['총_특수차'] / df['총_등록대수'] * 100

            st.subheader("데이터 테이블")
            st.dataframe(df)

            st.subheader("차량 유형 비율 - 스택 바 차트")
            fig_stack = px.bar(
                df,
                x='province',
                y=['승용차_비율', '승합차_비율', '화물차_비율', '특수차_비율'],
                title=f"{month} 시도별 차량 유형 비율",
                labels={'value': '비율 (%)', 'variable': '차량 유형', 'province': '시도'},
                barmode='stack',
                height=600
            )
            st.plotly_chart(fig_stack)

        # 지역별 데이터 트렌드
        elif page == "지역별 데이터 트렌드":
            st.title("📈 지역별 데이터 트렌드")
            province = st.selectbox("특정 시도의 데이터를 선택하세요:", df['province'])
            if province:
                monthly_data = get_monthly_data(province)
                fig_trend = px.line(
                    monthly_data,
                    x='월',
                    y=['총_승용차', '총_승합차', '총_화물차', '총_특수차'],
                    title=f"{province} 월별 차량 데이터 변화",
                    labels={'value': '등록 대수', 'variable': '차량 유형'},
                    height=600
                )
                st.plotly_chart(fig_trend)

        # 두 지역 비교
        elif page == "두 지역 비교":
            st.title("📊 두 지역 간 차량 유형 비율 비교")
            region1 = st.selectbox("첫 번째 지역 선택:", df['province'], key="region1")
            region2 = st.selectbox("두 번째 지역 선택:", df['province'], key="region2")

            if region1 and region2 and region1 != region2:
                compare_data = df[df['province'].isin([region1, region2])].copy()
                compare_data['총_등록대수'] = compare_data[['총_승용차', '총_승합차', '총_화물차', '총_특수차']].sum(axis=1)
                compare_data['승용차_비율'] = compare_data['총_승용차'] / compare_data['총_등록대수'] * 100
                compare_data['승합차_비율'] = compare_data['총_승합차'] / compare_data['총_등록대수'] * 100
                compare_data['화물차_비율'] = compare_data['총_화물차'] / compare_data['총_등록대수'] * 100
                compare_data['특수차_비율'] = compare_data['총_특수차'] / compare_data['총_등록대수'] * 100

                compare_data_long = compare_data.melt(
                    id_vars=['province'], 
                    value_vars=['승용차_비율', '승합차_비율', '화물차_비율', '특수차_비율'],
                    var_name='차량 유형', 
                    value_name='비율'
                )

                fig_compare = px.bar(
                    compare_data_long,
                    x='province',
                    y='비율',
                    color='차량 유형',
                    title=f"{region1} vs {region2} 차량 유형 비율 비교",
                    labels={'비율': '비율 (%)', 'province': '시도', '차량 유형': '차량 유형'},
                    barmode='group',
                    height=600
                )
                st.plotly_chart(fig_compare)

        # 데이터 예측 페이지
        elif page == "데이터 예측":
            st.title("📈 데이터 예측")

            # 시도 선택
            province = st.selectbox("데이터 예측을 위한 시도 선택", df['province'], key="prediction_province")

            # 차량 유형 선택
            vehicle_type = st.selectbox(
                "예측할 차량 유형을 선택하세요:",
                ['총_승용차', '총_승합차', '총_화물차', '총_특수차'],
                format_func=lambda x: x.replace("총_", "")  # UI에서 "총_" 제거
            )

            if province and vehicle_type:
                # 월별 데이터 가져오기
                trend_data = get_monthly_data(province)
                trend_data['month_num'] = range(len(trend_data))  # 월을 숫자로 변환

                # 예측 모델 학습
                model = LinearRegression()
                x = trend_data[['month_num']]
                y = trend_data[vehicle_type]
                model.fit(x, y)

                # 다음 달 예측
                next_month = pd.DataFrame({'month_num': [len(trend_data)]})
                prediction = model.predict(next_month)[0]

                # 결과 출력
                vehicle_name = vehicle_type.replace("총_", "")  # "총_" 제거
                st.write(f"**{province}**의 미래 {vehicle_name} 등록 대수 예측: **{int(prediction)}** 대")

                # 기존 데이터와 예측 데이터 결합
                trend_data['예측'] = np.nan
                trend_data.loc[len(trend_data)] = {
                    '월': f"{trend_data['월'].iloc[-1]} (예측)",
                    'month_num': len(trend_data),
                    vehicle_type: prediction,
                    '예측': prediction
                }

                # 시각화 (기존 데이터 + 예측 데이터)
                st.subheader(f"{vehicle_name} 등록 대수 추세 및 예측")
                fig_prediction = px.line(
                    trend_data,
                    x='월',
                    y=[vehicle_type, '예측'],
                    labels={'value': '등록 대수', 'variable': '데이터 유형', '월': '월'},
                    title=f"{province} 월별 {vehicle_name} 등록 대수 및 예측",
                    markers=True,
                    height=600
                )
                st.plotly_chart(fig_prediction)

