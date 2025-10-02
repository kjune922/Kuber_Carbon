from celery import Celery
import os
from src.db import SessionLocal, TaskResult

'''
app = Celery(
  'tasks', 
  backend='redis://localhost:6379', # worker와 작업결과를 저장하기위해 저장할 백엔드 선언
  broker="redis://localhost:6379" # Celery를 사용하기위해 task메세지들을 주고받기위한 message broker선언했음
  )
'''

# 그러나 docker로 한방에 할려고 backend나 broker주소를 매번 타이핑하긴싫으니 celery_broken_url, celery_result_backend 로 컨테이너환경변수로 선언

broken_url = os.getenv("CELERY_BROKEN_URL","redis://redis_kuber:6379/0") # 0은 DB번호
backend_url = os.getenv("CELERY_RESULT_BACKEND","redis://redis_kuber:6379/0") # 0은 DB번호

celery_app = Celery(
  "worker",
  broker = broken_url,
  backend = backend_url
)

@celery_app.task
def add(x,y):
  result_value = x + y
  db = SessionLocal()
  try:
    db_result = TaskResult(
      task_id=add.request.id, # Celery task id임
      status="성공!!!!",
      result=str(result_value)
    )
    db.add(db_result)
    db.commit()
  finally:
    db.close()
  return result_value
