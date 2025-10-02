from fastapi import FastAPI, Depends
from src.celery_app import celery_app, add
from celery.result import AsyncResult
from sqlalchemy.orm import Session
from src.db import SessionLocal, init_db, TaskResult

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
  
# Task 결과확인
@app.get("/task-result/{task_id}")
def get_task_result(task_id: str):
  result = AsyncResult(task_id, app=celery_app)
  return {
    "task_id": task_id,
    "상태": result.status,
    "결과": result.result
  }

# DB 저장된 결과 조회

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
  
