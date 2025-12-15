import csv
import json
import os
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

from app.core import Logger

logger = Logger.get_logger(__name__, "Data Exporters")


class FileSaver:

    VALID_EXTENSIONS = {
        ".csv": "csv",
        ".json": "json",
        ".xlsx": "excel",
        ".sqlite": "db",
    }

    @staticmethod
    def check_format(file_name: str) -> str:
        file_path = Path(file_name)
        ext = file_path.suffix.lower()
        if ext in FileSaver.VALID_EXTENSIONS:
            return FileSaver.VALID_EXTENSIONS[ext]
        else:
            raise ValueError(
                f"❌ Invalid file extension: {ext}. Supported: {list(FileSaver.VALID_EXTENSIONS.keys())}"
            )

    @staticmethod
    def save(
        items: list[dict[str:str]],
        file_name: Optional[str],
        table_name: Optional[str] = "products",
        mode: str = "overwrite",
    ):
        if not items:
            logger.warning("⚠️ No items to save.")
            return
        if file_name:
            FileSaver._save_to_file(file_name, items, table_name, mode)
        else:
            logger.warning("⚠️ No file name provided and no API endpoint.")

    @staticmethod
    def _save_to_file(
        file_name: str, items: list[dict[str:str]], table_name: str, mode: str
    ):
        ext = FileSaver.check_format(file_name)
        if mode == "overwrite":
            mode = "save"
        method_name = f"_{mode}_{ext}"
        logger.info(method_name)
        method = getattr(FileSaver, method_name, None)

        if callable(method):
            if ext == "sqlite":
                method(file_name, items, table_name)
            else:
                method(file_name, items)
        else:
            logger.error(f"❌ Unsupported  mode:  {mode} {method_name}")

    @staticmethod
    def _save_csv(file_name, items: pd.DataFrame):
        try:
            with open(file_name, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=items[0].keys())
                writer.writeheader()
                writer.writerows(items)
            logger.info(f"✅ Data saved as CSV: {file_name}")
        except Exception as e:
            logger.error(f"❌ Failed to save CSV: {e}")

    @staticmethod
    def _append_csv(file_name: str, items: List[Dict[str, str]]):
        try:
            file_exists = os.path.isfile(file_name)
            with open(file_name, mode="a", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=items[0].keys())

                if not file_exists:
                    writer.writeheader()
                writer.writerows(items)

            logger.info(f"➕ Appended {len(items)} rows to CSV: {file_name}")
        except Exception as e:
            logger.error(f"❌ Failed to append to CSV: {e}")

    @staticmethod
    def _save_json(file_name, items: List[Dict[str, str]]):
        try:
            with open(file_name, "w", encoding="utf-8") as f:
                json.dump(items, f, ensure_ascii=False, indent=4)
            logger.info(f"✅ Data saved as JSON: {file_name}")
        except Exception as e:
            logger.error(f"❌ Failed to save JSON: {e}")

    @staticmethod
    def _append_json(file_name, items: List[Dict[str, str]]):
        try:
            if Path(file_name).exists():
                with open(
                    file_name,
                    "r",
                ) as f:
                    try:
                        existing_data = json.load(f)
                        if not isinstance(existing_data, list):
                            existing_data = []
                    except json.JSONDecodeError:
                        existing_data = []
            else:
                existing_data = []
            existing_data.extend(items)

            with open(file_name, "w", encoding="utf-8") as f:
                json.dump(existing_data, f, ensure_ascii=False, indent=4)
            logger.info(f"➕ Appended {len(items)} items to JSON: {file_name}")

        except Exception as e:
            logger.error(f"❌ Failed to append to JSON:{e}")

    @staticmethod
    def _save_excel(file_name, items: List[Dict[str, str]]):
        try:
            pd.DataFrame(items).to_excel(file_name, index=False)
            logger.info(f"✅ Data saved as Excel: {file_name}")
        except Exception as e:
            logger.error(f"❌ Failed to save Excel: {e}")

    @staticmethod
    def _append_excel(file_name, items: List[Dict[str, str]]):
        try:
            if Path(file_name).exists():
                existing_data = pd.read_excel(file_name)
            else:
                existing_data = pd.DataFrame()
            new_df = pd.DataFrame(items)
            if not existing_data.empty:
                if set(existing_data.columns) != set(new_df.columns):
                    logger.warning(
                        "⚠️ Column mismatch between existing and new Excel data."
                    )

            data_f = pd.concat([existing_data, new_df], ignore_index=True)

            data_f.to_excel(file_name, index=False)
            logger.info(f"➕ Appended {len(new_df)} rows to Excel: {file_name}")

        except Exception as e:
            logger.error(f"❌ Failed to append to Excel: {e}")

    @staticmethod
    def _save_sqlite(file_name, items: List[Dict[str, str]], table_name):
        if not items:
            logger.warning("⚠️ No data to save to SQLite.")
            return
        try:
            with sqlite3.connect(file_name) as conn:
                cursor = conn.cursor()
                columns = ", ".join([f"{key} TEXT" for key in items[0].keys()])
                cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})")
                for item in items:
                    placeholders = ", ".join(["?"] * len(item))
                    values = tuple(item.values())
                    cursor.execute(
                        f"INSERT INTO {table_name} VALUES ({placeholders})", values
                    )
                conn.commit()
                logger.info(f"✅ Data saved to SQLite: {file_name} → {table_name}")
        except Exception as e:
            logger.error(f"❌ Failed to save SQLite: {e}")

    @staticmethod
    def _append_sqlite(file_name, items: List[Dict[str, str]], table_name: str):
        if not items:
            logger.warning("⚠️ No data to append to SQLite.")
            return

        try:
            with sqlite3.connect(file_name) as conn:
                cursor = conn.cursor()

                # Create table if not exists
                schema_cols = ", ".join([f"{key} TEXT" for key in items[0].keys()])
                cursor.execute(
                    f"CREATE TABLE IF NOT EXISTS {table_name} ({schema_cols})"
                )

                # Insert each row
                for item in items:
                    col_names_list = list(item.keys())
                    col_names = ", ".join(col_names_list)
                    placeholders = ", ".join(["?"] * len(col_names_list))
                    values = tuple(item[col] for col in col_names_list)

                    cursor.execute(
                        f"INSERT INTO {table_name} ({col_names}) VALUES ({placeholders})",
                        values,
                    )

                conn.commit()
                logger.info(
                    f"✅ Appended {len(items)} rows to SQLite table '{table_name}' in file '{file_name}'"
                )
        except Exception as e:
            logger.error(f"❌ Failed to append to SQLite: {e}")


# this file needs to be refactor in the future
# 📦 data_exporters/
# ├── base.py            🔹 Abstract interface: save(), append()
# ├── csv_saver.py       🔹 CSV-specific logic
# ├── json_saver.py      🔹 JSON logic
# ├── excel_saver.py     🔹 Excel logic
# ├── sqlite_saver.py    🔹 SQLite logic
# └── factory.py         🔹 FileSaverFactory: maps extension → handler


# work on sqlite

# peewee
