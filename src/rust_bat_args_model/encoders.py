"""Pure-Python ports of make_bat_command_line / append_arg / append_bat_arg.

Inputs are Python ``str`` (one code point per element). Rust works on UTF-16
code units / WTF-8; for the ASCII-driven rules ported here the results are
the same, and the output is returned as ``str``.
"""
from __future__ import annotations

import unicodedata
from dataclasses import dataclass

PREFIX = {
    "1.77.1": 'cmd.exe /d /c "',
    "1.77.2": 'cmd.exe /e:ON /v:OFF /d /c "',
}
SPECIAL_1771 = "\t &()[]{}^=;!'+,`~%|<>"
UNQUOTED_1772 = r"#$*+-./:?@\_"
HACK = "%%cd:~,"


class EncodeError(Exception):
    """Mirrors io::ErrorKind::InvalidInput returned by std."""

    def __init__(self, kind: str, message: str):
        super().__init__(message)
        self.kind = kind
        self.message = message


@dataclass(frozen=True)
class Arg:
    value: str
    raw: bool = False  # CommandExt::raw_arg -> Arg::Raw


def ensure_no_nuls(s: str) -> None:
    if "\0" in s:
        raise EncodeError("nul", "nul byte found in provided data")


def append_arg(out: list[str], arg: Arg, force_quotes: bool) -> None:
    """append_arg (identical in 1.77.1 and 1.77.2)."""
    if arg.raw:
        quote_mode = "never"
    else:
        quote_mode = "always" if force_quotes else "auto"
    s = arg.value
    ensure_no_nuls(s)
    if quote_mode == "always":
        quote, escape = True, True
    elif quote_mode == "auto":
        quote, escape = (" " in s or "\t" in s or s == ""), True
    else:
        quote, escape = False, False
    if quote:
        out.append('"')
    backslashes = 0
    for ch in s:
        if escape:
            if ch == "\\":
                backslashes += 1
            else:
                if ch == '"':
                    out.append("\\" * (backslashes + 1))  # 2n+1 before internal "
                backslashes = 0
        out.append(ch)
    if quote:
        out.append("\\" * backslashes)  # 2n before closing "
        out.append('"')


def _is_control(ch: str) -> bool:
    # Rust char::is_control: general category Cc.
    return unicodedata.category(ch) == "Cc"


def append_bat_arg(out: list[str], s: str, quote: bool) -> None:
    """append_bat_arg (new in 1.77.2)."""
    ensure_no_nuls(s)
    if s == "" or s.endswith("\\"):
        quote = True
    for ch in s:
        if 0xD800 <= ord(ch) <= 0xDFFF:
            continue  # lone surrogate: code_points().to_char() is None
        ascii_needs_quotes = ord(ch) < 128 and not (ch.isascii() and ch.isalnum() or ch in UNQUOTED_1772)
        if ascii_needs_quotes or _is_control(ch):
            quote = True
    if quote:
        out.append('"')
    backslashes = 0
    for ch in s:
        if ch == "\\":
            backslashes += 1
        else:
            if ch == '"':
                out.append("\\" * backslashes)  # 2n before internal "
                out.append('"')  # doubling acts as escape
            elif ch in ("%", "\r"):
                out.append(HACK)  # yt-dlp hack
            backslashes = 0
        out.append(ch)
    if quote:
        out.append("\\" * backslashes)
        out.append('"')


def _script(out: list[str], script: str) -> None:
    out.append('"')
    if '"' in script or script.endswith("\\"):
        raise EncodeError("script_name", 'Windows file names may not contain `"` or end with `\\`')
    out.append(script[:-1] if script.endswith("\0") else script)
    out.append('"')


def make_bat_command_line(version: str, script: str, args: list[Arg], force_quotes: bool = False) -> str:
    if version not in PREFIX:
        raise ValueError(version)
    out = [PREFIX[version]]
    _script(out, script)
    for arg in args:
        out.append(" ")
        if version == "1.77.1":
            fq = force_quotes
            if not arg.raw and not force_quotes:
                fq = any(c in SPECIAL_1771 for c in arg.value)
            append_arg(out, arg, fq)
        else:
            if not arg.raw:
                if "\r" in arg.value or "\n" in arg.value:
                    raise EncodeError("crlf", "batch file arguments are invalid")
                append_bat_arg(out, arg.value, force_quotes)
            else:
                append_arg(out, arg, force_quotes)
    out.append('"')
    return "".join(out)
