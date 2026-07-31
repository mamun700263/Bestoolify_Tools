import io

import pandas as pd
from fastapi.responses import StreamingResponse
from app.core import Logger

logger = Logger.get_logger(__name__,"Data Exporters")

def export_to_download(data:list[dict],format: str = "csv"):
    df = pd.DataFrame(data)
    buffer = io.BytesIO()
    headers = {}

    logger.info(f"saving file as {format}")
    if format == "csv":
        buffer = io.StringIO()
        df.to_csv(buffer, index=False)
        buffer.seek(0)
        headers = {"Content-Disposition": 'attachment; filename="results.csv"'}
        return StreamingResponse(buffer, media_type="text/csv", headers=headers)

    elif format == "json":
        buffer.write(df.to_json(orient="records", indent=4).encode("utf-8"))
        buffer.seek(0)
        headers = {"Content-Disposition": 'attachment; filename="results.json"'}
        return StreamingResponse(buffer, media_type="application/json", headers=headers)

    elif format == "excel":
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Results")
        buffer.seek(0)
        headers = {"Content-Disposition": 'attachment; filename="results.xlsx"'}
        return StreamingResponse(
            buffer,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers=headers,
        )

