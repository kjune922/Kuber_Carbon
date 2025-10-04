import requests

r = requests.get(
    "https://api.watttime.org/v2/login",
    auth=("kjune922", "dlrudalswns2!")  # ← 방금 만든 계정 정보 그대로
)
print(r.status_code)
print(r.json())