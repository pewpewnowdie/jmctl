import sys
import os
import questionary
from rich import print
from rich.rule import Rule

from jmctl.api import login, get_projects, start_test, stop_test
from jmctl.runner import run
from jmctl.metadata import collect
from jmctl.hashing import sha256

def main():
  if len(sys.argv) < 3 or sys.argv[1] != "run":
    print("[red]Usage: jmctl run <jmx_file>[/red]")
    sys.exit(1)

  jmx = sys.argv[2]
  if not os.path.exists(jmx):
    print(f"[red]Error: JMX file '{jmx}' does not exist[/red]")
    sys.exit(1)

  print(Rule("[bold cyan]JMCTL[/bold cyan]"))

  while(True):
    print("[dim]Please authenticate with your creds to continue[/dim]")

    username = questionary.text(
      "Username:",
      validate=lambda x: True if x.strip() else "Username cannot be empty"
    ).ask()

    password = questionary.text(
      "Password:",
      validate=lambda x: True if x.strip() else "Username cannot be empty"
    ).ask()

    access_token = login(username, password)
    if not access_token:
      print("[red]Authentication failed[/red]")
    else:
      break

  projects = get_projects(access_token)
  
  print("[green]Login successful![/green]")

  if not projects or len(projects) == 0:
    print("[red]Failed to fetch projects[/red]")
    sys.exit(1)
  
  project_key = questionary.select(
    "Select a project:",
    choices=[questionary.Choice(f"{p['name']} ({p['project_key']})", value=p['project_key']) for p in projects]
  ).ask()

  releases = [p["releases"] for p in projects if p['project_key'] == project_key][0]

  if not releases or len(releases) == 0:
    print("[red]No releases found for the selected project[/red]")
    sys.exit(1)

  release = questionary.select(
    "Select a release:",
    choices=[questionary.Choice(r['name'], value=r['id']) for r in releases]
  ).ask()

  run_name = questionary.text(
    "Run Name:",
    validate=lambda x: True if x and len(x.strip()) > 0 and len(x.strip()) <= 50 else "Run name length should be between 1 and 50 characters",
    validate_while_typing=False
  ).ask()

  if not run_name:
    print("[red]Run name is required[/red]")
    sys.exit(1)

  print()

  meta = collect()
  meta["user"] = username
  meta["project_key"] = project_key
  meta["run_name"] = run_name
  meta["release"] = release
  meta["jmx_hash"] = sha256(jmx)

  try:
    start_resp = start_test(meta, access_token)
    if not start_resp:
      print("[red]Error in Start Test: Please check if you have access to the selected project and release[/red]")
      sys.exit(1)
  except Exception as e:
    print(f"[red]Error in Start Test: {str(e)}[/red]")
    sys.exit(1)
  
  run_id = start_resp.get("run_id")
  upload_token = start_resp.get("upload_token")

  print("[dim]Running Jmeter...[/dim]\n") 
  result = run(jmx, upload_token)
  try:
    stop_resp = stop_test(run_id, result, upload_token, access_token)
    if not stop_resp:
      print("[red]Error in Stop Test[/red]")
      sys.exit(1)
  except Exception as e:
    print(f"[red]Error in Stop Test: {str(e)}[/red]")
    sys.exit(1)
  print("[green]Test run completed![/green]")