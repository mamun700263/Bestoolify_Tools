import csv
import io
import json
from typing import Dict, List

import pandas as pd

from app.core.data_exporters import FileSaver


class InMemoryExporter:

    @staticmethod
    def export(data: List[Dict], file_type: str = "csv") -> io.BytesIO:
        if file_type == "csv":
            return InMemoryExporter._csv(data)
        elif file_type == "json":
            return InMemoryExporter._json(data)
        elif file_type == "xlsx":
            return InMemoryExporter._excel(data)
        else:
            raise ValueError(f"❌ Unsupported format: {file_type}")

    @staticmethod
    def _csv(data: List[Dict]) -> io.BytesIO:
        stream = io.StringIO()
        writer = csv.DictWriter(stream, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        byte_stream = io.BytesIO()
        byte_stream.write(stream.getvalue().encode("utf-8"))
        byte_stream.seek(0)
        return byte_stream

    @staticmethod
    def _json(data: List[Dict]) -> io.BytesIO:
        json_str = json.dumps(data, indent=4, ensure_ascii=False)
        byte_stream = io.BytesIO(json_str.encode("utf-8"))
        return byte_stream

    @staticmethod
    def _excel(data: List[Dict]) -> io.BytesIO:
        stream = io.BytesIO()
        pd.DataFrame(data).to_excel(stream, index=False)
        stream.seek(0)
        return stream
