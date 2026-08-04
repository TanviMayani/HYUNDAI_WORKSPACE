from app.models import Base
import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from app.init_db import init_db
from app.jobs.jobs import JobRouter
from fastapi.openapi.utils import get_openapi
from app.api_key.api_key import API_KEY_ROUTER
from app.auth.login.user_login import LoginRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from app.config import SessionLocal, create_db_engine
from app.auth.sign_up.user_sign_up import SignUpRouter
from app.auth.profile.user_profile import ProfileRouter
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

load_dotenv()

request_limit = os.getenv("REQUEST_LIMIT", "10")
limiter = Limiter(key_func=get_remote_address, default_limits=[f"{request_limit}/second"])

class HIIBApp(FastAPI):
    def __init__(self):
        super().__init__(
            debug=True,
            docs_url="/v1/hiib/docs",
            redoc_url="/v1/hiib/redoc",
            openapi_url="/v1/hiib/openapi.json",
            contact={
                "name": "HIIB",
                "url": "https://www.binarysemantics.com/contact-us/",
                "email": "support@binarysemantics.com",
            },
        )

        self.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,                                                                                                                                                                                                                                                       
            allow_methods=["*"],
            allow_headers=["*"],
        )
        self.limiter = limiter

        self.state.limiter = limiter
        

        self.add_middleware(SlowAPIMiddleware)
        
        engine = create_db_engine()
        Base.metadata.create_all(bind=engine)


        SessionLocal.configure(bind=engine)
        init_db()

        self.login_router = LoginRouter()
        self.sign_up_router = SignUpRouter()
        self.api_key_router = API_KEY_ROUTER()
        self.job_router = JobRouter()
        self.profile_router = ProfileRouter()
        
        uploads_dir = os.path.join(os.getcwd(), "uploads")
        os.makedirs(uploads_dir, exist_ok=True)
        self.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")
        self.mount("/v1/hiib/uploads", StaticFiles(directory=uploads_dir), name="v1_uploads")

        self.api_key_router.add_routes()
      
        self.include_router(self.login_router.router)
        self.include_router(self.sign_up_router.router)
        self.include_router(self.job_router.router)
        self.include_router(self.api_key_router.router)
        self.include_router(self.profile_router.router)

    
    async def swagger_ui_html(self):
        return get_swagger_ui_html(
            title="HIIB - Swagger UI",
            swagger_js_url="/static/swagger-ui-bundle.js",
            swagger_css_url="/static/swagger-ui.css",
            openapi_url="v1/hiib/openapi.json",
        )

    async def get_open_api_endpoint(self):
        return get_openapi(
            title="HIIB API",
            description="Insurance ML API",
            version="1.0.0",
            routes=self.routes,
        )


def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content=[{
            "type": "Rate limit",
            "msg": "Rate limit exceeded.",
            "ctx": {"reason": "Too many requests. Please try again later."}
        }]
    )
            
app = HIIBApp()
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)

@app.get("/v1/hiib")
async def health_check():
    """Endpoint for health check."""
    return {"message": "HIIB server is running...."}

