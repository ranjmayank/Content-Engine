# Content Engine — working rules

**Not set up yet?** If `engine.config.json` doesn't exist, run the `engine-setup` skill (or `python3 setup/init.py`) before any content task. Setup rewrites this file with your niche's rules.

- Read `engine.config.json` at the start of any content task: brand, author, pillars, audience, voice, cadence, integrations.
- Stay inside `niche.pillars`; never cover `niche.out_of_scope`.
- Propose the topic first and wait for approval before writing; one topic at a time, covered across formats.
- Build from current, dated sources (`scanner/sources/digests/`), and check `analytics/opportunities.json` and `seo-audit/reports/latest.md` first.
- Never invent numbers. Every figure needs a dated source; site numbers need their date window.
- Don't publish, schedule, send or change site settings without an explicit go-ahead.
- Skills live in `.claude/skills/`; docs in `docs/`.
