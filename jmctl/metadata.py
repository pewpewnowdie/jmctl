import socket
from datetime import datetime
import subprocess
from jmctl.config import get_jmeter, get_work_dir
import re

def collect():
    jmeter_version = subprocess.run([get_jmeter(), "--version"], capture_output=True, text=True).stdout.strip()
    match = re.search(r'(\d+(?:\.\d+)+)', jmeter_version)
    metadata = {
        "host": socket.gethostname(),
        "start_time": datetime.now().isoformat(),
        "jmeter_version": match.group(1) if match else "unknown"
    }
    return metadata

