"""多模态解析包（OCR / 表格 / 视觉模型，可选）"""
from .parser import ocr_image, describe_image_with_vlm, extract_tables_pdf

__all__ = ["ocr_image", "describe_image_with_vlm", "extract_tables_pdf"]
