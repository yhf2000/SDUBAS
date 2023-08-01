import uvicorn
from fastapi import FastAPI, Depends
from starlette.middleware.cors import CORSMiddleware

from utils.auth_login import auth_login
from utils.response import standard_response
from controller import files, projects, permissions, resources, users

app = FastAPI()
app.include_router(files.files_router, prefix="/files")
app.include_router(permissions.permissions_router, prefix="/permissions")
app.include_router(projects.projects_router, prefix="/projects")
app.include_router(resources.resources_router, prefix="/resources")
app.include_router(users.files_router, prefix="/users")

origins = [
    "*",
]

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 允许的源列表
    allow_credentials=True,  # 允许返回 cookies
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有 HTTP 头
)


@app.get("/")
@standard_response
async def root(user=Depends(auth_login)):
    return {"message": "Hello World"}


@app.get("/hello/{name}")
@standard_response
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


def main():
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    main()
