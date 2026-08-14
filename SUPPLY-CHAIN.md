# Supply-Chain and Repository Security

This project handles boot tooling, source patches and a transformation of a
user-supplied proprietary application. Verify provenance before trusting any
command or artifact.

## Clone and repository identity

The canonical remote is:

```text
https://github.com/00TheMaster00/LG-V60-LineageOS-Revival.git
```

After cloning:

```bash
git remote -v
git status --short --branch
git log --show-signature -5
```

Historical commits may use the maintainer's former `The1-Master` GitHub
noreply identity. See [PROVENANCE.md](PROVENANCE.md). New official publication
should come from `00TheMaster00`.

## Verify the repository manifest

From the repository root:

```bash
python tools/generate_release_manifest.py --check
python tools/audit_public_release.py
python tools/check_markdown_links.py
```

`SHA256SUMS.txt` covers public release files while excluding Git internals and
the manifest itself. A passing manifest proves the working tree matches the
recorded file hashes; it does not independently authenticate the repository
owner, so begin from the canonical URL.

## Verify executable project components

Run the relevant tests before use:

```bash
python -m unittest discover -s DIY/06-LG-Camera/tests -v
python -m unittest discover -s DIY/01-Recovery-Backup/tests -v
python -m unittest discover -s tools/tests -v
bash DIY/05-Performance-Kernel/workflow/tests/syntax-check.sh
```

Read scripts before running them. No public script should contain a real
device serial, personal filesystem path, live sector coordinate or automatic
approval for a destructive write.

## Camera reconstruction trust model

The builder checks three independent identities:

1. exact stock input size and SHA-256;
2. exact binary-delta size and SHA-256; and
3. exact Candidate 24 output size and SHA-256.

Patching occurs in a temporary file and the final name is assigned only after
the output gate passes. Verify the resulting APK again with `apksigner` and
`zipalign`. The published signing-certificate hash identifies the project
certificate; it is not LG's production certificate.

Do not download a prebuilt “Candidate 24 APK” from a mirror merely because
the filename looks correct. Reconstruct locally from the exact owned stock
input and compare the final hash.

For source-level review, follow
[the local camera audit](DIY/06-LG-Camera/SOURCE-AUDIT.md). It validates exact
uncompressed APK-entry and normalized Smali hashes. Public CI exercises the
audit algorithms and a successful synthetic patch but cannot contain the
proprietary stock APK needed for a full Candidate 24 reconstruction.

## GitHub Actions boundary

The validation workflow declares:

```yaml
permissions:
  contents: read
```

This prevents the validation job's default token from writing repository
contents. Review every workflow change as security-sensitive because a person
with workflow-write permission can change what future automation executes.
Third-party Actions are pinned to immutable full commit SHAs; the adjacent
version comments are informational only.

Recommended repository settings for the canonical maintainer:

- restrict the Codex GitHub App to this selected repository rather than all
  present and future repositories;
- remove collaborators who no longer require write access;
- protect `main` with a ruleset requiring pull requests, Code Owner review and
  the `validate` status check;
- block force pushes and branch deletion;
- keep Actions' default token read-only and prevent Actions from approving
  pull requests;
- enable dependency alerts, secret scanning where available, and private
  vulnerability reporting; and
- protect the GitHub account with a passkey or hardware-backed 2FA and store
  recovery codes offline.

Repository rules and account security are enforced on GitHub, not by this
Markdown file. Verify them in repository/account settings.

## Release practice

For each public release:

1. merge a reviewed pull request into protected `main`;
2. require CI to pass on the exact merge commit;
3. create an annotated, preferably signed tag;
4. publish a release note that lists the commit and artifact SHA-256 values;
5. attach only redistributable artifacts; and
6. keep proprietary APKs, firmware, boot/partition images and private logs
   outside GitHub.

If a token, private key, phone partition, QCN, APK or personal log is committed,
remove public access, rotate/revoke the credential when applicable, preserve
incident evidence privately, and rewrite history only with a documented
coordination plan. Deleting the latest file does not remove it from earlier
Git history.
