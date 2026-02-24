import requests
import json
import os
from pprint import pprint

BASE_URL = "http://localhost:8080"

def login(username, password):
    url = f"{BASE_URL}/auth/login"
    payload = {"username": username, "password": password}
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        return None
    
def get_projects(access_token):
  projects_response = requests.get(
      f"{BASE_URL}/projects",
      headers={
          "Authorization": f"Bearer {access_token}"
      }
  )
  if projects_response.status_code == 200:
      return projects_response.json()
  else:
    return None
  
def start_test(meta, access_token):
  url = f"{BASE_URL}/jmeter_runs/start"
  payload = {
    "project_key": meta.get("project_key"),
    "release": meta.get("release"),
    "run_name": meta.get("run_name"),
    "host": meta.get("host"),
    "jmeter_version": meta.get("jmeter_version"),
    "start_time": meta.get("start_time"),
    "jmx_hash": meta.get("jmx_hash")
  }
  response = requests.post(url, json=payload, headers={"Authorization": f"Bearer {access_token}"})    
  if response.ok:
    return response.json()
  else:
     return None
  
def stop_test(run_id, meta, upload_token, access_token):
  url = f"{BASE_URL}/jmeter_runs/stop/{run_id}"
  headers={"Authorization": f"Bearer {access_token}",
           "X-Run-Token": upload_token}
  data = meta.copy()
  jmx_path = data.pop("jmx_path", None)
  jtl_path = data.pop("jtl_path", None)
  log_path = data.pop("log_path", None)
  data["script_name"] = os.path.basename(jmx_path) if jmx_path else "unknown.jmx"
  response = requests.post(
     url, 
     data={
      "metadata": json.dumps(data),
     },
     files={
       "jmx": open(jmx_path, "rb") if jmx_path else None,
       "jtl": open(jtl_path, "rb") if jtl_path else None,
       "log": open(log_path, "rb") if log_path else None, 
     }, 
     headers=headers
  )
  if response.ok:
    return response.json()
  else:
     return None