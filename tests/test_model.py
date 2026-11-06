import itertools
import json
import unittest
from pathlib import Path

from rust_bat_args_model.checker import check
from rust_bat_args_model.cli import encode_both, main
from rust_bat_args_model.encoders import PREFIX, Arg, EncodeError, make_bat_command_line

ROOT = Path(__file__).resolve().parent.parent
CASES = [json.loads(x) for x in (ROOT / "fixtures/cases.jsonl").read_text().splitlines() if x]
EXP = json.loads((ROOT / "fixtures/expected.json").read_text())


def got(c):
    r = encode_both(c["script"], [Arg(a["value"], a["raw"]) for a in c["args"]], c["force_quotes"])
    return [x["cmdline"] if x["ok"] else "ERR:" + x["error_kind"] for x in r.values()]


class Fixtures(unittest.TestCase):
    def test_count(self):
        self.assertEqual(len(CASES), 18)

    def test_hand_expectations(self):
        for c in CASES:
            self.assertEqual(got(c), EXP[c["id"]], c["id"])

    def test_cli(self):
        import contextlib
        import io
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.assertEqual(main(["hello world"]), 0)
        self.assertTrue(json.loads(buf.getvalue())["1.77.2"]["ok"])


class Encoder(unittest.TestCase):
    def test_prefixes(self):
        self.assertEqual(PREFIX["1.77.1"], 'cmd.exe /d /c "')
        self.assertEqual(PREFIX["1.77.2"], 'cmd.exe /e:ON /v:OFF /d /c "')

    def test_crlf_only_rejected_for_regular_args_in_1772(self):
        with self.assertRaises(EncodeError):
            make_bat_command_line("1.77.2", "t.bat", [Arg("a\nb")])
        # raw_arg goes through append_arg, which does not check CR/LF
        self.assertIn("\n", make_bat_command_line("1.77.2", "t.bat", [Arg("a\nb", raw=True)]))

    def test_script_trailing_nul_stripped(self):
        self.assertEqual(make_bat_command_line("1.77.2", "t.bat\0", []), PREFIX["1.77.2"] + '"t.bat""')

    def test_backslash_counts(self):
        # 1.77.2: n extra backslashes before an internal quote (2n total),
        # the doubled quote, the closing quote and the outer closing quote.
        for n in range(4):
            line = make_bat_command_line("1.77.2", "t.bat", [Arg("\\" * n + '"')])
            self.assertTrue(line.endswith(' "' + "\\" * (2 * n) + '""""'), (n, line))
        # 1.77.1: 2n+1 backslashes before an internal quote (unquoted arg)
        for n in range(4):
            line = make_bat_command_line("1.77.1", "t.bat", [Arg("\\" * n + '"')])
            self.assertTrue(line.endswith(" " + "\\" * (2 * n + 1) + '""'), (n, line))

    def test_percent_always_gets_hack_in_1772(self):
        for s in ["%", "a%b", "%%", "%x%"]:
            line = make_bat_command_line("1.77.2", "t.bat", [Arg(s)])
            self.assertEqual(line.count("%%cd:~,"), s.count("%"))


class CheckerModel(unittest.TestCase):
    """Claims about OUR checker, never about cmd.exe."""

    def test_real_behaviour_is_always_unknown(self):
        for c in CASES:
            for x in encode_both(c["script"], [Arg(a["value"], a["raw"]) for a in c["args"]], c["force_quotes"]).values():
                if x["ok"]:
                    self.assertEqual(x["check"]["real_cmd_behaviour"], "UNKNOWN")
                    self.assertNotIn("safe", x["check"]["model_status"])

    def test_1771_quote_amp_flagged(self):
        c = check(make_bat_command_line("1.77.1", "test.bat", [Arg('"&echo X')]))
        self.assertEqual(c["model_status"], "findings_in_model")

    def test_raw_arg_flagged_in_both(self):
        for v in PREFIX:
            self.assertEqual(check(make_bat_command_line(v, "t.bat", [Arg("&x", raw=True)]))["model_status"], "findings_in_model")

    def test_1772_regular_args_no_hard_findings_on_small_corpus(self):
        alpha = 'a\\"&%^ |<>()!'
        for p in itertools.product(alpha, repeat=3):
            s = "".join(p)
            c = check(make_bat_command_line("1.77.2", "t.bat", [Arg(s)]))
            self.assertNotEqual(c["model_status"], "findings_in_model", repr(s))
            self.assertFalse(c["ends_in_quotes"], repr(s))

    def test_1771_has_hard_findings_on_same_corpus(self):
        alpha = 'a\\"&%^ |<>()!'
        n = sum(check(make_bat_command_line("1.77.1", "t.bat", [Arg("".join(p))]))["model_status"] == "findings_in_model"
                for p in itertools.product(alpha, repeat=3))
        self.assertGreater(n, 0)


if __name__ == "__main__":
    unittest.main()
