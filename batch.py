"""MDL 批量处理模块 - 批量转换和处理多个文档"""

import os
import glob
import json
import multiprocessing
from typing import List, Dict, Any, Callable, Optional
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from datetime import datetime


@dataclass
class BatchConfig:
    """批量处理配置"""
    max_workers: int = 4
    use_multiprocessing: bool = False
    num_gpus: int = 0
    workers_per_gpu: int = 1
    chunk_size: int = 10
    retry_failed: bool = True
    max_retries: int = 3
    progress_callback: Optional[Callable[[int, int], None]] = None


@dataclass
class BatchResult:
    """批量处理结果"""
    success: bool
    file_path: str
    output_path: Optional[str] = None
    error: Optional[str] = None
    processing_time: float = 0.0
    retries: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BatchReport:
    """批量处理报告"""
    total_files: int = 0
    successful: int = 0
    failed: int = 0
    total_time: float = 0.0
    throughput: float = 0.0
    results: List[BatchResult] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_files": self.total_files,
            "successful": self.successful,
            "failed": self.failed,
            "total_time": self.total_time,
            "throughput": f"{self.throughput:.2f} files/sec",
            "success_rate": f"{(self.successful / self.total_files * 100):.1f}%" if self.total_files > 0 else "0%",
            "results": [
                {
                    "file": r.file_path,
                    "success": r.success,
                    "output": r.output_path,
                    "error": r.error,
                    "time": r.processing_time,
                    "retries": r.retries,
                }
                for r in self.results
            ],
        }

    def print_summary(self):
        print("\n" + "=" * 50)
        print("批量处理报告")
        print("=" * 50)
        print(f"总文件数: {self.total_files}")
        print(f"成功: {self.successful}")
        print(f"失败: {self.failed}")
        print(f"成功率: {(self.successful / self.total_files * 100):.1f}%" if self.total_files > 0 else "0%")
        print(f"总耗时: {self.total_time:.2f}秒")
        print(f"吞吐量: {self.throughput:.2f} 文件/秒")
        print("=" * 50)


class BatchProcessor:
    """批量处理器"""

    def __init__(self, config: BatchConfig = None):
        self.config = config or BatchConfig()
        if self.config.max_workers <= 0:
            self.config.max_workers = multiprocessing.cpu_count()

    def process_files(
        self,
        file_patterns: List[str],
        processor: Callable[[str], Any],
        output_dir: Optional[str] = None,
        output_ext: str = ".md",
    ) -> BatchReport:
        files = self._collect_files(file_patterns)
        report = BatchReport(total_files=len(files))
        start_time = datetime.now()

        executor_class = ProcessPoolExecutor if self.config.use_multiprocessing else ThreadPoolExecutor

        with executor_class(max_workers=self.config.max_workers) as executor:
            futures = {
                executor.submit(self._process_single, f, processor, output_dir, output_ext): f
                for f in files
            }
            completed = 0
            for future in as_completed(futures):
                result = future.result()
                report.results.append(result)
                if result.success:
                    report.successful += 1
                else:
                    report.failed += 1
                completed += 1
                if self.config.progress_callback:
                    self.config.progress_callback(completed, len(files))

        report.total_time = (datetime.now() - start_time).total_seconds()
        report.throughput = len(files) / report.total_time if report.total_time > 0 else 0
        return report

    def _collect_files(self, patterns: List[str]) -> List[str]:
        files = []
        for pattern in patterns:
            if os.path.isfile(pattern):
                files.append(pattern)
            else:
                matched = glob.glob(pattern, recursive=True)
                files.extend([f for f in matched if os.path.isfile(f)])
        return list(set(files))

    def _process_single(
        self,
        file_path: str,
        processor: Callable[[str], Any],
        output_dir: Optional[str],
        output_ext: str,
    ) -> BatchResult:
        start_time = datetime.now()
        retries = 0
        last_error = None

        max_attempts = self.config.max_retries + 1 if self.config.retry_failed else 1

        for attempt in range(max_attempts):
            try:
                result = processor(file_path)
                output_path = None
                if output_dir:
                    os.makedirs(output_dir, exist_ok=True)
                    base_name = os.path.splitext(os.path.basename(file_path))[0]
                    output_path = os.path.join(output_dir, base_name + output_ext)
                    with open(output_path, "w", encoding="utf-8") as f:
                        f.write(str(result))
                return BatchResult(
                    success=True,
                    file_path=file_path,
                    output_path=output_path,
                    processing_time=(datetime.now() - start_time).total_seconds(),
                    retries=retries,
                )
            except Exception as e:
                last_error = str(e)
                retries += 1

        return BatchResult(
            success=False,
            file_path=file_path,
            error=last_error,
            processing_time=(datetime.now() - start_time).total_seconds(),
            retries=retries,
        )


class DocumentBatchProcessor:
    """文档批量处理器"""

    def __init__(self, config: BatchConfig = None):
        self.config = config or BatchConfig()
        self.processor = BatchProcessor(self.config)

    def convert_to_markdown(
        self,
        input_patterns: List[str],
        output_dir: str,
        clean: bool = True,
    ) -> BatchReport:
        from formats import convert_to_markdown
        from cleaner import clean_document

        def process(file_path: str) -> str:
            md = convert_to_markdown(file_path)
            if clean:
                md = clean_document(md)
            return md

        return self.processor.process_files(
            input_patterns,
            process,
            output_dir,
            ".md",
        )

    def convert_to_html(
        self,
        input_patterns: List[str],
        output_dir: str,
    ) -> BatchReport:
        from formats import convert_to_markdown
        from converter import md_to_html

        def process(file_path: str) -> str:
            md = convert_to_markdown(file_path)
            return md_to_html(md)

        return self.processor.process_files(
            input_patterns,
            process,
            output_dir,
            ".html",
        )

    def extract_images(
        self,
        input_patterns: List[str],
        output_dir: str,
    ) -> BatchReport:
        from image_extractor import extract_images_from_document

        def process(file_path: str) -> str:
            images = extract_images_from_document(file_path, output_dir)
            return json.dumps(images, ensure_ascii=False, indent=2)

        return self.processor.process_files(
            input_patterns,
            process,
            output_dir,
            "_images.json",
        )


def batch_convert(
    input_patterns: List[str],
    output_dir: str,
    output_format: str = "markdown",
    clean: bool = True,
    max_workers: int = 4,
    use_multiprocessing: bool = False,
) -> BatchReport:
    """批量转换文档的便捷函数"""
    config = BatchConfig(
        max_workers=max_workers,
        use_multiprocessing=use_multiprocessing,
    )
    processor = DocumentBatchProcessor(config)
    if output_format.lower() in ("md", "markdown"):
        return processor.convert_to_markdown(input_patterns, output_dir, clean)
    elif output_format.lower() == "html":
        return processor.convert_to_html(input_patterns, output_dir)
    else:
        raise ValueError(f"不支持的输出格式: {output_format}")
