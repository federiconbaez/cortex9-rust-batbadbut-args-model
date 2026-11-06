# Sources

Local copies under `security-research-45/sources/next/` (not in this repo):

| Source | Used for | SHA-256 of copy |
|---|---|---|
| rust-lang/rust `library/std/src/sys/pal/windows/args.rs` at tag 1.77.1 | 1.77.1 encoder | f38fdbaec1077f82ade1fc7a91894dd7e07ce2cbe289b8c11cc23a3e600d5b75 |
| same file at tag 1.77.2 | 1.77.2 encoder, yt-dlp hack comment | 8adbff8b7996e5c54a8fc66807728d15ec06a416b112fb9125f16cd1c6fcece1 |
| Rust security advisory CVE-2024-24576 (blog.rust-lang.org, 2024-04-09) | scope, "all cases" statement, raw_arg, InvalidInput | 61b29cf6359b0661c35614a3b7bf624152ee0f8ff18a4df6753d0ba24c27be7d |
| "Announcing Rust 1.77.2" (blog source) | affected platforms | 6438ff7f9489b13cd0cb24293524273b7ea232a5ca32849dd13513a60b4fcce5 |
| Microsoft Learn, `cmd` command page | outer-quote stripping rule used by the checker | 2e70a8561baa1af81a44bd7dbbfb7176236954f9ebd5df1487356afe1db6c61c (page changes over time) |
