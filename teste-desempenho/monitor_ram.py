import argparse, subprocess, threading, time, re, json, os
from datetime import datetime
from pathlib import Path

def parse_mem_to_gb(s):
    if not s:
        return None
    head = s.split('/')[0].strip().replace(',', '.')
    m = re.match(r'^([0-9]+(?:\.[0-9]+)?)\s*([KMG]i?B)$', head, re.IGNORECASE)
    if not m:
        return None
    val = float(m.group(1))
    unit = m.group(2).lower()
    if unit in ('kib','kb'):
        return val/(1024.0*1024.0)
    if unit in ('mib','mb'):
        return val/1024.0
    if unit in ('gib','gb'):
        return val
    return None

def sample_once(hint):
    out = subprocess.run(["docker","stats","--no-stream","--format","{{.Name}},{{.MemUsage}}"], capture_output=True, text=True)
    if out.returncode != 0 or not out.stdout:
        return []
    rows = []
    for line in out.stdout.strip().splitlines():
        parts = [p.strip() for p in line.split(",")]
        if len(parts) >= 2 and hint.lower() in parts[0].lower():
            rows.append((parts[0], parts[1]))
    return rows

def monitor(hint, interval, stop_event, log_path, peak_holder):
    with open(log_path, "w", encoding="utf-8") as f:
        while not stop_event.is_set():
            ts = datetime.now().isoformat()
            rows = sample_once(hint)
            for name, mem in rows:
                f.write(f"{ts},{name},{mem}\n")
                f.flush()
                gb = parse_mem_to_gb(mem)
                if isinstance(gb, float) and gb > (peak_holder["peak"] or 0.0):
                    peak_holder["peak"] = gb
            time.sleep(interval)

def run_cmd(cmd):
    return subprocess.run(cmd, shell=True).returncode

def update_results_json(results_path, scenario, peak_gb):
    p = Path(results_path)
    if not p.exists():
        return
    data = json.loads(p.read_text(encoding="utf-8"))
    data.setdefault("testes",{}).setdefault(scenario,{})["peak_mem_gb"] = peak_gb
    p.write_text(json.dumps(data, indent=2), encoding="utf-8")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hint", required=True)
    ap.add_argument("--interval", type=float, default=1.0)
    ap.add_argument("--out-dir", default=".")
    ap.add_argument("--tag", default="run1")
    ap.add_argument("--duration", type=int, default=0)
    ap.add_argument("--cmd", default="")
    ap.add_argument("--results-json", default="")
    ap.add_argument("--scenario", default="")
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    log_path = out_dir / f"mem_{args.hint}_{args.tag}.log"
    json_path = out_dir / f"mem_{args.hint}_{args.tag}.json"

    stop_event = threading.Event()
    peak_holder = {"peak": 0.0}
    th = threading.Thread(target=monitor, args=(args.hint, args.interval, stop_event, str(log_path), peak_holder), daemon=True)
    th.start()

    start_ts = datetime.now().isoformat()
    rc = 0
    if args.cmd:
        rc = run_cmd(args.cmd)
    elif args.duration > 0:
        time.sleep(args.duration)
    else:
        try:
            while True:
                time.sleep(0.5)
        except KeyboardInterrupt:
            pass
    stop_event.set()
    th.join(timeout=5)
    end_ts = datetime.now().isoformat()

    result = {
        "hint": args.hint,
        "tag": args.tag,
        "started_at": start_ts,
        "ended_at": end_ts,
        "peak_mem_gb": round(float(peak_holder["peak"] or 0.0), 6),
        "cmd_rc": rc
    }
    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    if args.results_json and args.scenario:
        update_results_json(args.results_json, args.scenario, result["peak_mem_gb"])

if __name__ == "__main__":
    main()
