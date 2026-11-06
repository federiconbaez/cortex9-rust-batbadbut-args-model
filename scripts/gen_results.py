"""Regenerate results/ (pure string encoding; nothing is executed)."""
import csv
import hashlib
import io
import itertools
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from rust_bat_args_model.cli import VERSIONS, encode_both  # noqa: E402
from rust_bat_args_model.encoders import Arg  # noqa: E402

SMALL = 'a\\"&%^ |<>()!'


def corpus():
    printable = [chr(c) for c in range(32, 127)] + ["\t"]
    yield from ("".join(p) for p in itertools.product(printable, repeat=2))
    yield from ("".join(p) for p in itertools.product(SMALL, repeat=4))


def main(out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    cases = [json.loads(x) for x in (ROOT / "fixtures/cases.jsonl").read_text().splitlines() if x]
    full, rows = {}, []
    for c in cases:
        r = encode_both(c["script"], [Arg(a["value"], a["raw"]) for a in c["args"]], c["force_quotes"])
        full[c["id"]] = r
        for v in VERSIONS:
            x = r[v]
            rows.append({"id": c["id"], "version": v, "ok": x["ok"],
                         "cmdline_json": json.dumps(x.get("cmdline", ""), ensure_ascii=True),
                         "error_kind": x.get("error_kind", ""),
                         "model_status": x["check"]["model_status"] if x["ok"] else "",
                         "finding_kinds": ";".join(sorted({f["kind"] for f in x["check"]["findings"]})) if x["ok"] else "",
                         "real_cmd_behaviour": "UNKNOWN"})
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=list(rows[0]), lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    (out / "cases.csv").write_text(buf.getvalue())
    (out / "cases.json").write_text(json.dumps(full, indent=1, ensure_ascii=True, sort_keys=True) + "\n")
    tally = {v: {"total": 0, "error": 0, "findings_in_model": 0, "ends_in_quotes": 0,
                 "only_unknown_in_model": 0, "no_findings_in_model": 0} for v in VERSIONS}
    for s in corpus():
        r = encode_both("test.bat", [Arg(s)])
        for v in VERSIONS:
            t = tally[v]
            t["total"] += 1
            if not r[v]["ok"]:
                t["error"] += 1
                continue
            ch = r[v]["check"]
            t[ch["model_status"]] += 1
            t["ends_in_quotes"] += ch["ends_in_quotes"]
    s = io.StringIO()
    sw = csv.writer(s, lineterminator="\n")
    keys = list(tally[VERSIONS[0]])
    sw.writerow(["version"] + keys)
    for v in VERSIONS:
        sw.writerow([v] + [tally[v][k] for k in keys])
    (out / "corpus_tally.csv").write_text(s.getvalue())
    names = ["cases.csv", "cases.json", "corpus_tally.csv"]
    (out / "SHA256SUMS").write_text("".join(
        f"{hashlib.sha256((out / n).read_bytes()).hexdigest()}  {n}\n" for n in names))
    print(f"{len(cases)} cases, corpus {tally[VERSIONS[0]]['total']} strings -> {out}")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "results")
