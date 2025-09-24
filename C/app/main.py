import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from contextlib import asynccontextmanager
<<<<<<< HEAD

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, jwxt, user
=======
import os
import asyncio
from app.api import auth
>>>>>>> 007d238 (新分支，组合了前后端+进行了数据库具体配置，就此而言，什么也没干。)
from app.core.config import config
from app.core.logger import logger
from app.core.sql import close_db, load_db
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware  # 解决跨域问题


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))# 获取项目根目录路径
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

logger.info(f"项目根目录: {BASE_DIR}")
logger.info(f"前端目录路径: {FRONTEND_DIR}")
logger.info(f"前端目录是否存在: {os.path.exists(FRONTEND_DIR)}")

if os.path.exists(FRONTEND_DIR):
    try:
        contents = os.listdir(FRONTEND_DIR)
        logger.info(f"前端目录内容: {contents}")
        # 检查是否有HTML文件
        html_files = [f for f in contents if f.endswith('.html')]
        logger.info(f"HTML文件: {html_files}")
    except Exception as e:
        logger.error(f"读取前端目录失败: {e}")


# 定义生命周期事件处理器
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("初始化 Server...")
    await load_db()
    yield
    logger.info("正在退出...")
    await close_db()
    logger.info("已安全退出")

app = FastAPI(
    title=config.title,
    version=config.version,
    lifespan=lifespan
)

<<<<<<< HEAD
app = FastAPI(title=config.title, version=config.version, lifespan=lifespan)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 允许的前端源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有请求头
)

# 注册 API 路由
=======
>>>>>>> 007d238 (新分支，组合了前后端+进行了数据库具体配置，就此而言，什么也没干。)
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(user.router, prefix="/api/user", tags=["user"])
app.include_router(jwxt.router, prefix="/api/jwxt", tags=["jwxt"])

# 配置跨域：允许前端Vue项目的请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:5175"],  # 添加所有可能的开发端口
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有请求头
)

# 挂载前端静态文件
if os.path.exists(FRONTEND_DIR):
    app.mount("/frontend", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
else:
    logger.warning("前端目录不存在，无法挂载静态文件")


@app.get("/")
async def root():
    # 检查是否存在Vue构建后的index.html文件
    vue_dist_dir = os.path.join(FRONTEND_DIR, "金融就业服务系统", "finance-employment", "dist")
    index_file = os.path.join(vue_dist_dir, "index.html")
    
    if os.path.exists(index_file):
        return FileResponse(index_file)
    else:
        # 先检查原有的login.html文件
        login_file = os.path.join(FRONTEND_DIR, "login.html")
        if os.path.exists(login_file):
            return FileResponse(login_file)
        else:
            # 列出前端目录的所有文件
            frontend_files = []
            if os.path.exists(FRONTEND_DIR):
                # 使用线程池运行同步的文件操作
                frontend_files = await asyncio.to_thread(os.listdir, FRONTEND_DIR)

            return JSONResponse({
                "message": "前端文件未找到",
                "frontend_directory": FRONTEND_DIR,
                "vue_dist_directory": vue_dist_dir,
                "frontend_files": frontend_files,
                "hint": "请确保已构建Vue应用或login.html文件在frontend目录中"
            })




# 捕获所有未匹配的路由并返回index.html
@app.get("/{path:path}", include_in_schema=False)
async def catch_all(path: str):
    # 检查是否存在Vue构建后的应用
    vue_dist_dir = os.path.join(FRONTEND_DIR, "金融就业服务系统", "finance-employment", "dist")
    index_file = os.path.join(vue_dist_dir, "index.html")
    
    if os.path.exists(index_file):
        # 如果存在Vue构建后的应用，返回index.html，由Vue Router处理路由
        return FileResponse(index_file)
    else:
        # 如果Vue应用不存在，返回404
        raise HTTPException(status_code=404, detail="页面未找到")



if __name__ == "__main__":
    logger.info(f"服务器地址: http://{config.host}:{config.port}")
    logger.info(f"FastAPI 文档地址: http://{config.host}:{config.port}/docs")
<<<<<<< HEAD
    logger.info(f"OpenAPI JSON 地址: http://{config.host}:{config.port}/openapi.json")
    uvicorn.run(app, host=config.host, port=config.port)
=======
    uvicorn.run("app.main:app", host=config.host, port=config.port, reload=True)

>>>>>>> 007d238 (新分支，组合了前后端+进行了数据库具体配置，就此而言，什么也没干。)
