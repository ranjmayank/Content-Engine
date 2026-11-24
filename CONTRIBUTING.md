# Contributing

Thanks for helping. The most useful contributions:

1. **Tested source lists for a niche preset.** Run the scanner for a week, keep only 🟢 sources, and add `setup/presets/<niche>.sources.json` (and `"sources_file"` in the preset).
2. **New niche presets** — pillars with a clear `covers` line, keywords tuned on real digests, hashtags.
3. **Audit checks** — add the issue to `seo-audit/issues.py` (severity, title, why, fix) and the check in `seo-audit/audit.py`; add a page that triggers it to `tests/fixture-site/`.
4. **Skill improvements** — keep skills niche-neutral: read values from `engine.config.json` instead of naming a brand.

## Ground rules

- Standard library only for the scanner, audit and tools (they must run on a bare GitHub runner). `analytics/fetch.py` may use `google-auth` and `requests`; brand scripts may use Pillow.
- Never commit personal data: no `engine.config.json`, analytics exports, digests or reports from your own site. `.gitignore` in the template excludes the private ones; check `git status` before you push.
- Run the tests: `bash tests/run.sh`.
- Plain, specific writing in docs and skills. No hype.

## Pull requests

Describe what changed and how you tested it. One topic per PR.
