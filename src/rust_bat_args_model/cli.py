"""rust-bat-args-model: encode one argument list with both std versions."""
from __future__ import annotations

import argparse
import json
import sys

from .encoders import Arg, EncodeError, make_bat_command_line
from .checker import check

VERSIONS = ("1.77.1", "1.77.2")


def encode_both(script: str, args: list[Arg], force_quotes: bool = False) -> dict:
    out = {}
    for v in VERSIONS:
        try:
            line = make_bat_command_line(v, script, args, force_quotes)
            out[v] = {"ok": True, "cmdline": line, "check": check(line)}
        except EncodeError as e:
            out[v] = {"ok": False, "error_kind": e.kind, "error": e.message}
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="rust-bat-args-model", description=__doc__)
    ap.add_argument("--script", default="test.bat")
    ap.add_argument("--force-quotes", action="store_true")
    ap.add_argument("--raw", action="append", default=[], help="argument passed as raw_arg")
    ap.add_argument("args", nargs="*")
    a = ap.parse_args(argv)
    args = [Arg(x) for x in a.args] + [Arg(x, raw=True) for x in a.raw]
    json.dump(encode_both(a.script, args, a.force_quotes), sys.stdout, indent=2, ensure_ascii=True)
    sys.stdout.write("\n")
    return 0
