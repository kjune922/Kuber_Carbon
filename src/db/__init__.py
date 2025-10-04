import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://kjune0922:dlrudalswns2@postgres_kuber:5432/kuber_db"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# TaskResult 모델 정의

class TaskResult(Base):
  __tablename__ = "task_results"
  
  id = Column(Integer, primary_key=True, index=True)
  task_id = Column(String, unique=True, index=True)
  status = Column(String)
  result = Column(String)

# 클러스터 상태 테이블 (클러스터의 상태와 탄소량 저장 테이블)
class ClusterStatus(Base):
  __tablename__ = "cluster_status"
  
  id = Column(Integer, primary_key=True,index=True)
  cluster_name = Column(String, unique = True, index = True)
  cpu_usage = Column(Float) ## cpu사용량
  memory_usage = Column(Float) ## 메모리 사용량
  carbon_emission = Column(Float) ## 탄소 배출략
  updated_at = Column(DateTime, default=datetime.now)



# 테이블 초기화 함수

def init_db():
  Base.metadata.create_all(bind=engine)