"""A deliberately simplified quote-state checker. THIS IS OUR MODEL, NOT cmd.exe.

Steps (each an interpretation, documented in LIMITATIONS.md):
 1. Take the text after the ``/c `` switch. Per the Microsoft ``cmd`` page,
    when the "preserve quotes" conditions are not met and the first
    character is a quote, it "is stripped along with the closing quotation
    mark"; we read that closing mark as the *last* quote in the string.
 2. Toggle an in-quotes flag on every ``"``; nothing else escapes a quote.
 3. Report metacharacters ``& | < > ( ) ^`` seen outside quotes, ``%``
    anywhere (Rust's own comments say ``%VAR%`` is expanded), and CR/LF.
 4. ``%`` preceded by ``%%cd:~,`` is reported as neutralised-by-hack with
    status UNKNOWN: its effect depends on cmd variable substring expansion,
    which is described only in the Rust source comment and is not modelled.

The checker never reports "safe". Its strongest statement is
``no_findings_in_model`` and real cmd behaviour is always ``UNKNOWN``.
"""
from __future__ import annotations

from .encoders import HACK

META_OUTSIDE = set("&|<>()^")


def check(cmdline: str) -> dict:
    i = cmdline.find("/c ")
    rest = cmdline[i + 3:] if i >= 0 else cmdline
    stripped_outer = False
    if rest.startswith('"') and rest.count('"') >= 2:
        last = rest.rfind('"')
        rest = rest[1:last] + rest[last + 1:]
        stripped_outer = True
    hack_pos: set[int] = set()
    hack_end: set[int] = set()
    k = rest.find(HACK + "%")
    while k >= 0:
        hack_pos.update(range(k, k + len(HACK) + 1))
        hack_end.add(k + len(HACK))
        k = rest.find(HACK + "%", k + len(HACK) + 1)
    findings = []
    inq = False
    for pos, ch in enumerate(rest):
        if ch == '"':
            inq = not inq
        elif ch in META_OUTSIDE and not inq:
            findings.append({"pos": pos, "char": ch, "kind": "metachar_outside_quotes"})
        elif pos in hack_end:  # the original '%' that ends a hack span
            findings.append({"pos": pos, "char": ch, "kind": "percent_hack_UNKNOWN"})
        elif pos in hack_pos:
            pass
        elif ch == "%":
            findings.append({"pos": pos, "char": ch, "kind": "percent_expansion_possible"})
        elif ch in "\r\n":
            findings.append({"pos": pos, "char": repr(ch), "kind": "line_break"})
    hard = [f for f in findings if f["kind"] != "percent_hack_UNKNOWN"]
    if hard:
        status = "findings_in_model"
    elif findings:
        status = "only_unknown_in_model"
    else:
        status = "no_findings_in_model"
    return {"stripped_outer_quotes": stripped_outer, "after_strip": rest, "ends_in_quotes": inq,
            "findings": findings, "model_status": status, "real_cmd_behaviour": "UNKNOWN"}
