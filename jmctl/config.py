import os
import shutil
import tempfile
import uuid
import datetime

def get_work_dir(run_id=None):
    if run_id is None:
        run_id = str(uuid.uuid4())
    work_dir = os.path.join(tempfile.gettempdir(), "pctl", run_id)
    os.makedirs(work_dir, exist_ok=True)
    return work_dir

def get_jmeter():
    jmeter_path = shutil.which("jmeter")
    if jmeter_path is None:
        raise FileNotFoundError("jmeter not found in PATH. Please install jmeter to use jmctl.")
    return jmeter_path