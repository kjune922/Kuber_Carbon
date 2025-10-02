from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
  return {
    "message" : "이경준의 쿠버네티스프로젝트"
  }