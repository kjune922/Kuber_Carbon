from celery import Celery
import os
from datetime import timedelta, datetime
import random
from src.db import SessionLocal, TaskResult, init_db, ClusterStatus
from src.scheduler.carbon_scheduler_real import run_real_carbon_scheduler
from src.scheduler.carbon_collector import update_cluster_carbon_intensity


#   Celery 기본 설정


broker_url = os.getenv("CELERY_BROKER_URL", "redis://redis_kuber:6379/0")
backend_url = os.getenv("CELERY_RESULT_BACKEND", "redis://redis_kuber:6379/0")

celery_app = Celery(
    "worker",
    broker=broker_url,
    backend=backend_url
)

celery_app.conf.timezone = 'Asia/Seoul'

# DB 초기화
init_db()


#   Celery Beat 스케줄링 설정


celery_app.conf.beat_schedule = {
    # 실시간 탄소 스케줄러 (1분마다 실행)
    '탄소 스케줄러 실행': {
        'task': 'src.celery_app.run_real_carbon_scheduler_task',
        'schedule': timedelta(minutes=1),
    },
    # 클러스터 자동 초기화 (30초마다)
    'auto-initialize-clusters': {
        'task': 'src.celery_app.auto_initialize_clusters',
        'schedule': 30.0,
    },
}



#   기본 add() 작업 - 단순 연산 + DB 저장


@celery_app.task
def add(x, y):
    """단순 덧셈 작업 + 결과를 DB에 저장"""
    result_value = x + y
    session = None
    try:
        session = SessionLocal()
        db_result = TaskResult(
            task_id=add.request.id,
            status="성공!!!!",
            result=str(result_value)
        )
        session.add(db_result)
        session.commit()
        return result_value

    except Exception as e:
        print(f"[add 오류] {e}")
        if session and session.is_active:
            session.rollback()
        raise e

    finally:
        if session:
            session.close()
        try:
            SessionLocal.remove()
        except Exception:
            pass



#   실전 Caspian 탄소 스케줄러 Task


@celery_app.task
def run_real_carbon_scheduler_task():
    """Caspian 기반 클러스터 스케줄러 실행"""
    return run_real_carbon_scheduler()



#   클러스터 자동 초기화 Task (한국/일본)

@celery_app.task
def auto_initialize_clusters():
    """
    ClusterStatus 테이블에
    기본 클러스터 2개(KR/JP)를 자동 생성하는 Task
    """
    session = None
    try:
        session = SessionLocal()
        clusters = [
            {"cluster_name": "cluster_kr", "region": "KR"},
            {"cluster_name": "cluster_jp", "region": "JP"},
        ]

        for c in clusters:
            exists = session.query(ClusterStatus).filter_by(cluster_name=c["cluster_name"]).first()
            if not exists:
                new_data = ClusterStatus(
                    cluster_name=c["cluster_name"],
                    region=c["region"],
                    cpu_usage=round(random.uniform(20, 90), 2),
                    memory_usage=round(random.uniform(30, 95), 2),
                    carbon_intensity=round(random.uniform(50, 400), 2),
                    last_updated=datetime.utcnow(),
                )
                session.add(new_data)

        session.commit()
        print("[auto_initialize_clusters] 한국/일본 클러스터 등록 완료")

    except Exception as e:
        print(f"[auto_initialize_clusters 오류] {e}")
        if session and session.is_active:
            session.rollback()

    finally:
        if session:
            session.close()
        try:
            SessionLocal.remove()
        except Exception:
            pass


#   Celery Beat: WattTime 실시간 탄소데이터 갱신 (10초마다)

@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """Celery Beat 주기적 작업 등록"""
    sender.add_periodic_task(10.0, update_cluster_carbon_intensity.s(), name='update_wattime_data')
    print("[Celery Beat] WattTime 실시간 탄소데이터 10초 주기 업데이트 등록 완료")
