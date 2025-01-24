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
def get_data(month, province=None, district=None):
    query = f"""
    SELECT province, district, 
           SUM(passenger) AS 총_승용차, 
           SUM(bus) AS 총_승합차, 
           SUM(truck) AS 총_화물차,
           SUM(special) AS 총_특수차
    FROM car_registration
    WHERE month = '{month}'
    """
    if province:
        query += f" AND province = '{province}'"
    if district:
        query += f" AND district = '{district}'"
    query += " GROUP BY province, district;"
    engine = get_engine()
    return pd.read_sql(query, con=engine)

def get_monthly_data(province, district=None):
    query = f"""
    SELECT month AS 월,
           SUM(passenger) AS 총_승용차, 
           SUM(bus) AS 총_승합차,
           SUM(truck) AS 총_화물차,
           SUM(special) AS 총_특수차
    FROM car_registration
    WHERE province = '{province}'
    """
    if district:
        query += f" AND district = '{district}'"
    query += " GROUP BY month ORDER BY month;"
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
months_query = "SELECT DISTINCT month FROM car_registration ORDER BY month;"
available_months = pd.read_sql(months_query, con=engine)['month'].tolist()

# 사용자 입력: 월, 시도, 시군구 선택
month = st.sidebar.selectbox("분석할 월을 선택하세요:", available_months)

