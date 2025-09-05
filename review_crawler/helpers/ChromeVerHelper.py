import sys
import asyncio
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    import winreg

def get_chrome_major_version():
    if sys.platform != 'win32':
        return None
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Google\Chrome\BLBeacon') as key:
            version_string, _ = winreg.QueryValueEx(key, 'version')
            major_version = int(version_string.split('.')[0])
            return major_version
    except FileNotFoundError:
        return None
    except Exception:
        return None