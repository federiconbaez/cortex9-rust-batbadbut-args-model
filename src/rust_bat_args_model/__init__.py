"""Offline, string-only re-implementation of the batch-file command-line
encoders in Rust std ``library/std/src/sys/pal/windows/args.rs`` at 1.77.1
(vulnerable, CVE-2024-24576) and 1.77.2 (fixed), plus a deliberately
simplified quote-state checker that is *this project's model*, not cmd.exe.

Nothing here spawns a process, calls cmd.exe or touches the filesystem.
"""
