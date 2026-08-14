# Security Policy

Do not open a public issue containing a partition image, QCN, IMEI, phone
number, ADB serial, token, signing key or private log. Remove the attachment
from the Internet first if one was uploaded accidentally.

For ordinary compatibility bugs, use the issue template and provide only
sanitized evidence. This project cannot repair or alter IMEI and will not
accept foreign identity/calibration images.

## Repository and supply-chain reports

Security-sensitive reports include:

- a credential, private key or personal/device identifier committed to Git;
- a public artifact whose published SHA-256 does not match;
- a workflow or script that can write outside its documented target;
- a dependency-confusion, archive-extraction or path-traversal weakness;
- a camera builder bypass that promotes an unverified input/output;
- a recovery tool that can select an ambiguous partition or device; and
- a mirror or account impersonating an official `00TheMaster00` release.

Use GitHub private vulnerability reporting when it is enabled for the
canonical repository. Until then, do not publish an exploit, credential or
private device artifact merely to prove the report. Open a minimal public
issue asking the maintainer for a private contact channel, without including
the sensitive details.

## Supported security scope

The current `main` branch is the supported public documentation/tooling
release. Proprietary APKs, firmware packages, firehose binaries, prebuilt boot
images, forks and third-party mirrors are outside the supported supply chain.

Read [SUPPLY-CHAIN.md](SUPPLY-CHAIN.md) for verification and repository-
hardening guidance. The only canonical maintainer is
[@00TheMaster00](https://github.com/00TheMaster00).

## If sensitive material was committed

1. restrict or remove public access immediately;
2. revoke/rotate any credential or key;
3. record the affected commit and download exposure privately;
4. remove the material from the current tree;
5. coordinate history rewriting when required; and
6. re-run the public-data audit on the complete replacement history.

Deleting a file in a later commit does not remove it from earlier Git history.
