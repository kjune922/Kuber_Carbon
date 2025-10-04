import random
from celery import Celery
from src.db import SessionLocal, ClusterStatus

celery_app = Celery(
  "auto_updater",
  broker="redis://redis_kuber:6379/0",
  backend="redis://redis_kuber:6379/0"
)

@celery_app.task
def auto_update_clusters():
  # 클러스터 상태를 주기적으로 자동 업뎃
  db = SessionLocal()
  try:
    clusters = db.query(ClusterStatus).all() # ClusterStatus 테이블을 대상으로 쿼리를 시작하겠다는 코드
    if not clusters: # 근데 없으면? 
      print("클러스터 데이터가 없습니다")
      return
    
    for cluster in clusters:
      cluster.cpu_usage = round(random.uniform(20,90),2) # 20.0과 90.0사이에서 랜덤실수하나 만들고 소수점 둘째 자리까지 반올림!
      cluster.memory_usage = round(random.uniform(30,95),2)
      cluster.carbon_emission = round(random.uniform(1000,3000),2)
      
    db.comiit()
    print("클러스터 상태 자동 업뎃 완")
  finally:
    db.close()