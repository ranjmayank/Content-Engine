# Security

**Report a vulnerability privately:** GitHub → this repo → **Security → Report a vulnerability** (a private advisory). Please don't open a public issue. You'll get a reply within 7 days.

## Keeping your own copy safe
- Secrets belong in GitHub Actions secrets, never in files, commits, issues or chats. See [docs/ACCESS.md](docs/ACCESS.md).
- Make your copy **private** if it stores Search Console, GA4 or Bing data — the analytics job commits it.
- If a key leaks, revoke it first, then replace it. Deleting the commit doesn't make a leaked key safe.
- The scanner and audit only fetch public pages. The audit respects robots.txt for its user agent `ContentEngine-Audit`.
- Workflows use the built-in `GITHUB_TOKEN` with write access to your repo only.

Supported version: the latest `main`.
