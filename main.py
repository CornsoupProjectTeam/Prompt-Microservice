from fastapi import FastAPI
from app.routers import chathistory_router, perschat_router

app = FastAPI(title="성격 분석 챗봇 API")

app.include_router(chathistory_router)
app.include_router(perschat_router)
