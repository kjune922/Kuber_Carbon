from fastapi import FastAPI, Depends
from pydantic import BaseModel
from src.celery_app import celery_app, add, run_real_carbon_scheduler_task
from celery.result import AsyncResult
from sqlalchemy.orm import Session
from src.db import SessionLocal, init_db, TaskResult, ClusterStatus
from src.scheduler.carbon_scheduler import select_optimal_cluster

app = FastAPI()

# DB 세션
# 세션 ---> DB연결에 필요한 --> engine -> DB로 가는 자동차, session -> 그 차를 운전하는 운전자
def get_db():
  db = SessionLocal()  # 실제 DB연결 열겠다 --> 이걸 코드를짜야지 select, insert, update, delete 같은 쿼리를 쓸 수 있음
  try:
    yield db # 라우터에 db를 전달 --> FastAPI에서 주로씀 yield를 쓰면 라우터함수가 실행되는 동안 db를 열고, 끝나면 닫으란 뜻
  finally:
    db.close() # 끝나면 db 닫아버리기

@app.on_event("startup") # 서버 시작할때마다 테이블을 생성
def startup_event():
  init_db() # 이 부분이 테이블이 없으면 자동으로 테이블 생성
  
## 클러스터 상태등록 / 갱신용 스키마
class ClusterUpdate(BaseModel):
  cluster_name: str
  cpu_usage: float
  memory_usage: float
  carbon_emission: float
  
## 클러스터의 상태등록과 업데이트부분
@app.post("/update-cluster/")
def update_cluster_status(data: ClusterUpdate, db: Session = Depends(get_db)):
  cluster = db.query(ClusterStatus).filter(ClusterStatus.cluster_name == data.cluster_name).first()
  
  if cluster:
    # 만약 클러스터가져올거 있으면 기존 클러스터 업데이트해주고
    cluster.cpu_usage = data.cpu_usage
    cluster.memory_usage = data.memory_usage
    cluster.carbon_emission = data.carbon_emission
  else:
    # 없으면 새 클러스터 업뎃 ㄱㄱ
    cluster = ClusterStatus(
      cluster_name = data.cluster_name,
      cpu_usage = data.cpu_usage,
      memory_usage = data.memory_usage,
      carbon_emission = data.carbon_emission
    )
    db.add(cluster)
  db.commit()
  return {
    "message" : f"{data.cluster_name}의 상태가 DB에 잘 저장됐음ㅎ"
  }

@app.get("/")
def root():
  return {
    "message" : "이경준의 쿠버네티스프로젝트"
  }
  
# Celery Task 실행부분
@app.get("/add-task/")
def run_add_task(x: int,y: int):
  task = add.delay(x,y) # 비동기로 실행할수있게하는 task부분
  return {
    "task_id": task.id
  }
  
# 탄소스케줄러 task
@app.get("/scheduler-task/") 
def scheduler_task():
  result = select_optimal_cluster()
  return result 
  
  
  
# Task 결과확인
@app.get("/task-result/{task_id}")
def get_task_result(task_id: str):
  result = AsyncResult(task_id, app=celery_app)
  return {
    "task_id": task_id,
    "상태": result.status,
    "결과": result.result
  }

# DB 저장된 결과 조회 -> 초기테스트버전

@app.get("/db-results/")
def read_db_results(db: Session = Depends(get_db)):
  results = db.query(TaskResult).all()
  output = []
  for r in results:
    
    row = {
      "id": r.id,
      "task_id": r.task_id,
      "status": r.status,
      "result": r.result
    }
    output.append(row)
  return output

# 모든 클러스터 상태 조회

@app.get("/get-clusters/")
def get_clusters(db: Session = Depends(get_db)):
  clusters = db.query(ClusterStatus).all()
  
  if not clusters:
    return {
      "message" : "저장된 클러스터가 없습니다"
    }
    
  result = []
  for c in clusters:
    result.append ({
      "클러스터 이름" : c.cluster_name,
      "CPU 사용률" : c.cpu_usage,
      "메모리 사용률" : c.memory_usage,
      "탄소 배출량" : c.carbon_emission,
    })
  return result
  
## 실전 클러스터

@app.post("/real-carbon-schedule/")
def trigger_real_carbon_schedule():
  task = run_real_carbon_scheduler_task.delay()
  return {
    "task_id" : task.id,
    "message" : "실전 real 탄소 스케줄링 작업 시작함"
  }
  
@app.get("/carbon-status/")
def carbon_status():
    """
    최근 탄소 스케줄링 실행 결과를 조회
    (Celery Beat이 저장한 TaskResult 데이터를 최신 순으로 반환)
    """
    db = SessionLocal()
    results = db.query(TaskResult).order_by(TaskResult.id.desc()).limit(10).all()
    db.close()
    return [
        {
            "id": r.id,
            "task_id": r.task_id,
            "status": r.status,
            "result": r.result
        }
        for r in results
    ]