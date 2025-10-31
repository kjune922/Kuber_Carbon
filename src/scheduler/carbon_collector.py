import requests
from requests.auth import HTTPBasicAuth
from src.db import SessionLocal, ClusterStatus

# WattTime 계정 (이후 .env로 분리 권장)
USERNAME = "kjune922"
PASSWORD = "dlrudalswns2!"  # 실제 운영시 제거 권장

# 지역별 좌표
REGIONS = {
    "KR": {"lat": 37.5665, "lon": 126.9780},
    "JP": {"lat": 35.6762, "lon": 139.6503},
}

def fetch_wattime_token():
    """WattTime API 토큰 발급"""
    url = "https://api.watttime.org/login"
    res = requests.get(url, auth=HTTPBasicAuth(USERNAME, PASSWORD))
    if res.status_code == 200:
        return res.json().get("token")
    else:
        raise Exception(f"WattTime login failed: {res.text}")

def get_carbon_intensity(token, lat, lon):
    """위도/경도 기준으로 현재 탄소 배출량 조회"""
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://api.watttime.org/v2/index?latitude={lat}&longitude={lon}"
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        data = res.json()
        return data.get("carbon_intensity", None)
    else:
        print("WattTime intensity fetch failed:", res.text)
        return None

def update_cluster_carbon_intensity():
    """한국/일본 클러스터의 탄소 강도 실시간 업데이트"""
    session = SessionLocal()
    try:
        token = fetch_wattime_token()
        for region, coords in REGIONS.items():
            carbon_value = get_carbon_intensity(token, coords["lat"], coords["lon"])
            if carbon_value is None:
                continue

            cluster = session.query(ClusterStatus).filter_by(region=region).first()
            if cluster:
                cluster.carbon_intensity = round(carbon_value, 2)
                session.commit()
                print(f"[WattTime] {region} updated → {cluster.carbon_intensity} gCO₂/kWh")
            else:
                print(f"[WattTime] {region} cluster not found in DB")

    except Exception as e:
        print(f"[WattTime Collector Error] {e}")

    finally:
        session.close()
