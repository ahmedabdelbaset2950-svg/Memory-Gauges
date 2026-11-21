import os
import uuid

from pathlib import Path

from werkzeug.utils import secure_filename


MAX_UPLOAD_BYTES = 10 * 1024 * 1024

IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
DOCUMENT_EXTENSIONS = {"pdf", "jpg", "jpeg", "png", "gif", "webp", "xlsx", "xls", "csv", "doc", "docx", "txt"}
EXCEL_EXTENSIONS = {"xlsx", "xls"}


def validate_and_save_upload(file, upload_dir, allowed_extensions, max_bytes=MAX_UPLOAD_BYTES):
    if not file or not getattr(file, "filename", ""):
        raise ValueError("No file was provided.")

    original_name = secure_filename(file.filename)
    if not original_name or "." not in original_name:
        raise ValueError("The uploaded file name is invalid.")

    extension = original_name.rsplit(".", 1)[1].lower()
    if extension not in allowed_extensions:
        raise ValueError("This file type is not allowed.")

    file.stream.seek(0, os.SEEK_END)
    size = file.stream.tell()
    file.stream.seek(0)
    if size <= 0:
        raise ValueError("The uploaded file is empty.")
    if size > max_bytes:
        raise ValueError("The uploaded file is too large.")

    header = file.stream.read(16)
    file.stream.seek(0)
    if extension in IMAGE_EXTENSIONS:
        is_jpeg = header.startswith(b"\xff\xd8\xff")
        is_png = header.startswith(b"\x89PNG\r\n\x1a\n")
        is_webp = header.startswith(b"RIFF") and len(header) >= 12 and header[8:12] == b"WEBP"
        if not (is_jpeg or is_png or is_webp):
            raise ValueError("The image content is invalid.")
    elif extension in EXCEL_EXTENSIONS:
        if not (header.startswith(b"PK") or header.startswith(b"\xd0\xcf\x11\xe0")):
            raise ValueError("The Excel file content is invalid.")
    elif extension == "pdf":
        if not header.startswith(b"%PDF-"):
            raise ValueError("The PDF file content is invalid.")

    target_dir = Path(upload_dir).resolve()
    target_dir.mkdir(parents=True, exist_ok=True)
    stored_name = f"{uuid.uuid4().hex}_{original_name}"
    target = (target_dir / stored_name).resolve()
    if target.parent != target_dir:
        raise ValueError("Unsafe upload path.")

    file.save(str(target))
    return stored_name, original_name, extension
