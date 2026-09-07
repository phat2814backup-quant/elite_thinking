# -*- coding: utf-8 -*-
"""
Bộ chuyển đổi tài liệu đa định dạng sang Markdown (Document to Markdown Converter).
Sử dụng AnyDoc (firecrawl-anydoc) làm lõi chuyển đổi siêu tốc (<5ms, viết bằng Rust).
Có cơ chế fallback sang pypdf / text reader để đảm bảo hoạt động trên mọi môi trường.
Ngay sau khi xử lý xong, file tạm nhị phân được xóa ngay lập tức để tiết kiệm dung lượng.
"""
import os
import tempfile
from pathlib import Path
from typing import Optional, Union, BinaryIO

def convert_document_to_markdown(
    file_source: Union[str, Path, BinaryIO],
    original_filename: str = ""
) -> str:
    """
    Chuyển đổi file bất kỳ (PDF, DOCX, PPTX, XLSX, TXT, MD, CSV, EPUB, RTF...) sang Markdown.
    
    Args:
        file_source: Đường dẫn file cục bộ HOẶC file object (UploadedFile từ Streamlit).
        original_filename: Tên file gốc kèm đuôi mở rộng (đặc biệt quan trọng khi truyền file object).
        
    Returns:
        Nội dung Markdown dạng chuỗi (UTF-8).
    """
    temp_path: Optional[str] = None
    input_path: str = ""
    ext: str = ""

    try:
        # Trường hợp 1: file_source là đường dẫn
        if isinstance(file_source, (str, Path)):
            input_path = str(file_source)
            ext = Path(input_path).suffix.lower()
        # Trường hợp 2: file_source là file stream / UploadedFile từ Streamlit
        else:
            if not original_filename and hasattr(file_source, "name"):
                original_filename = file_source.name
            
            ext = Path(original_filename).suffix.lower() if original_filename else ".bin"
            
            # Tạo file tạm thời có đúng phần mở rộng để AnyDoc nhận diện đúng định dạng
            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tf:
                temp_path = tf.name
                if hasattr(file_source, "getvalue"):
                    tf.write(file_source.getvalue())
                elif hasattr(file_source, "read"):
                    file_source.seek(0)
                    tf.write(file_source.read())
            input_path = temp_path

        # Ưu tiên 1: Thử nghiệm AnyDoc (Rust engine - siêu tốc, chất lượng cao)
        try:
            import anydoc
            md_text = anydoc.to_markdown(input_path)
            if md_text and len(md_text.strip()) > 0:
                return md_text.strip()
        except Exception as anydoc_err:
            # Ghi nhận log fallback nếu cần
            pass

        # Ưu tiên 2: Fallback cho PDF bằng pypdf
        if ext == ".pdf":
            try:
                import pypdf
                reader = pypdf.PdfReader(input_path)
                pages_text = []
                for i, page in enumerate(reader.pages):
                    pt = page.extract_text()
                    if pt:
                        pages_text.append(f"<!-- Page {i+1} -->\n{pt.strip()}")
                if pages_text:
                    return "\n\n---\n\n".join(pages_text)
            except Exception:
                pass

        # Ưu tiên 3: Fallback đọc văn bản thông thường (TXT, MD, CSV, JSON...)
        try:
            with open(input_path, "r", encoding="utf-8", errors="replace") as f:
                return f.read()
        except Exception as read_err:
            raise RuntimeError(f"Không thể trích xuất nội dung từ tệp: {read_err}")

    finally:
        # Luôn luôn dọn dẹp file tạm nhị phân để không chiếm dụng bộ nhớ/ổ đĩa
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except OSError:
                pass