if month:
    st.sidebar.write(f"선택한 월: **{month}**")
    
    # 시도 선택
    provinces_query = "SELECT DISTINCT province FROM car_registration ORDER BY province;"
    available_provinces = pd.read_sql(provinces_query, con=engine)['province'].tolist()
    province = st.sidebar.selectbox("시도를 선택하세요:", ["전체"] + available_provinces)
    selected_province = None if province == "전체" else province

    # 시군구 선택
    districts = []
    if selected_province:
        districts_query = f"""
        SELECT DISTINCT district FROM car_registration 
        WHERE province = '{selected_province}' ORDER BY district;
        """
        districts = pd.read_sql(districts_query, con=engine)['district'].tolist()
    district = st.sidebar.selectbox("시군구를 선택하세요:", ["전체"] + districts)
    selected_district = None if district == "전체" else district

    # 데이터 가져오기
    df = get_data(month, province=selected_province, district=selected_district)

    if df.empty:
        st.warning("선택한 조건에 해당하는 데이터가 없습니다.")
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
                title=f"{month} 지역별 차량 유형 비율",
                labels={'value': '등록 대수', 'variable': '차량 유형', 'province': '지역'},
                barmode='stack',
                height=600
            )
            st.plotly_chart(fig_stack)

        # 지역별 데이터 트렌드
        elif page == "지역별 데이터 트렌드":
            st.title("📈 지역별 데이터 트렌드")
            
            # 특정 시도의 데이터를 선택하세요
            province = st.selectbox("특정 시도의 데이터를 선택하세요:", df['province'].unique(), key="trend_province")
            
            if province:
                # 시군구 선택
                district_options = ["전체"] + df[df['province'] == province]['district'].dropna().unique().tolist()
                district = st.selectbox(
                    "시군구를 선택하세요:", 
                    district_options, 
                    key=f"trend_district_{province}"  # 각 시도에 대해 고유 키 설정
                )
                selected_district = None if district == "전체" else district

                # 데이터 가져오기
                monthly_data = get_monthly_data(province, district=selected_district)

                # 데이터가 존재하는 경우 그래프 생성
                if not monthly_data.empty:
                    fig_trend = px.line(
                        monthly_data,
                        x='월',
                        y=['총_승용차', '총_승합차', '총_화물차', '총_특수차'],
                        title=f"{province} {district if district else ''} 월별 차량 데이터 변화",
                        labels={'value': '등록 대수', 'variable': '차량 유형'},
                        height=600
                    )
                    st.plotly_chart(fig_trend)
                else:
                    st.warning(f"선택한 지역 ({province} {district if district else ''})에 데이터가 없습니다.")

        # 두 지역 비교
        elif page == "두 지역 비교":
            st.title("📊 두 지역 간 차량 유형 비율 비교")

            # 전체 데이터를 기반으로 비교를 위한 지역 선택
            all_provinces = available_provinces  # 모든 지역 리스트 생성

            # 첫 번째 지역 선택
            region1 = st.selectbox("첫 번째 지역 선택:", all_provinces, key="region1")

            # 두 번째 지역 선택 (첫 번째 지역 제외)
            remaining_provinces = [province for province in all_provinces if province != region1]
            region2 = st.selectbox("두 번째 지역 선택:", remaining_provinces, key="region2")

            if region1 and region2:
                # 두 지역 데이터 필터링
                filtered_data = get_data(month)
                compare_data = filtered_data[filtered_data['province'].isin([region1, region2])].copy()

                # 데이터가 비어 있는 경우 처리
                if compare_data.empty:
                    st.warning(f"선택된 두 지역 ({region1}, {region2})에 대한 데이터가 없습니다.")
                else:
                    # 비율 계산
                    compare_data['총_등록대수'] = compare_data[['총_승용차', '총_승합차', '총_화물차', '총_특수차']].sum(axis=1)
                    compare_data['승용차_비율'] = compare_data['총_승용차'] / compare_data['총_등록대수'] * 100
                    compare_data['승합차_비율'] = compare_data['총_승합차'] / compare_data['총_등록대수'] * 100
                    compare_data['화물차_비율'] = compare_data['총_화물차'] / compare_data['총_등록대수'] * 100
                    compare_data['특수차_비율'] = compare_data['총_특수차'] / compare_data['총_등록대수'] * 100

                    # 데이터를 길게 변환하여 그래프 그리기
                    compare_data_long = compare_data.melt(
                        id_vars=['province'],
                        value_vars=['승용차_비율', '승합차_비율', '화물차_비율', '특수차_비율'],
                        var_name='차량 유형',
                        value_name='비율'
                    )

                    # 그래프 생성
                    fig_compare = px.bar(
                        compare_data_long,
                        x='province',
                        y='비율',
                        color='차량 유형',
                        title=f"{region1} vs {region2} 차량 유형 비율 비교",
                        labels={'비율': '등록 대수', 'province': '지역', '차량 유형': '차량 유형'},
                        barmode='group',
                        height=600
                    )
                    st.plotly_chart(fig_compare)



        # 데이터 예측
        elif page == "데이터 예측":
            st.title("📈 데이터 예측")

            # 중복 제거된 시도 데이터 가져오기
            provinces_query = "SELECT DISTINCT province FROM car_registration ORDER BY province;"
            available_provinces = pd.read_sql(provinces_query, con=engine)['province'].drop_duplicates().tolist()

            # 데이터 예측을 위한 시도 선택
            province = st.selectbox("데이터 예측을 위한 시도 선택", available_provinces, key="prediction_province")

            # 시군구 데이터 가져오기
            if province:
                districts_query = f"""
                SELECT DISTINCT district FROM car_registration 
                WHERE province = '{province}' 
                ORDER BY district;
                """
                available_districts = pd.read_sql(districts_query, con=engine)['district'].drop_duplicates().tolist()
                district_options = ["전체"] + available_districts
                district = st.selectbox("시군구를 선택하세요:", district_options, key="prediction_district")
                selected_district = None if district == "전체" else district

            # 차량 유형 선택
            vehicle_type = st.selectbox(
                "예측할 차량 유형을 선택하세요:",
                ['총_승용차', '총_승합차', '총_화물차', '총_특수차'],
                format_func=lambda x: x.replace("총_", "")  # UI에서 "총_" 제거
            )

            if province and vehicle_type:
                # 월별 데이터 가져오기
                trend_data = get_monthly_data(province, district=selected_district)
                trend_data['month_num'] = range(len(trend_data))  # 월을 숫자로 변환

                # 예측 모델 학습
                model = LinearRegression()
                x = trend_data[['month_num']]
                y = trend_data[vehicle_type]
                model.fit(x, y)

                # 다음 달 예측
                next_month = pd.DataFrame({'month_num': [len(trend_data)]})
                prediction = model.predict(next_month)[0]

                # 결과 출력 메시지 구성
                vehicle_name = vehicle_type.replace("총_", "")  # "총_" 제거
                location = f"{province}" + (f" {selected_district}" if selected_district else "")
                st.write(f"**{location}**의 미래 {vehicle_name} 등록 대수 예측: **{int(prediction)}** 대")

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
                    title=f"{location} 월별 {vehicle_name} 등록 대수 및 예측",
                    markers=True,
                    height=600
                )
                st.plotly_chart(fig_prediction)

