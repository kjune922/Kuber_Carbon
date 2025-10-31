from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from datetime import datetime
import os


#   PostgreSQL 연결 설정

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://kjune922:dlrudalswns2@postgres_kuber:5432/kuber_db"
)

engine = create_engine(DATABASE_URL)
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()


#   TaskResult 모델 (Celery 작업 결과)

class TaskResult(Base):
    __tablename__ = "task_results"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String, unique=True, index=True)
    status = Column(String)
    result = Column(String)



#   ClusterStatus 모델 (클러스터 상태)

class ClusterStatus(Base):
    __tablename__ = "cluster_status"

    id = Column(Integer, primary_key=True, index=True)
    cluster_name = Column(String, unique=True, index=True)
    region = Column(String, nullable=True)  # 한국, 일본 추가
    cpu_usage = Column(Float)
    memory_usage = Column(Float)
    carbon_intensity = Column(Float)
    network_latency = Column(Float, nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow)


#   DB 초기화 함수

def init_db():
    """테이블 자동 생성"""
    Base.metadata.create_all(bind=engine)
    print("[DB 초기화 완료] 테이블이 존재하지 않으면 자동 생성됨.")
