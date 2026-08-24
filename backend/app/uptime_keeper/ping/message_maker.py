from app.core.logger import Logger

logger = Logger.get_logger(__name__,"uptime")


def message_maker(status_code: int) -> str:
    if 200 <= status_code < 300:
        return "Request successful. The service is operating normally."

    if 300 <= status_code < 400:
        return "The service responded with a redirect."

    if 400 <= status_code < 500:
        return "The server rejected the request due to a client-side error."

    if 500 <= status_code < 600:
        return "The server encountered an error while processing the request."

    return "The service returned an unexpected HTTP status code."
