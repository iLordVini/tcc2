import subprocess, json, time

from datetime import datetime

from pathlib import Path

BASE_URL = "http://localhost:3000"

HINT = "postgrest_api"

MONITOR = str((Path(__file__).parent.parent / "monitor_ram.py").resolve())

PROFILES = {
    "load": """{ "stages": [ { "duration": "2m", "target": 25 }, { "duration": "7m", "target": 25 }, { "duration": "2m", "target": 0 } ] }""",
    "stress": """{ "stages": [ { "duration": "2m", "target": 50 }, { "duration": "5m", "target": 50 }, { "duration": "1m", "target": 0 } ] }""",
    "spike": """{ "stages": [ { "duration": "1m", "target": 15 }, { "duration": "30s", "target": 100 }, { "duration": "2m", "target": 100 }, { "duration": "30s", "target": 15 }, { "duration": "1m", "target": 0 } ] }""",
    "soak": """{ "stages": [ { "duration": "2m", "target": 15 }, { "duration": "15m", "target": 15 }, { "duration": "3m", "target": 0 } ] }"""
}

def build_k6_script(stage_profile):
    return f"""
import http from 'k6/http';
import {{ check, group, sleep }} from 'k6';
export const options = {stage_profile};
const BASE_URL = '{BASE_URL}';
const MIN_ID = 1;
const MAX_ID = 1000000;
export default function () {{
  const rand = Math.random();
  const randomId = Math.floor(Math.random() * (MAX_ID - MIN_ID + 1)) + MIN_ID;
  if (rand < 0.60) {{
    group('GET - Leitura', function () {{
      const r = http.get(`${{BASE_URL}}/products?id=eq.${{randomId}}`);
      check(r, {{ 'GET status 200': (x) => x.status === 200 }});
      sleep(0.2);
    }});
  }} else {{
    group('POST - Criar', function () {{
      const create = http.post(
        `${{BASE_URL}}/products`,
        JSON.stringify({{ name: "Produto Teste PostgREST", price: 1 }}),
        {{ headers: {{ 'Content-Type': 'application/json', 'Prefer': 'return=representation' }} }}
      );
      check(create, {{ 'POST 201': (r) => r.status === 201 }});
      sleep(0.2);
    }});
  }}
}}
""".strip()

def _pick(metrics, keys):

    for k in keys:

        if k in metrics:

            return metrics[k]

    return {}


def _avg_p95(mo):

    if not mo:

        return None, None

    v = mo.get("values")

    if isinstance(v, dict):

        return v.get("avg"), v.get("p(95)")

    return mo.get("avg"), mo.get("p(95)")


def _rate(mo):

    if not mo:

        return None

    v = mo.get("values")

    if isinstance(v, dict) and "rate" in v:

        return v.get("rate")

    return mo.get("rate") or mo.get("value")


def parse_k6_summary(p):

    d = json.loads(p.read_text(encoding="utf-8"))

    m = d.get("metrics", {})

    dur = _pick(m, ["http_req_duration{expected_response:true}", "http_req_duration", "http_req_waiting"])

    avg_ms, p95_ms = _avg_p95(dur)

    thp = _rate(m.get("http_reqs", {})) or _rate(m.get("iterations", {}))

    fail = _rate(m.get("http_req_failed", {}))

    succ = (1 - fail) if isinstance(fail, (int, float)) else None

    return {"avg_ms": avg_ms, "p95_ms": p95_ms, "throughput_rps": thp, "fail_rate": fail, "success_rate": succ}


def run_k6(profile_name, workdir: Path, run_dir: Path):

    js_path = run_dir / f"test_{profile_name}.js"

    js_path.write_text(build_k6_script(PROFILES[profile_name]), encoding="utf-8")

    summary_file = run_dir / f"results_{profile_name}_summary.json"

    tag = profile_name

    cmd = f'k6 run "{js_path}" --summary-export "{summary_file}"'

    subprocess.run(["python", MONITOR, "--hint", HINT, "--interval", "1", "--out-dir", str(run_dir), "--tag", tag, "--cmd", cmd], check=False)

    res = {}

    if summary_file.exists():

        res = parse_k6_summary(summary_file)

    mem_json = run_dir / f"mem_{HINT}_{tag}.json"

    if mem_json.exists():

        try:

            res["peak_mem_gb"] = json.loads(mem_json.read_text(encoding="utf-8")).get("peak_mem_gb")

        except:

            res["peak_mem_gb"] = None

    return res


def main():

    start_ts = datetime.now().strftime("%Y%m%d-%H%M%S")

    script_dir = Path(__file__).parent.resolve()

    run_dir = script_dir / start_ts

    run_dir.mkdir(parents=True, exist_ok=True)

    resultados = {"ferramenta": "PostgREST", "cenario": "60/40", "timestamp": start_ts, "testes": {}}

    workdir = script_dir

    for profile_name in ["soak"]:

        resultados["testes"][profile_name] = run_k6(profile_name, workdir, run_dir)

        time.sleep(3)

    (script_dir / f"results_postgrest_60_40_{start_ts}.json").write_text(json.dumps(resultados, indent=2), encoding="utf-8")


if __name__ == "__main__":

    main()
