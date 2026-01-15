"""
OpenCloudPrint - 文档转换任务 (修复版)
"""
import os
import subprocess
import shutil
from pathlib import Path
from celery import Task
from app.tasks.celery_app import celery_app
from app.core.config import settings

class ConvertDocumentTask(Task):
    _db = None
    @property
    def db(self):
        if self._db is None:
            from app.core.database import SessionLocal
            self._db = SessionLocal()
        return self._db

@celery_app.task(bind=True, base=ConvertDocumentTask, name="app.tasks.conversion.convert_document")
def convert_document(self, job_id: str, file_path: str, file_type: str) -> dict:
    try:
        # 1. 准备路径
        input_path = Path(file_path)
        output_dir = Path(settings.CONVERTED_DIR)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 预期输出文件路径 (job_id.pdf)
        final_output_path = output_dir / f"{job_id}.pdf"

        # 如果已经是 PDF，直接复制过去
        if file_type.lower() == "pdf":
            shutil.copy2(input_path, final_output_path)
            return {"success": True, "converted_path": str(final_output_path), "error": None}

        # 2. 调用 LibreOffice 转换
        if file_type.lower() in ["docx", "doc", "xlsx", "xls", "pptx", "ppt"]:
            # LibreOffice 会在 output_dir 生成与原文件名同名的 pdf
            success = _convert_with_libreoffice(input_path, output_dir)
            
            if success:
                # 找到 LibreOffice 生成的那个文件 (原文件名.pdf)
                generated_filename = input_path.stem + ".pdf"
                generated_file_path = output_dir / generated_filename
                
                # 【关键修复】将生成的文件重命名为 {job_id}.pdf
                if generated_file_path.exists():
                    # 如果目标文件已存在先删除，防止报错
                    if final_output_path.exists():
                        final_output_path.unlink()
                    generated_file_path.rename(final_output_path)
                    return {"success": True, "converted_path": str(final_output_path), "error": None}
                else:
                    return {"success": False, "converted_path": None, "error": "Converted file not found"}
            else:
                return {"success": False, "converted_path": None, "error": "LibreOffice conversion failed"}

        # 图片转换逻辑 (略，保持原样或按需补充)
        return {"success": False, "converted_path": None, "error": "Unsupported file type"}

    except Exception as e:
        return {"success": False, "converted_path": None, "error": str(e)}

def _convert_with_libreoffice(input_path: Path, output_dir: Path) -> bool:
    try:
        # 使用 --outdir 指定输出目录
        cmd = [
            "soffice", "--headless", "--convert-to", "pdf",
            "--outdir", str(output_dir), str(input_path)
        ]
        # 设置 HOME 目录防止权限报错
        env = os.environ.copy()
        env['HOME'] = '/tmp'
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, env=env)
        if result.returncode != 0:
            print(f"LibreOffice Error: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"Conversion Exception: {e}")
        return False