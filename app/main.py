from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import settings
from app.api.v1 import chat, orchestration, validation, skills, mock

def create_app() -> FastAPI:
    """创建 FastAPI 应用"""
    
    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        version="0.1.0"
    )
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 注册路由
    app.include_router(chat.router, prefix=f"{settings.api_prefix}/chat", tags=["chat"])
    app.include_router(orchestration.router, prefix=f"{settings.api_prefix}/orchestration", tags=["orchestration"])
    app.include_router(validation.router, prefix=f"{settings.api_prefix}/validation", tags=["validation"])
    app.include_router(skills.router, prefix=f"{settings.api_prefix}/skills", tags=["skills"])
    app.include_router(mock.router, prefix=f"{settings.api_prefix}/mock", tags=["mock"])
    
    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}
    
    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
