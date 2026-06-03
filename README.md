# ProblemBase

A search engine for unsolved software problems — built because customer discovery is broken.

---

## The Problem I Was Trying to Solve

Every builder I've talked to goes through the same painful loop.

They have an idea. They spend weeks on customer discovery — Reddit threads, Twitter searches, App Store reviews, GitHub issues — manually reading through hundreds of posts trying to answer one question: *is this problem real enough to build for?*

The data they need already exists. Millions of users document their frustrations with software every day, publicly, with timestamps and upvotes. But it's scattered across five different platforms with no structure. You can't search across it. You can't see which complaints are actually high-severity versus one-off edge cases. You can't tell if a problem is growing or shrinking over time.

So founders either skip the research entirely and build blind, or spend 40 hours doing it manually before writing a single line of code.

I built ProblemBase to fix that. You type a product name. It scrapes complaints from Hacker News and GitHub Issues, runs them through an LLM to cluster by theme and score by severity, and returns a structured breakdown of where the real pain is — in under 30 seconds.

---

## How It Works

```
User searches "Notion"
        ↓
FastAPI backend receives POST /search/
        ↓
Aggregator scrapes HackerNews + GitHub Issues in parallel
        ↓
Raw complaints sent to Groq (Llama 3.3 70B) for clustering
        ↓
LLM groups complaints into themes, scores severity, extracts insight
        ↓
Structured JSON response returned
        ↓
React frontend displays ranked problem clusters with sources
        ↓
Result cached in SQLite for 24 hours (same query = instant response)
```

The core insight behind the architecture: complaints aren't just text, they're signals. A GitHub issue with 5,000 reactions means something different from one with 3. Aggregating score alongside text and clustering by theme — rather than just keyword matching — surfaces the actual severity of each problem.

---

## Tech Stack

| Layer | Technology | Why |
|---|---|---|
| Backend | FastAPI | Async-first, typed, auto docs — right for AI pipelines |
| AI Analysis | Groq + Llama 3.3 70B | Fast inference, free tier, structured JSON output |
| Scraping | HackerNews Algolia API + GitHub REST API | Official APIs, reliable, no rate limit issues at this scale |
| Cache | SQLite | Zero infra, good enough for v1, easy to swap for Redis later |
| Frontend | React + Tailwind CSS | Fast to build, clean output |
| Build Tool | Vite | Fast HMR, zero config for React |

---

## Project Structure

```
problembase/
├── backend/
│   ├── main.py                  # FastAPI app, CORS, startup events
│   ├── config.py                # Pydantic settings, reads from .env
│   ├── routers/
│   │   └── search.py            # POST /search/ route
│   ├── scrapers/
│   │   ├── hackernews.py        # HN Algolia API scraper
│   │   └── github.py            # GitHub Issues scraper
│   ├── services/
│   │   ├── aggregator.py        # Combines scraper outputs, sorts by score
│   │   ├── analyzer.py          # Groq LLM clustering + severity scoring
│   │   └── cache.py             # SQLite read/write, 24hr TTL
│   ├── models/
│   │   ├── request.py           # SearchRequest schema
│   │   └── response.py          # SearchResponse, ProblemCluster, Complaint
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   └── App.jsx              # Search UI + results display
│   └── package.json
├── .env.example
└── README.md
```

---

## API Reference

### `POST /search/`

Scrapes complaints for a product and returns AI-clustered problem themes.

**Request**
```json
{
  "product": "Notion",
  "limit": 10
}
```

**Response**
```json
{
  "product": "Notion",
  "total_complaints": 35,
  "status": "success",
  "clusters": [
    {
      "theme": "Sync Issues",
      "severity": "high",
      "insight": "Users frequently lose work due to sync failures, particularly on mobile.",
      "complaint_count": 8,
      "complaints": [
        {
          "text": "...",
          "source": "hackernews",
          "url": "https://news.ycombinator.com/item?id=...",
          "score": 210
        }
      ]
    }
  ]
}
```

**Severity levels:** `critical` → `high` → `medium` → `low`

### `GET /health`

```json
{
  "status": "ok",
  "app": "ProblemBase",
  "version": "1.0.0"
}
```

Auto-generated interactive docs available at `/docs` when running locally.

---

## Running Locally

**Prerequisites:** Python 3.11+, Node.js 18+

**Backend**

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Copy and fill in your keys
cp .env.example .env

uvicorn main:app --reload
# → http://127.0.0.1:8000
# → http://127.0.0.1:8000/docs
```

**Frontend**

```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

**Required API Keys** (all free)

| Key | Where to get it |
|---|---|
| `GROQ_API_KEY` | console.groq.com |
| `GITHUB_TOKEN` | github.com/settings/tokens — only needs `public_repo` scope |

---

## Challenges and How I Dealt With Them

**The GitHub scraper returns noise.**
Searching "Notion issue" on GitHub returns issues from completely unrelated repos that happen to mention the word. The fix was sorting by reaction count — highly-reacted issues float to the top regardless of which repo they're from, and genuinely popular complaints tend to be relevant. It's not perfect, but it's good enough for v1 and it's honest in the README.

**LLM output is non-deterministic.**
The analyzer prompt returns JSON, but the model occasionally wraps it in markdown code fences or adds a preamble sentence. I added a stripping step before `json.loads()` and kept temperature at 0.3 to reduce variance. If parsing fails, the route returns a 500 with the raw model output so it's debuggable.

**First search is slow (15-20 seconds).**
Scraping two sources and then calling an LLM adds up. The cache layer (SQLite, 24hr TTL) solves this for repeat queries — second search is instant. For v1 this is acceptable. The right v2 fix is background job processing with a job ID so the frontend can poll for results instead of holding the connection open.

**Groq deprecated the model mid-build.**
`llama3-8b-8192` got decommissioned while I was building. Switched to `llama-3.3-70b-versatile`. Lesson: pin model versions in config, not hardcoded in service files.

---

## What This Is Not (Yet)

This is v1. It works, it's useful, and it's honest about its limitations.

- **No trend data.** The most valuable thing ProblemBase could eventually do is show complaint volume over time — a problem growing 3x in 6 months with no solution is a business opportunity. That requires storing historical scrape results, which needs a real database.

- **No Reddit.** Reddit's API now requires manual approval for new apps. HN and GitHub are better signal for software tools anyway — the audience is right — but Reddit would add volume.

- **Scraper noise.** GitHub search isn't scoped to the product's actual repository, so unrelated issues sometimes surface. A v2 fix is to first resolve the product to its official GitHub org, then search within that org only.

- **No auth or rate limiting.** Fine for a portfolio project. Not fine for production traffic.

- **SQLite → Redis in production.** The cache works but doesn't scale horizontally. Straightforward swap when needed.

---

## If I Were Building v2

Background job queue (Celery or FastAPI BackgroundTasks with Redis) so the frontend gets a job ID immediately and polls for completion — no more hanging HTTP connections during scraping.

Persistent complaint storage in PostgreSQL so trend lines become possible. The schema is simple: `(product, complaint_text, source, score, scraped_at)`.

Repository resolution — map product names to GitHub org/repo so scraping is scoped correctly.

---

## License

MIT
