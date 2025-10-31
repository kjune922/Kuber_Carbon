from fastapi import FastAPI
from src.db import SessionLocal, ClusterStatus, init_db
from src.celery_app import run_real_carbon_scheduler_task

app = FastAPI(title="Kuberzo Carbon-Aware Scheduler API")


#   DB 초기화
init_db()
#   기본 라우트
@app.get("/")
def root():
    return {"message": "쿠버조(Kuberzo) 탄소 인지형 스케줄링 API 정상 작동 중 "}


#   모든 클러스터 상태 조회

@app.get("/get-clusters")
def get_clusters():
    """현재 DB의 모든 클러스터 상태 조회"""
    session = SessionLocal()
    try:
        clusters = session.query(ClusterStatus).all()
        result = []
        for c in clusters:
            result.append({
                "id": c.id,
                "cluster_name": c.cluster_name,
                "region": c.region,
                "cpu_usage": c.cpu_usage,
                "memory_usage": c.memory_usage,
                "carbon_intensity": c.carbon_intensity,
                "network_latency": c.network_latency,
                "last_updated": c.last_updated,
            })
        return {"clusters": result}

    except Exception as e:
        print(f"[get-clusters 오류] {e}")
        return {"error": str(e)}

    finally:
        session.close()


#   현재 Caspian 스케줄러 결과 확인

@app.get("/run-scheduler")
def run_scheduler_now():
    """즉시 Caspian 스케줄러 실행 후 결과 반환"""
    result = run_real_carbon_scheduler_task.apply_async()
    return {"message": "스케줄러 실행 요청됨", "task_id": result.id}
