import streamlit as st
import pandas as pd
import requests
import folium
from streamlit_folium import st_folium

# --- 페이지 기본 설정 ---
st.set_page_config(page_title="한강 나들이 지수 대시보드", page_icon="🚲", layout="wide")

st.title("🚲 오늘 한강 가도 될까? (실시간 나들이 지수)")
st.write("한강 공원 주변의 날씨와 따릉이 현황을 확인해보세요!")

# 1. 한강 공원 선택
parks = {
    "여의도 한강공원": {"lat": 37.5271, "lon": 126.9328},
    "반포 한강공원": {"lat": 37.5105, "lon": 126.9960},
    "뚝섬 한강공원": {"lat": 37.5315, "lon": 127.0667}
}
selected_park = st.selectbox("가고 싶은 한강 공원을 선택하세요:", list(parks.keys()))
lat = parks[selected_park]["lat"]
lon = parks[selected_park]["lon"]

# 2. 실시간 날씨 데이터 가져오기 (Open-Meteo API - 무료, 키 필요없음)
@st.cache_data
def get_weather(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()["current_weather"]
    except Exception as e:
        return None
    return None

weather = get_weather(lat, lon)

# 3. 따릉이 가상 데이터 생성 
# (인증키 발급 대기 시간 없이 즉시 실행 가능한 프로토타입 구현을 위해 가상 데이터 사용)
bike_stations = pd.DataFrame({
    "대여소명": [f"{selected_park} 제1입구", f"{selected_park} 편의점 앞", f"{selected_park} 광장"],
    "위도": [lat + 0.002, lat - 0.001, lat + 0.003],
    "경도": [lon + 0.001, lon + 0.002, lon - 0.002],
    "잔여대수": [15, 3, 8]
})

# --- 화면 구성 ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("🌡️ 현재 날씨")
    if weather:
        st.metric(label="현재 온도", value=f"{weather['temperature']} °C")
        st.metric(label="현재 풍속", value=f"{weather['windspeed']} km/h")
        
        # 나들이 지수 로직
        if weather['temperature'] > 15 and weather['windspeed'] < 20:
            st.success("날씨가 완벽해요! 당장 출발하세요. 🏃‍♂️")
        else:
            st.warning("바람이 강하거나 쌀쌀할 수 있어요. 겉옷을 꼭 챙기세요! 🧥")
    else:
        st.error("날씨 정보를 불러오지 못했습니다.")

with col2:
    st.subheader("🚲 인근 따릉이 잔여 현황")
    st.dataframe(bike_stations[["대여소명", "잔여대수"]], hide_index=True)

# 4. 지도 시각화 (Folium)
st.subheader("🗺️ 공원 및 대여소 위치")
m = folium.Map(location=[lat, lon], zoom_start=15)

# 선택한 공원 중심 마커
folium.Marker([lat, lon], popup=selected_park, icon=folium.Icon(color="red", icon="star")).add_to(m)

# 자전거 대여소 마커
for idx, row in bike_stations.iterrows():
    folium.Marker(
        [row["위도"], row["경도"]],
        popup=f"{row['대여소명']} (잔여: {row['잔여대수']}대)",
        icon=folium.Icon(color="blue", icon="bicycle", prefix='fa')
    ).add_to(m)

# Streamlit 화면에 지도 렌더링
st_folium(m, width=800, height=400)