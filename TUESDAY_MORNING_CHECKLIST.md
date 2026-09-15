# Tuesday Morning Weekly Update Checklist

**Goal:** Pull latest ESPN data, aggregate it, calculate playoff odds, and generate the weekly email for Pennoni league.

**Time needed:** ~5-10 minutes (mostly waiting for scripts to finish)

---

## Step-by-Step (Copy & Paste in Terminal)

### 1️⃣ Pull Latest Data from ESPN

```bash
python pipeline/ESPNWeeklyUpdate.py
```

**What it does:** Fetches this week's standings, matchups, and trades from ESPN
**Wait for:** "Done" message
**Typical time:** 2-3 minutes

---

### 2️⃣ Add This Week's Results

```bash
python pipeline/add_current_week_results.py
```

**What it does:** Scores this week's games and adds them to the master matchup file
**Wait for:** Completion message
**Typical time:** 1 minute

---

### 3️⃣ Rebuild Cross-League Data (Offline)

```bash
python pipeline/rebuild_aggregates.py
```

**What it does:** Reads all league workbooks and rebuilds the cross-league CSVs (no ESPN calls)
**Wait for:** "Done" message
**Typical time:** 1 minute
**Note:** This updates lifetime history and playoff data for ALL pages

---

### 4️⃣ Calculate Playoff Scenarios

```bash
python pipeline/playoff_chances.py --league "Pennoni Younglings"
```

**What it does:** Calculates % chance to make playoffs for each record next week
**Output:** `data/playoff_chances_by_week.csv`
**Typical time:** 2-3 minutes

---

### 5️⃣ Generate Email HTML

```bash
python pipeline/generate_weekly_email.py --league "Pennoni Younglings" --output email.html
```

**What it does:** Reads all the data above and creates a formatted HTML email
**Output:** `email.html` in your current directory
**Typical time:** < 1 minute

---

## Step 6️⃣: Send the Email

1. **Open** `email.html` in your browser (double-click the file)
2. **Select all** (Ctrl+A) and **copy** the styled content
3. **Go to Gmail** → **Compose**
4. **Paste** into the email body
5. **To:** Add the Pennoni league emails (set up a mail alias or distribution list)
6. **Subject:** `🏈 Pennoni Younglings - Week X Recap`
7. **Send** ✉️

---

## All-In-One Command

Run all scripts sequentially:

```bash
python pipeline/ESPNWeeklyUpdate.py && \
python pipeline/add_current_week_results.py && \
python pipeline/rebuild_aggregates.py && \
python pipeline/playoff_chances.py --league "Pennoni Younglings" && \
python pipeline/generate_weekly_email.py --league "Pennoni Younglings" --output email.html && \
echo "✅ All done! Open email.html to preview."
```

---

## Troubleshooting

| Issue                   | Fix                                                   |
| ----------------------- | ----------------------------------------------------- |
| "No matchup data found" | Run`ESPNWeeklyUpdate.py` first                      |
| Email looks plain       | Copy/paste the HTML into Gmail's rich editor          |
| ESPN credentials error  | Check that credentials.py has valid S2 tokens         |
| File not found errors   | Make sure you're running from the repo root directory |

---

## Optional: Email Customization

Edit `pipeline/generate_weekly_email.py` to:

- Change league name or colors
- Add more insights (boom/bust players, trade recommendations)
- Include standings for other leagues
- Add team-specific commentary

---

## Next Steps

Once you test this on Tuesday:

- Set up a **Gmail distribution list** for league members (e.g., `pennoni-league@googlegroups.com`)
- Schedule the scripts to run automatically (Windows Task Scheduler, or `cron` on Mac/Linux)
- Automate email sending (Python SMTP or Mailgun)

---

**Questions?** Check the script headers for detailed documentation.
