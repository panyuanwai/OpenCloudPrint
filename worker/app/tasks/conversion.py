"""
OpenCloudPrint - 文档转换任务
使用 LibreOffice 将各种格式转换为 PDF
"""
import os
import subprocess
import shutil
from pathlib import Path
from typing import Optional
from celery import Task

from app.tasks.celery_app import celery_app
from app.core.config import settings


class ConvertDocumentTask(Task):
    """文档转换任务基类"""
    _db = None

    @property
    def db(self):
        """获取数据库连接"""
        if self._db is None:
            from app.core.database import SessionLocal
            self._db = SessionLocal()
        return self._db


@celery_app.task(bind=True, base=ConvertDocumentTask, name="app.tasks.conversion.convert_document")
def convert_document(self, job_id: str, file_path: str, file_type: str) -> dict:
    """
    将文档转换为 PDF

    Args:
        job_id: 打印任务 ID
        file_path: 原始文件路径
        file_type: 文件类型 (pdf/docx/xlsx/pptx/jpg/png)

    Returns:
        dict: {
            "success": bool,
            "converted_path": str | None,
            "error": str | None
        }
    """
    try:
        # 如果已经是 PDF，直接返回
        if file_type.lower() == "pdf":
            return {
                "success": True,
                "converted_path": file_path,
                "error": None
            }

        # 构建输出路径
        input_path = Path(file_path)
        output_dir = Path(settings.CONVERTED_DIR)
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{job_id}.pdf"

        # 根据文件类型选择转换方式
        if file_type.lower() in ["docx", "doc", "xlsx", "xls", "pptx", "ppt", "odt", "ods", "odp"]:
            # 使用 LibreOffice 转换 Office 文档
            success = _convert_with_libreoffice(input_path, output_dir)
        elif file_type.lower() in ["jpg", "jpeg", "png", "gif", "bmp"]:
            # 使用 ImageMagick 或其他工具转换图片
            success = _convert_image_to_pdf(input_path, output_path)
        else:
            return {
                "success": False,
                "converted_path": None,
                "error": f"Unsupported file type: {file_type}"
            }

        if success:
            return {
                "success": True,
                "converted_path": str(output_path),
                "error": None
            }
        else:
            return {
                "success": False,
                "converted_path": None,
                "error": "Conversion failed"
            }

    except Exception as e:
        return {
            "success": False,
            "converted_path": None,
            "error": str(e)
        }


def _convert_with_libreoffice(input_path: Path, output_dir: Path) -> bool:
    """
    使用 LibreOffice 转换文档

    LibreOffice 无头模式转换命令:
    soffice --headless --convert-to pdf --outdir /output /input/file.docx
    """
    try:
        cmd = [
            "soffice",
            "--headless",
            "--convert-to", "pdf",
            "--outdir", str(output_dir),
            str(input_path)
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60  # 60 秒超时
        )

        return result.returncode == 0

    except subprocess.TimeoutExpired:
        return False
    except Exception:
        return False


def _convert_image_to_pdf(input_path: Path, output_path: Path) -> bool:
    """
    将图片转换为 PDF

    可以使用 PIL/Pillow 或 img2pdf
    """
    try:
        from PIL import Image

        image = Image.open(input_path)

        # 如果是 RGBA 模式，转换为 RGB
        if image.mode == "RGBA":
            image = image.convert("RGB")

        # 保存为 PDF
        image.save(str(output_path), "PDF")
        return True

    except Exception:
        return False
