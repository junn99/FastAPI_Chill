from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import models
from database import engine
from routers import brands, projects, manufacturers

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Brand Manager API")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발환경에서는 모든 origin 허용, 프로덕션에서는 제한 필요
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(brands.router)
app.include_router(projects.router)
app.include_router(manufacturers.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Brand Manager API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)