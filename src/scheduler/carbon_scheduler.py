# DB에서 모든 클러스터의 탄소 배출량 / 자원 상태 조회
# 탄소 배출량이 "가장 낮은 클러스터" 자동적으로 선택
# 선택된 클러스터에 "작업 배치 요청" 반환 (2025-10-04기준 단순히 선택 결과만 리턴하고있음 아직은)

from sqlalchemy.orm import Session
from src.db import SessionLocal, ClusterStatus

def select_optimal_cluster(): # FastAPI에서 API로 호출할수있게 연동 ㄱㄱ
  db: Session = SessionLocal()
  try:
    clusters = db.query(ClusterStatus).all()
    if not clusters:
      return {
        "message" : "안에 가능한 클러스터가없음요"
      }
    
    best_cluster = min(clusters, key=lambda c: c.carbon_emission) # 파이썬 람다비교식임 -> clusters,안에 carbon_emission을 c라고한뒤
    # 가장 작은 c값을 best_cluster로 지정
    return {
      "선택된 클러스터" : best_cluster.cluster_name,
      "탄소 배출량 " : best_cluster.carbon_emission,
      "CPU 사용률" : best_cluster.cpu_usage,
      "메모리 사용률" : best_cluster.memory_usage,
    }
  finally:
    db.close() 