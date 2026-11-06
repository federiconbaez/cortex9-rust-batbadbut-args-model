# cortex9-rust-batbadbut-args-model

[Español](README.es.md) · [Practice guide](PRACTICE.md)

A pure-Python, string-only port of how Rust's standard library builds the
`cmd.exe` command line when `std::process::Command` runs a Windows batch
file, in **1.77.1** (vulnerable, CVE-2024-24576 "BatBadBut") and **1.77.2**
(fixed), plus a deliberately simplified quote-state checker.

**Nothing here runs a process, calls cmd.exe or touches Windows.** The
encoders produce strings; the checker is **this project's model**, not
cmd.exe. Real cmd behaviour is always reported as `UNKNOWN`. Rust's own
advisory says: "Due to the complexity of cmd.exe, we didn't identify a
solution that would correctly escape arguments in all cases." This project
does **not** promise universal escaping. See [LIMITATIONS.md](LIMITATIONS.md).

## What is ported, and from where

`library/std/src/sys/pal/windows/args.rs` at tags 1.77.1 and 1.77.2:

| Rule | 1.77.1 | 1.77.2 | Code |
|---|---|---|---|
| Prefix | `cmd.exe /d /c "` | `cmd.exe /e:ON /v:OFF /d /c "` | `PREFIX` |
| Script name | quoted; error if it contains `"` or ends in `\` | same | `_script` |
| When an arg is quoted | any of ``\t &()[]{}^=;!'+,`~%\|<>`` (or space/tab/empty) | empty, ends in `\`, any ASCII not alphanumeric and not in `#$*+-./:?@\_`, or any Unicode control char | `make_bat_command_line`, `append_bat_arg` |
| Internal `"` | n+1 backslashes added (2n+1 total), MSVCRT style | n backslashes added (2n total) and the quote doubled | `append_arg` / `append_bat_arg` |
| `%` | quoted only | `%` → `%%cd:~,%` ("yt-dlp hack") | `HACK` |
| CR / LF in a regular arg | passed through | InvalidInput "batch file arguments are invalid" | `make_bat_command_line` |
| NUL | InvalidInput | InvalidInput | `ensure_no_nuls` |
| `raw_arg` | as-is | as-is (still through `append_arg`) | `Arg(raw=True)` |

The checker (`checker.py`) strips the outer `/c "…"` quotes following the
Microsoft `cmd` page (reading "the closing quotation mark" as the last one),
toggles an in-quotes flag on every `"`, and reports `& | < > ( ) ^` outside
quotes, any `%`, and CR/LF. A `%` inside the 1.77.2 hack is reported as
`percent_hack_UNKNOWN`.

## Run

```sh
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m rust_bat_args_model '"&echo X' 'hello world'
python3 scripts/gen_results.py /tmp/out && diff -r results /tmp/out
```

## Results (from `results/`)

- All 18 fixture cases match command lines derived by hand from the Rust
  source (`fixtures/expected.json`).
- `corpus_tally.csv`, 37777 strings (all 2-character printable ASCII plus
  all 4-character strings over ``a\"&%^ |<>()!``), checker on each:
  1.77.1 has 11565 with findings in the model and 7150 that end inside
  quotes; 1.77.2 has 0 of either, and 8016 whose only finding is the hack
  (`UNKNOWN`).
- That is a statement about **this checker on this corpus**, not a proof
  that 1.77.2 output is safe in cmd.exe.
- `raw_arg` input is flagged in both versions: std leaves it to the caller.

Licence: Apache-2.0.
