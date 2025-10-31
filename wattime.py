import requests
from requests.auth import HTTPBasicAuth

# WattTime 계정 정보
username = "kjune922"
password = "dlrudalswns2!"

# 로그인 요청
login_url = "https://api.watttime.org/login"
response = requests.get(login_url, auth=HTTPBasicAuth(username, password))

# 결과 확인
print("응답 코드:", response.status_code)
print("응답 내용:", response.json())
