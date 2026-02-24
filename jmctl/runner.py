import subprocess
import os
from jmctl.config import get_jmeter, get_work_dir
from datetime import datetime
import json
from jmctl.hashing import sha256
from pprint import pprint
import csv

def parse_jtl(filepath: str):
  rows = []
  with open(filepath, 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
      rows.append(row)

  if not rows:
    return None
  
  timestamps = [int(r['timeStamp']) for r in rows]
  elapsed_times = [int(r['elapsed']) for r in rows]
  all_threads = [int(r['allThreads']) for r in rows]
  successes = [r['success'].strip().lower() == 'true' for r in rows]

  total_requests = len(rows)
  failed_requests = len([s for s in successes if not s])
  start_time = min(timestamps)
  end_time = max(ts + el for ts, el in zip(timestamps, elapsed_times))
  duration_sec = (end_time - start_time) / 1000

  minutes = int(duration_sec // 60)
  seconds = int(duration_sec % 60)
  duration = f"{minutes}m {seconds}s"

  v_users = max(all_threads)

  avg_response_time = sum(elapsed_times) / total_requests if total_requests > 0 else 0
  avg_response_time_str = f"{avg_response_time:.0f} ms"

  error_rate = (failed_requests / total_requests) * 100 if total_requests > 0 else 0
  error_rate_str = f"{error_rate:.2f}%"

  throughput = total_requests / duration_sec if duration_sec > 0 else 0
  throughput_str = f"{throughput:.2f} req/s"

  if error_rate > 5:
    status = "failed"
  elif error_rate > 1:
    status = "warning"
  else:
    status = "passed"

  return {
    "duration": duration,
    "v_users": v_users,
    "avg_response_time": avg_response_time_str,
    "error_rate": error_rate_str,
    "throughput": throughput_str,
    "run_status": status
  }

def run(jmx_path, run_id):
  work_dir = get_work_dir(run_id if run_id else None)
  os.makedirs(work_dir, exist_ok=True)

  jtl_path = os.path.join(work_dir, "results.jtl")
  log_path = os.path.join(work_dir, "pytest.log")

  pytest_cmd = [get_jmeter(), "-n", "-t", jmx_path, "-l", jtl_path, "-j", log_path]

  proc = subprocess.Popen(
    pytest_cmd,
    stdout=subprocess.PIPE, 
    stderr=subprocess.STDOUT, 
    text=True, bufsize=1, 
    creationflags=subprocess.CREATE_NO_WINDOW
  )

  for line in proc.stdout:
    print(line, end="")

  proc.wait()

  result = parse_jtl(jtl_path)
  result['exit_code'] = proc.returncode
  result['jtl_path'] = jtl_path
  result['log_path'] = log_path
  result['jmx_path'] = jmx_path
  result['artifacts'] = {'jtl_hash': sha256(jtl_path),
                         'log_hash': sha256(log_path)}

  return result