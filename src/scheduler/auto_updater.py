import requests
from datetime import datetime
from src.db import SessionLocal, ClusterStatus
import logging

logging.basicConfig(level=logging.INFO)

# 실제 Caspian API 엔드포인트 (예시 URL)
CASPIAN_API_BASE = "http://caspian-api.kuberzo.internal"  # Caspian Metric API 주소로 교체

def fetch_caspian_metrics(cluster_name: str):
    """Caspian API에서 CPU, 메모리, 탄소지표 가져오기"""
    try:
        resp = requests.get(f"{CASPIAN_API_BASE}/metrics/{cluster_name}", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            return {
                "cpu": data.get("cpu_usage"),
                "mem": data.get("memory_usage"),
                "co2": data.get("carbon_intensity")
            }
        else:
            logging.warning(f"[{cluster_name}] API 응답 오류: {resp.status_code}")
    except Exception as e:
        logging.error(f"[{cluster_name}] API 연결 실패: {e}")
    return None

def auto_update_clusters():
    """Caspian에서 클러스터 상태 갱신"""
    session = SessionLocal()
    clusters = ["caspian-a", "caspian-b", "caspian-c"]  # 실제 Caspian 등록된 클러스터 이름

    for name in clusters:
        metrics = fetch_caspian_metrics(name)
        if not metrics:
            continue

        existing = session.query(ClusterStatus).filter_by(cluster_name=name).first()
        if existing:
            existing.cpu_usage = metrics["cpu"]
            existing.memory_usage = metrics["mem"]
            existing.carbon_intensity = metrics["co2"]
            existing.last_updated = datetime.utcnow()
        else:
            new_cluster = ClusterStatus(
                cluster_name=name,
                cpu_usage=metrics["cpu"],
                memory_usage=metrics["mem"],
                carbon_intensity=metrics["co2"],
                last_updated=datetime.utcnow(),
            )
            session.add(new_cluster)
        logging.info(f"[{name}] 갱신 완료: {metrics}")

    session.commit()
    session.close()
    return "Cluster metrics updated"
