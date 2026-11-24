# Start here — set up Content Engine in your browser

**No coding, nothing to install.** Everything below happens on github.com (and, in Part 2, in your Google and Bing accounts). Do Part 1 today; Parts 2 and 3 whenever you're ready.

| Part | What you get | Time | Needed? |
|---|---|---|---|
| **[1. Get it running](#part-1--get-it-running-15-minutes)** | Daily news for your niche + a weekly SEO check of your site | 15 min | ✅ Yes |
| **[2. Connect your data and email](#part-2--connect-your-data-and-email-30-minutes)** | Your Google/Bing search numbers, a daily report and email | 30 min | Recommended |
| **[3. Write with Claude](#part-3--write-with-claude-10-minutes)** | Blog posts, LinkedIn posts, Reels and a daily topic list | 10 min | Recommended |

**You need:** a free GitHub account (github.com/signup) and the address of your website or blog. That's all for Part 1.

<details>
<summary><b>New to GitHub? 6 words you'll see (click to open)</b></summary>

| Word | What it means here |
|---|---|
| **Repository (repo)** | Your copy of Content Engine — a folder of files that lives on GitHub |
| **Actions** | GitHub's free robot that runs the engine's jobs on a schedule. It's a tab at the top of your repo |
| **Workflow** | One of those jobs, e.g. "Daily fuel scan". You can start any of them by hand with **Run workflow** |
| **Secret** | A password or key you give GitHub so the jobs can use it. Nobody — not even you — can read it again after saving |
| **Variable** | Like a secret, but not hidden (e.g. your site address) |
| **Commit** | A saved change. The jobs commit their reports, so new files appear in your repo by themselves |
</details>

---

## Part 1 — Get it running (15 minutes)

### Step 1. Make your own copy

1. Open **https://github.com/ranjmayank/Content-Engine** (sign in to GitHub first).
2. Click the green **Use this template** button (top right) → **Create a new repository**.
3. **Repository name:** anything, e.g. `my-content-engine`.
4. Choose **Private** (recommended — your search numbers will be stored in it).
5. Click **Create repository**.

✔️ **You should see:** your new repo, with the same files, under your own name.

### Step 2. Run the setup form

1. In **your** repo, click the **Actions** tab (top of the page).
   - If you see a green button saying *"I understand my workflows, go ahead and enable them"*, click it.
2. In the list on the left, click **1 · Set up my engine**.
3. On the right, click the grey **Run workflow** button. A form opens. Fill it in:

   | Box | What to type | Example |
   |---|---|---|
   | Your brand or blog name | What your readers know you as | `Growth Notes` |
   | Your website address | Where your blog posts live | `growthnotes.com` |
   | Your name | Your author name | `Sam Lee` |
   | Your niche | Pick the closest one — you can fine-tune later | `b2b-saas — B2B SaaS growth` |
   | Where are you? | Your country or city | `India`, `London`, `New York` |
   | One line about what you do | Optional | `runs marketing at a SaaS company` |
   | Language | The language you write in | `English` |
   | Websites you read | Optional — news sites or blogs in your niche, separated by commas | `saastr.com, lennysnewsletter.com` |

4. Click the green **Run workflow** button at the bottom of the form.
5. Wait about a minute and refresh the page. A run appears with a yellow dot (running), then a **green tick ✅**.
6. Click the run, then **Summary**: it shows what was set up.

✔️ **You should see:** new files in your repo's **Code** tab — `engine.config.json` (your settings) and images in `brand/`. The setup also **starts your first news scan and SEO audit** automatically.

> ❌ **Red cross instead?** Click the run → the red step → read the last lines. The most common causes are a typo in the website address or the niche, and there's a fix in [troubleshooting](troubleshooting.md). You can always just run the form again.

### Step 3. See your first results (wait 5–10 minutes)

In the **Actions** tab, wait until **Daily fuel scan** and **Weekly SEO audit** both show a green tick. Then, in the **Code** tab, open:

| File | What it is |
|---|---|
| `scanner/sources/digests/` → the newest file | Today's news in your niche, best stories first, each with a summary, numbers and a link |
| `seo-audit/reports/latest.md` | Your site's score out of 100 and a "Fix these first" list in plain words |
| `scanner/sources/SOURCES.md` | Which news sources worked (🟢) and which didn't (🔴) |
| `brand/` | Starter profile picture, banners and a quote card in your colours |

To open a file: click the folder, then the file name. GitHub shows it formatted.

### Step 4. Check your setup

**Actions** → **2 · Check my setup** → **Run workflow** → **Run workflow**. Open the finished run → **Summary**. You'll get a checklist like this:

| | Item | To do |
|---|---|---|
| ✅ | Settings | |
| ✅ | News digest | |
| ✅ | SEO audit | |
| ⬜ | Google key | START-HERE.md → Part 2, step A |

It ends with **"Do this next"** — the single next step — and a table of **when your daily jobs run** in your timezone. The defaults work; if you'd like the email at a different time, the table shows the one line to change. Run it whenever you're unsure where you are.

**🎉 Part 1 is done.** From now on, the news scan runs every morning and the SEO audit every Monday, on their own. You don't need to keep anything open.

---

## Part 2 — Connect your data and email (30 minutes)

Optional, but this is what makes the engine about **your** site: which searches already find you, which pages to fix, and a daily email.

### How to add a secret or a variable (you'll do this a few times)

1. In your repo: **Settings** tab (top right) → in the left menu **Secrets and variables** → **Actions**.
2. For a **secret**: stay on the **Secrets** tab → **New repository secret** → type the **Name** exactly as shown (capitals and underscores) → paste the value → **Add secret**.
3. For a **variable**: click the **Variables** tab → **New repository variable** → Name → Value → **Add variable**.

Never paste these into a chat, a file in the repo, or an email.

### A. Google Search Console and Google Analytics (20 minutes)

You'll create a free "robot account" in Google Cloud and give it **read-only** access to your Search Console and Analytics. You need: your site already in [Search Console](https://search.google.com/search-console) (and, optionally, in Google Analytics 4).

**A1. Create a project** — go to **console.cloud.google.com** (sign in with your Google account) → top-left project picker → **New project** → name it `content-engine` → **Create**. Make sure it's selected in the project picker.

**A2. Switch on two APIs** — in the search bar at the top type **Google Search Console API** → open it → **Enable**. Then search **Google Analytics Data API** → **Enable**.

**A3. Create the robot account** — menu (☰) → **IAM & Admin** → **Service accounts** → **+ Create service account** → name `content-engine` → **Create and continue** → skip the roles → **Done**.
✔️ You'll see it in the list with an email like `content-engine@your-project.iam.gserviceaccount.com`. **Copy that email.**

**A4. Download its key** — click the service account → **Keys** tab → **Add key** → **Create new key** → **JSON** → **Create**. A `.json` file downloads.
> ❌ *"Service account key creation is disabled"?* Your company's Google account blocks this. Use a project in a personal Google account instead — it can still read your site's data once you add it in A5.

**A5. Give it read access**
- **Search Console:** search.google.com/search-console → pick your site → **Settings** → **Users and permissions** → **Add user** → paste the robot email → Permission **Restricted** → **Add**. (Only an owner of the property can do this.)
- **Google Analytics (optional):** analytics.google.com → **Admin** (⚙️ bottom left) → under *Property*: **Property access management** → **+** → **Add users** → paste the robot email → Role **Viewer** → untick "Notify" → **Add**. While you're in Admin, open **Property details** and copy the **Property ID** (a number like `412345678`).

**A6. Tell GitHub** (see *How to add a secret* above):

| Type | Name | Value |
|---|---|---|
| Secret | `GOOGLE_SERVICE_ACCOUNT_JSON` | Open the downloaded `.json` file in Notepad (Windows) or TextEdit (Mac), select all, copy, paste — the whole thing, including `{` and `}` |
| Variable | `GSC_SITE_URL` | Your site **exactly as Search Console shows it** in the property picker: `sc-domain:example.com` for a Domain property, or `https://example.com/` (with the slash) for a URL-prefix property |
| Variable | `GA4_PROPERTY_ID` | The Property ID number (skip if you don't use GA4) |

**A7. Test it** — **Actions** → **Daily search & analytics pull** → **Run workflow**. After a green tick, open `analytics/reports/latest.md`: your clicks, the searches you're close to page 1 for, pages to fix, and visits from ChatGPT and other AI assistants.

Then delete the downloaded `.json` file from your computer (GitHub has it now).

### B. Bing Webmaster Tools (5 minutes, recommended)

Bing's search results also power Microsoft Copilot and ChatGPT search.

1. **bing.com/webmasters** → sign in → **Add site** → the quickest way is **Import from Google Search Console**.
2. **Settings** (⚙️ top right) → **API access** → **API key** → **Generate** → copy it.
3. In GitHub: secret `BING_API_KEY` = the key · variable `BING_SITE_URL` = your site as Bing lists it, e.g. `https://example.com/`.

### C. The daily email (5 minutes)

Every morning you'll get the day's ranked topics. With Gmail:

1. Turn on **2-Step Verification** for your Google account (myaccount.google.com → Security), if it isn't already.
2. Go to **myaccount.google.com/apppasswords** → name it `content engine` → **Create** → copy the 16-letter password.
3. In GitHub add:

| Type | Name | Value |
|---|---|---|
| Secret | `SMTP_HOST` | `smtp.gmail.com` |
| Secret | `SMTP_PORT` | `587` |
| Secret | `SMTP_USER` | your Gmail address |
| Secret | `SMTP_PASS` | the 16-letter app password (no spaces) |
| Variable | `MAIL_TO` | where to send it — your email (several: separate with commas) |

4. Test: **Actions** → **Daily topic email** → **Run workflow**. Check your inbox (and spam folder).

Not on Gmail? Any email provider's SMTP settings work — search "<your provider> SMTP settings".

**Then run "2 · Check my setup" again** — Part 2 should show ✅.

---

## Part 3 — Write with Claude (10 minutes)

The engine collects and ranks; **Claude writes**. The writing instructions ("skills") are in your repo, so Claude writes in your niche, voice and format.

### Option 1 — claude.ai (easiest)

1. Sign in at **claude.ai** → **Settings → Connectors** → connect **GitHub** and allow access to your repo.
2. Start a chat (or a Project), attach your repo from GitHub, and say: **"Read CLAUDE.md and engine.config.json, then plan my week."**
3. To use a skill everywhere without attaching the repo: download a skill folder from `.claude/skills/` and upload it under **Customize → Skills**.

### Option 2 — Claude Code (if you use a terminal)

Clone your repo and open the folder in Claude Code. The skills load automatically.

### Things to ask Claude

| Say | You get |
|---|---|
| "Finish setting up my engine" | It asks the rest: your bio, social handles, voice, colours, posting rhythm — and updates your settings |
| "Plan my week" | A scored list of ideas and a day-by-day content plan |
| "What should I write today?" | Today's best topics from your news and your data |
| "Write a blog post on topic 2" | Outline first, then a full SEO + AI-search optimised post |
| "Turn this post into LinkedIn posts and a carousel" | The full distribution set |
| "Make a reel from this post" | A script and production sheet (or a finished video) |
| "Review this draft before I publish" | Honest feedback with fixes |
| "Audit my site" / "How is my site doing?" | The audit and your data turned into 3–5 actions |
| "Are we cited in ChatGPT answers?" | An AI-visibility check |

### A daily topic list in your email (optional)

Pick one:
- **Claude API key** (simplest, a few cents a day): console.anthropic.com → **API keys** → create → in GitHub add the secret `ANTHROPIC_API_KEY`. The **Daily topic list (Claude API)** job then builds the list every morning before the email goes out.
- **A Claude scheduled task:** in Claude, create a daily scheduled task with the prompt from `.claude/skills/topic-list/SKILL.md`.

---

## Changing things later

| To change | Do this |
|---|---|
| Brand, site, niche, location, language | Run **1 · Set up my engine** again (your other settings are kept) |
| Bio, handles, voice, colours, times, channels, topics | Ask Claude: *"change my settings: …"* — or edit `engine.config.json` on GitHub (✏️ pencil icon → edit → **Commit changes**) |
| The times the daily jobs run | The setup run's **Summary** (and **2 · Check my setup**) has a table: open the file it names → ✏️ → change that one `cron` line → **Commit changes**. Or on your computer: `python3 setup/schedule.py` |
| Add news sites | Run **1 · Set up my engine** again with the sites in the last box, or ask Claude *"add these sources: …"* |
| Pause everything | **Actions** → pick a workflow → **•••** → **Disable workflow** |
| Get new features | [UPDATING.md](UPDATING.md) |

## Questions people ask

- **Does it cost anything?** Part 1 and 2 are free (GitHub Actions' free minutes cover it — about 150–300 of the 2,000 free minutes a month for a private repo). Claude needs a Claude plan or API credits.
- **Is my data safe?** Your repo is private if you chose Private. Secrets are encrypted and can't be read back. The robot account only has read access, and you can remove it any time in Search Console / Analytics.
- **My site is on Wix / Squarespace / Shopify / Webflow / WordPress — does it work?** Yes. The scan and audit only read your public pages; Search Console works for any site. Claude writes the posts; you paste them into your site (WordPress can get drafts directly — see [integrations](integrations.md)).
- **I don't have a website yet.** Parts 1 and 3 still work for news and social posts — use your LinkedIn or Instagram URL as the website, and the audit will simply have little to check.
- **It went wrong and I'm stuck.** Run **2 · Check my setup**, then see [troubleshooting.md](troubleshooting.md). Still stuck? Open an issue on the original repo with the step you're on and the red error message (never include secrets).

**Prefer the terminal?** [SETUP.md](SETUP.md) is the full command-line setup with every option.
