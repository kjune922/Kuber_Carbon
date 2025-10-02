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