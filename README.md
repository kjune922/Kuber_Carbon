# Kuber_Carbon

-------------

2025 - 10 - 02 

프로젝트하면서 몰랐던거 정리


FastAPI는 앱의 생명주기(lifecycle)에 맞춰 이벤트 훅을 지원합니다:

@app.on_event("startup")
def startup_event():
    print("서버 시작할 때 실행")

@app.on_event("shutdown")
def shutdown_event():
    print("서버 종료할 때 실행")


"startup" 훅 → 서버가 켜질 때 딱 한 번 실행

"shutdown" 훅 → 서버가 종료될 때 딱 한 번 실행

# 2025-10-04

cluster = db.query(ClusterStatus).filter(ClusterStatus.cluster_name == data.cluster_name).first()

db.query(Clusterstatus) -> 클러스터상태 테이블전체에서 검색을 시작하고
.fliter(Clusterstatus.cluster_name == data.cluster_name) 입력받은 cluster_name과 같은이름의 레코드만 찾아보겠다
.first() - > 조건에 맞는 행이 여러개여도 일단 첫번째 한개만 반환 ㄱㄱ

-----> 한마디로 지금 들어온 클러스터 이름이 DB에 이미 존재하는지 체크해라

그리고 그밑에 if else문의 의미는
만약 이미 존재하는 클러스터면 기존 데이터들을 업데이트시키고 새로들어온거 맞게,

아니라면 새로 DB에 저장하겠다는 의미

# 2025-10-04 -2 

클러스터 상태 자동 업데이트 백그라운드 테스크 Celery로 등록