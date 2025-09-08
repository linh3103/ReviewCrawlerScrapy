from datetime import datetime

def format_date_str(dateStr: str) -> str:
    dt = datetime.strptime(dateStr, "%y.%m.%d")
    return dt.strftime("%Y.%m.%d")