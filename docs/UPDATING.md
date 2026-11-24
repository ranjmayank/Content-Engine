# Getting updates

Copies made with **Use this template** don't receive later improvements automatically. Pull them from the original repo as `upstream` — your settings and data are separate files, so updates don't touch them.

## One-time
```bash
git remote add upstream https://github.com/ranjmayank/Content-Engine.git
```

## Each update
```bash
git fetch upstream
git merge upstream/main --allow-unrelated-histories -m "Update Content Engine"   # first time needs --allow-unrelated-histories
python3 setup/init.py --migrate      # adds any new settings with their defaults; keeps yours
python3 setup/schedule.py            # re-applies your local times to the workflows
bash tests/run.sh
git push
```

Read [CHANGELOG.md](../CHANGELOG.md) first for anything that needs action.

## What's yours vs what's the engine's

| Yours — updates never change these | The engine's — updates replace these |
|---|---|
| `engine.config.json`, `scanner/sources/*.json` and digests, `analytics/data/`, `analytics/reports/`, `seo-audit/reports/`, `content/`, `tracker/`, `brand/*.png`, `style.md`, `CLAUDE.md` (written by setup) | `scanner/fuel_scanner.py`, `analytics/*.py`, `seo-audit/*.py`, `setup/`, `tools/`, `.claude/skills/`, `docs/`, `.github/workflows/` |

**Merge conflicts:**
- In `.github/workflows/*.yml` it's usually the `cron:` line — take the upstream version, then run `python3 setup/schedule.py`.
- In a skill you customised: keep your version, or move your changes into `style.md` → "Standing notes" / `CLAUDE.md` so future updates merge cleanly.
- `CLAUDE.md` / `style.md`: keep yours (`git checkout --ours CLAUDE.md style.md`).

**Forks** can also use GitHub's **Sync fork** button.
