# Limitations

- **The checker is our model, not cmd.exe.** Each step is an interpretation:
  outer-quote stripping reads "the closing quotation mark" in the Microsoft
  page as the last quote; only `"` toggles quoting; `^` escaping, delayed
  expansion, `for` variables, `call` re-parsing and how the batch script
  itself uses `%1`/`%~1` are **not** modelled. `real_cmd_behaviour` is
  always `UNKNOWN`.
- **No universal-escaping claim.** Zero findings in the checker on the
  corpus for 1.77.2 says nothing about cmd.exe in general. Rust's advisory
  states no complete escaping was found and std returns InvalidInput where
  it cannot escape safely.
- The `%%cd:~,%` hack relies on cmd substring expansion with extensions
  enabled (`/e:ON`), as explained only in the Rust source comment. The model
  reports it as `percent_hack_UNKNOWN`.
- Strings are Python `str`; Rust works on WTF-8 / UTF-16. Lone surrogates
  are skipped when deciding on quotes, as `to_char()` returns `None`; other
  encoding effects are not modelled.
- Not ported: how std decides a program is a batch file, path resolution,
  `to_user_path`, and non-batch `make_command_line`.
- No Windows run was done. Expected strings were derived by hand from the
  Rust source and compared with the port; that is all the evidence.
- CI configuration is included; at the time of the local commit it had only
  been run locally, not on a hosted runner.
