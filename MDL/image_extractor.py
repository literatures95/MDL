"""MDL 图片提取模块 - 从文档中提取和处理图片"""

import os
import re
import base64
import hashlib
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass
class ImageInfo:
    """图片信息"""
    original_path: str
    local_path: Optional[str] = None
    alt_text: str = ""
    width: Optional[int] = None
    height: Optional[int] = None
    format: Optional[str] = None
    size_bytes: int = 0
    hash: str = ""


class ImageExtractor:
    """Markdown 图片提取器"""

    IMAGE_PATTERN = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")

    @staticmethod
    def extract_images(markdown: str) -> List[Dict[str, str]]:
        """从 Markdown 中提取图片信息"""
        images = []
        for match in ImageExtractor.IMAGE_PATTERN.finditer(markdown):
            alt_text = match.group(1)
            image_path = match.group(2)
            images.append({
                "alt": alt_text,
                "path": image_path,
                "full_match": match.group(0),
            })
        return images

    @staticmethod
    def extract_and_save(
        markdown: str,
        output_dir: str,
        base_url: Optional[str] = None,
        download_remote: bool = False,
    ) -> Tuple[str, List[ImageInfo]]:
        """提取并保存图片，返回更新后的 Markdown"""
        os.makedirs(output_dir, exist_ok=True)
        images = ImageExtractor.extract_images(markdown)
        saved_images = []
        for img in images:
            original_path = img["path"]
            local_path = ImageExtractor._save_image(
                original_path,
                output_dir,
                base_url,
                download_remote,
            )
            if local_path:
                saved_images.append(ImageInfo(
                    original_path=original_path,
                    local_path=local_path,
                    alt_text=img["alt"],
                ))
                markdown = markdown.replace(img["full_match"], f"![{img['alt']}]({local_path})")
        return markdown, saved_images

    @staticmethod
    def _save_image(
        source_path: str,
        output_dir: str,
        base_url: Optional[str],
        download_remote: bool,
    ) -> Optional[str]:
        """保存单个图片"""
        if source_path.startswith("data:"):
            return ImageExtractor._save_base64_image(source_path, output_dir)
        parsed = urlparse(source_path)
        if parsed.scheme in ("http", "https"):
            if download_remote:
                return ImageExtractor._download_image(source_path, output_dir)
            return None
        if os.path.exists(source_path):
            return ImageExtractor._copy_local_image(source_path, output_dir)
        if base_url:
            full_path = os.path.join(base_url, source_path)
            if os.path.exists(full_path):
                return ImageExtractor._copy_local_image(full_path, output_dir)
        return None

    @staticmethod
    def _save_base64_image(data_url: str, output_dir: str) -> Optional[str]:
        """保存 Base64 编码的图片"""
        try:
            match = re.match(r"data:image/([^;]+);base64,(.+)", data_url)
            if not match:
                return None
            img_format = match.group(1)
            img_data = base64.b64decode(match.group(2))
            img_hash = hashlib.md5(img_data).hexdigest()[:8]
            filename = f"image_{img_hash}.{img_format}"
            filepath = os.path.join(output_dir, filename)
            with open(filepath, "wb") as f:
                f.write(img_data)
            return filepath
        except Exception:
            return None

    @staticmethod
    def _download_image(url: str, output_dir: str) -> Optional[str]:
        """下载远程图片"""
        try:
            import urllib.request
            img_hash = hashlib.md5(url.encode()).hexdigest()[:8]
            parsed = urlparse(url)
            ext = os.path.splitext(parsed.path)[1] or ".png"
            filename = f"image_{img_hash}{ext}"
            filepath = os.path.join(output_dir, filename)
            urllib.request.urlretrieve(url, filepath)
            return filepath
        except Exception:
            return None

    @staticmethod
    def _copy_local_image(source: str, output_dir: str) -> Optional[str]:
        """复制本地图片"""
        try:
            import shutil
            filename = os.path.basename(source)
            dest = os.path.join(output_dir, filename)
            if source != dest:
                shutil.copy2(source, dest)
            return dest
        except Exception:
            return None


class ImageProcessor:
    """图片处理器"""

    @staticmethod
    def get_image_info(image_path: str) -> Optional[ImageInfo]:
        """获取图片详细信息"""
        if not os.path.exists(image_path):
            return None
        info = ImageInfo(original_path=image_path, local_path=image_path)
        info.size_bytes = os.path.getsize(image_path)
        with open(image_path, "rb") as f:
            info.hash = hashlib.md5(f.read()).hexdigest()
        try:
            from PIL import Image
            with Image.open(image_path) as img:
                info.width, info.height = img.size
                info.format = img.format.lower() if img.format else None
        except ImportError:
            pass
        except Exception:
            pass
        return info

    @staticmethod
    def resize_image(
        input_path: str,
        output_path: str,
        max_width: int = 800,
        max_height: int = 600,
    ) -> bool:
        """调整图片大小"""
        try:
            from PIL import Image
            with Image.open(input_path) as img:
                img.thumbnail((max_width, max_height), Image.LANCZOS)
                img.save(output_path)
                return True
        except ImportError:
            return False
        except Exception:
            return False

    @staticmethod
    def convert_format(
        input_path: str,
        output_path: str,
        target_format: str = "png",
    ) -> bool:
        """转换图片格式"""
        try:
            from PIL import Image
            with Image.open(input_path) as img:
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                img.save(output_path, format=target_format.upper())
                return True
        except ImportError:
            return False
        except Exception:
            return False


def extract_images_from_markdown(
    markdown: str,
    output_dir: str = "images",
    download_remote: bool = False,
) -> Tuple[str, List[ImageInfo]]:
    """从 Markdown 提取图片的便捷函数"""
    return ImageExtractor.extract_and_save(
        markdown,
        output_dir,
        download_remote=download_remote,
    )


def extract_images_from_document(
    file_path: str,
    output_dir: str,
) -> List[Dict[str, str]]:
    """从文档提取图片"""
    from formats import convert_to_markdown
    md = convert_to_markdown(file_path)
    _, images = extract_images_from_markdown(md, output_dir)
    return [
        {
            "original": img.original_path,
            "local": img.local_path,
            "alt": img.alt_text,
        }
        for img in images
    ]
