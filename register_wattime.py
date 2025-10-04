import requests

register_url = "https://api.watttime.org/register"

payload = {
    "username": "kjune922",             # 네가 사용할 아이디
    "password": "dlrudalswns2!",        # 비밀번호 (8자 이상, 특수문자 포함)
    "email": "kjune922@naver.com",     # 실제 이메일 주소
    "org": "Dong-A University Project" # 선택사항 (조직명)
}

resp = requests.post(register_url, json=payload)
print(resp.status_code)
print(resp.text)


