import os
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://kjune922:dlrudalswns2@postgres_kuber:5432/kuberzo"
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

# 테이블 생성 함수 

def init_db():
  Base.metadata.create_all(bind=engine)