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

# src/db/__init__.py의 역할

FastAPI와 Celery가 같은 DB 세션을 공유할 수 있도록 연결 세팅을 관리함.

###

ECR준비

나중에 fastapi-deployment.yaml에 이미지주소에 쓸거
266735841992.dkr.ecr.ap-northeast-2.amazonaws.com/fastapi-kuber

aws ecr 로그인 window상 도커 데몬에러날때

docker login -u AWS -p $(aws ecr get-login-password --region ap-northeast-2) https://266735841992.dkr.ecr.ap-northeast-2.amazonaws.com


푸쉬

docker push 266735841992.dkr.ecr.ap-northeast-2.amazonaws.com/fastapi-kuber:latest

ecr 위치

https://ap-northeast-2.console.aws.amazon.com/ecr/private-registry/repositories?region=ap-northeast-2


eks 연결후 이제 yaml파일들 배포

1
kubectl apply -f k8s/redis-deployment.yaml
kubectl apply -f k8s/postgres-statefulset.yaml

2
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml

--> 시크릿 야말 인코딩
postgre사용자명 : a2p1bmUwOTIy
postgre비번 : ZGxydWRhbHN3bnMy
db이름 : a3ViZXJfZGI=


--> 시크릿 wattime 인코딩
kjune922
dlrudalswns2!
3
kubectl apply -f k8s/services.yaml

4
kubectl apply -f k8s/fastapi-deployment.yaml
kubectl apply -f k8s/celery-worker-deployment.yaml
kubectl apply -f k8s/celery-beat-deployment.yaml


####

Arn : arn:aws:iam::266735841992:policy/AmazonEBSCSIDriverPolicy

###

네트워크 레이턴시는 현재 한국과 일본 왕복 rtt가 35~ 45정도니까
40.0ms은 그냥 임시 평균값
(AWS 서울–도쿄 간 실제 평균 왕복 RTT가 약 35~45ms 정도라 현실적으로도 타당하게넣음)

현재 캐스피안 알고리즘 공식이
score = α·CPU + β·Memory + γ·Carbon + δ·Latency

내가 프로젝트내에 설정한 값
alpha = 0.3
beta  = 0.2
gamma = 0.4
delta = 0.1

= 0.3*(59.11) + 0.2*(86.69) + 0.4*(120.9) + 0.1*(40.0)
= 87.431 이 나옴


####### 마지막 eks끄고 키고 대쉬보드 보는것까지 템플릿

클라우드 쿠버 동기화서버 끄고키는법

# 1. 현재 클러스터 상태 확인
aws eks list-clusters --region ap-northeast-2
aws eks describe-cluster --name kuberzo-cluster --region ap-northeast-2

# 2. 노드 그룹 이름 확인
aws eks list-nodegroups --cluster-name kuberzo-cluster --region ap-northeast-2

# 3. 노드 그룹 내 EC2 인스턴스 목록 확인
aws ec2 describe-instances --filters "Name=tag:eks:cluster-name,Values=kuberzo-cluster" --query "Reservations[*].Instances[*].[InstanceId,State.Name]" --region ap-northeast-2


>>>

aws ec2 describe-instances --filters "Name=tag:eks:cluster-name,Values=kuberzo-cluster" --query "Reservations[*].Instances[*].[InstanceId,State.Name]" --region ap-northeast-2
[
    [
        [
            "i-0f154b489b0842416",
            "running"
        ]
    ],
    [
        [
            "i-0314c867da6cf0a1b",
            "running"
        ]
    ],
    [
        [

이렇게 뜨면 저거 인스턴스 이름따서 이렇게 그때그떄다름

aws ec2 stop-instances --instance-ids i-0f154b489b0842416 i-0314c867da6cf0a1b --region ap-northeast-2

aws ec2 stop-instances --instance-ids i-0f154b489b0842416 i-06f6ebebc371f3234 --region ap-northeast-2

이렇게 끄고

만약 stopping 뜨고있으면
상태확인계속 ㄱ

aws ec2 describe-instances --filters "Name=tag:eks:cluster-name,Values=kuberzo-cluster" --query "Reservations[*].Instances[*].[InstanceId,State.Name]" --region ap-northeast-2

다시키자

aws ec2 start-instances --instance-ids i-0f154b489b0842416 i-0314c867da6cf0a1b --region ap-northeast-2


키는거확인 (꺼질떄랑 같음)

aws ec2 describe-instances --filters "Name=tag:eks:cluster-name,Values=kuberzo-cluster" --query "Reservations[*].Instances[*].[InstanceId,State.Name]" --region ap-northeast-2


## 노드연결확인

kubectl get nodes -n default


## 주요 pod애들 확인

kubectl get pods -n default

혹시 에러뜨면

kubectl rollout restart deployment fastapi-kuber -n default
kubectl rollout restart deployment celery-worker -n default
kubectl rollout restart deployment celery-beat -n default




