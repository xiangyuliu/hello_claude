import uuid
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

app = FastAPI(title="Image & Prompt Service")

STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
async def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.post("/upload")
async def upload(
    image: UploadFile = File(...),
    prompt: str = Form(...),
):
    """接收一张图片和一段文字提示，保存图片并返回元数据供后续处理。"""

    # 校验文件扩展名
    ext = Path(image.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型 '{ext}'，允许: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # 读取并校验大小
    content = await image.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="文件大小不能超过 10 MB")

    # 生成唯一文件名并保存
    file_id = uuid.uuid4().hex
    save_path = UPLOAD_DIR / f"{file_id}{ext}"
    save_path.write_bytes(content)

    return JSONResponse(
        {
            "file_id": file_id,
            "filename": image.filename,
            "content_type": image.content_type,
            "size": len(content),
            "path": str(save_path),
            "prompt": prompt,
        }
    )
