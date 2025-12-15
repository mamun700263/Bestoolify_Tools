import inspect
import json
import logging
import os
import re
import sys
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler
from typing import List, Optional


class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }
        for key, value in record.__dict__.items():
            if key not in (
                "args",
                "asctime",
                "created",
                "exc_info",
                "exc_text",
                "filename",
                "funcName",
                "levelname",
                "levelno",
                "lineno",
                "module",
                "msecs",
                "message",
                "msg",
                "name",
                "pathname",
                "process",
                "processName",
                "relativeCreated",
                "stack_info",
                "thread",
                "threadName",
            ):
                log_record[key] = value
        return json.dumps(log_record)


class Logger:
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    log_pattern = re.compile(r"\[(.*?)\] \[(.*?)\] \[(.*?)\] (.*)")

    @classmethod
    def get_logger(
        cls,
        name: str = None,
        file_name: Optional[str] = None,
        to_console: bool = False,
        format: str = "text",
    ) -> logging.Logger:

        if not name:
            name = cls.name_finder()

        file_name = file_name or name
        log_file = os.path.join(cls.log_dir, f"{file_name}.log")

        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)

        if not any(isinstance(h, RotatingFileHandler) for h in logger.handlers):
            # Choose formatter based on input
            if format == "json":
                formatter = JSONFormatter()
            else:
                formatter = cls.formatter

            file_handler = RotatingFileHandler(
                log_file, maxBytes=5 * 1024 * 1024, backupCount=3
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

            if to_console:
                stream_handler = logging.StreamHandler(sys.stdout)
                stream_handler.setFormatter(formatter)
                logger.addHandler(stream_handler)

        return logger

    @staticmethod
    def name_finder(default: str = "default") -> str:
        try:
            for frame_info in inspect.stack():
                module = inspect.getmodule(frame_info.frame)

                if module and hasattr(module, "__file__"):
                    path = module.__file__
                    if "logger" not in os.path.basename(path).lower():
                        return os.path.splitext(os.path.basename(path))[0]
        except Exception:
            pass
        return default

    @staticmethod
    def parse_log_line(line: str):
        match = Logger.log_pattern.match(line)
        if not match:
            return None, None
        try:
            log_time = datetime.strptime(match.group(1), "%Y-%m-%d %H:%M:%S")
            return log_time, line.strip()

        except Exception:
            return None, None

    @staticmethod
    def parse_to_datetime(dt_str: str, is_start=True) -> datetime:
        """Parse date string. Accepts 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS'."""
        formats = ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]
        for fmt in formats:
            try:
                dt = datetime.strptime(dt_str, fmt)
                if fmt == "%Y-%m-%d":
                    return (
                        dt.replace(hour=0, minute=0, second=0)
                        if is_start
                        else dt.replace(hour=23, minute=59, second=59)
                    )
                return dt
            except ValueError:
                continue
        raise ValueError(
            f"Invalid date string '{dt_str}'. Use 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS'"
        )

    @staticmethod
    def filter_logs(
        file_path: str,
        start_time: str,
        end_time: str,
        level: Optional[str] = None,
        name: Optional[str] = None,
        time_format: str = "%Y-%m-%d %H:%M:%S",
        limit: Optional[int] = None,
    ) -> List[str]:
        """Filter log lines by time range, level, and page/module name."""

        try:
            start_dt = Logger.parse_to_datetime(start_time, True)
            end_dt = Logger.parse_to_datetime(end_time, is_start=False)
        except ValueError as e:
            raise ValueError(
                f"Time parsing failed. Format should be: {time_format}"
            ) from e

        if start_dt > end_dt:
            raise ValueError("start_time must be before end_time")
        results = []
        level_tag = level.upper() if level else None
        name_tag = name.lower() if name else None

        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                log_time, clean_line = Logger.parse_log_line(line)
                if not log_time:
                    continue
                if not (start_dt <= log_time <= end_dt):
                    continue
                if level_tag and f"[{level_tag}]" not in clean_line.upper():
                    continue
                if name_tag and f"[{name_tag}]" not in clean_line.lower():
                    continue
                results.append(clean_line)

                if limit and len(results) >= limit:
                    break

        return results

    @staticmethod
    def last_n_minutes_logs(file_path: str, n: int = 30, **kwargs):
        end = datetime.now()
        start = end - timedelta(minutes=n)
        return Logger.filter_logs(
            file_path=file_path,
            start_time=start.strftime("%Y-%m-%d %H:%M:%S"),
            end_time=end.strftime("%Y-%m-%d %H:%M:%S"),
            **kwargs,
        )

    @staticmethod
    def last_n_hours_logs(file_path: str, n: int = 1, **kwargs):
        end = datetime.now()
        start = end - timedelta(hours=n)
        return Logger.filter_logs(
            file_path=file_path,
            start_time=start.strftime("%Y-%m-%d %H:%M:%S"),
            end_time=end.strftime("%Y-%m-%d %H:%M:%S"),
            **kwargs,
        )

    @staticmethod
    def last_n_days_logs(file_path: str, n: int = 1, **kwargs):
        end = datetime.now()
        start = end - timedelta(days=n)
        return Logger.filter_logs(
            file_path=file_path,
            start_time=start.strftime("%Y-%m-%d %H:%M:%S"),
            end_time=end.strftime("%Y-%m-%d %H:%M:%S"),
            **kwargs,
        )
