from app.core.data_exporters.download_able import export_to_download
from app.uptime_keeper.caching.db_to_redis import get_ping_history

def monitor_ping_data(monitor_id:str,file_name:str,since_hours:int=24):
    data = get_ping_history(monitor_id,since_hours)
    return export_to_download(data,file_name)