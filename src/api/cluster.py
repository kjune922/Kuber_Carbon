
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from src.db import SessionLocal, ClusterStatus

router = APIRouter()


# DB 세션 의존성

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 클러스터 업데이트용 스키마

class ClusterUpdate(BaseModel):
    cluster_name: str
    cpu_usage: float
    memory_usage: float
    carbon_emission: float



# 클러스터 상태 등록 / 갱신

@router.post("/update-cluster/")
def update_cluster_status(data: ClusterUpdate, db: Session = Depends(get_db)):
    cluster = db.query(ClusterStatus).filter(ClusterStatus.cluster_name == data.cluster_name).first()

    if cluster:
        cluster.cpu_usage = data.cpu_usage
        cluster.memory_usage = data.memory_usage
        cluster.carbon_emission = data.carbon_emission
    else:
        cluster = ClusterStatus(
            cluster_name=data.cluster_name,
            cpu_usage=data.cpu_usage,
            memory_usage=data.memory_usage,
            carbon_emission=data.carbon_emission
        )
        db.add(cluster)

    db.commit()
    db.refresh(cluster)
    return {"message": f"{cluster.cluster_name}의 상태가 DB에 잘 저장됐음ㅎ"}



# 모든 클러스터 상태 조회

@router.get("/get-clusters/")
def get_clusters(db: Session = Depends(get_db)):
    clusters = db.query(ClusterStatus).all()
    if not clusters:
        return {"message": "저장된 클러스터가 없습니다"}

    return [
        {
            "클러스터 이름": c.cluster_name,
            "CPU 사용률": c.cpu_usage,
            "메모리 사용률": c.memory_usage,
            "탄소 배출량": c.carbon_emission,
            "갱신시각": c.updated_at
        }
        for c in clusters
    ]
