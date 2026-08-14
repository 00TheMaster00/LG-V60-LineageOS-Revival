# Contributing

Contributions are welcome when they improve reproducibility, compatibility or
evidence quality without weakening the safety boundary.

Before opening a pull request:

1. run `python tools/audit_public_release.py`;
2. run `python tools/check_markdown_links.py`;
3. run `python -m unittest discover -s DIY/06-LG-Camera/tests -v` when
   touching Camera tooling;
4. run `python -m unittest discover -s DIY/01-Recovery-Backup/tests -v` when
   touching recovery tooling;
5. run `bash DIY/05-Performance-Kernel/workflow/tests/syntax-check.sh` when
   touching kernel/profile tooling;
6. regenerate `SHA256SUMS.txt` with
   `python tools/generate_release_manifest.py`;
7. state the exact V60 variant, ROM and vendor baseline tested;
8. classify every claim as proven, observed, inferred or untested; and
9. do not attach proprietary applications, firmware or private partitions.

Failed approaches are valuable when they include a clear hypothesis, exact
change, result and rollback. Do not present experimental kernel/fingerprint
patches as fixes without a completed physical enrollment test.
