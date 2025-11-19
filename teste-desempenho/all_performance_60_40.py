import subprocess, sys, re, json, time
from datetime import datetime
from pathlib import Path

def find_script(base, candidates):
    for rel in candidates:
        p = base / rel
        if p.exists():
            return p
    return None

def existing_run_dirs(tool_dir):
    pat = re.compile(r"^\d{8}-\d{6}$")
    return {d.name: d for d in tool_dir.iterdir() if d.is_dir() and pat.match(d.name)}

def newest_run_dir(tool_dir):
    dirs = [d for d in tool_dir.iterdir() if d.is_dir()]
    if not dirs:
        return None
    return max(dirs, key=lambda d: d.stat().st_mtime)

def collect_results(run_dir):
    res = []
    for p in run_dir.glob("results_*_*.json"):
        res.append(str(p.resolve()))
    for p in run_dir.glob("mem_*_*.json"):
        res.append(str(p.resolve()))
    for p in run_dir.glob("results_*_summary.json"):
        res.append(str(p.resolve()))
    return res

def run_tool(name, script_path):
    tool_dir = script_path.parent
    before = existing_run_dirs(tool_dir)
    rc = subprocess.run([sys.executable, str(script_path)], cwd=str(tool_dir)).returncode
    after = existing_run_dirs(tool_dir)
    newdirs = [d for k, d in after.items() if k not in before]
    run_dir = newdirs[0] if newdirs else newest_run_dir(tool_dir)
    outputs = collect_results(run_dir) if run_dir else []
    return {
        "tool": name,
        "script": str(script_path.resolve()),
        "cwd": str(tool_dir.resolve()),
        "return_code": rc,
        "run_dir": str(run_dir.resolve()) if run_dir else None,
        "artifacts": outputs
    }

def main():
    base = Path(__file__).parent
    scripts = [
        ("DreamFactory", find_script(base, ["dreamfactory/dreamfactory_performance_60_40.py"])),
        ("NocoDB", find_script(base, ["nocodb/nocodb_performance_60_40.py"])),
        ("pREST", find_script(base, ["prest/prest_performance_60_40.py"])),
        ("PostgREST", find_script(base, ["postgrest/postgrest_performance_60_40.py"]))
    ]
    session = datetime.now().strftime("%Y%m%d-%H%M%S")
    summary = {"session": session, "started_at": datetime.now().isoformat(), "sequence": [], "errors": []}
    for name, script in scripts:
        if script is None:
            summary["errors"].append({"tool": name, "error": "script_not_found"})
            continue
        info = run_tool(name, script)
        summary["sequence"].append(info)
        time.sleep(3)
    summary["ended_at"] = datetime.now().isoformat()

if __name__ == "__main__":
    main()
