# 🧭 RepoPilot

**An AI issue-triage dashboard for GitHub repositories.**
Paste the link to any public GitHub repo. RepoPilot fetches its open issues and uses Google's Gemini model to label each one, rate its priority, and summarise it in a single sentence.

**Live demo:** https://repopilot-shaun.streamlit.app/
<img width="1901" height="919" alt="Capture" src="https://github.com/user-attachments/assets/d925fe73-68ef-4c32-99d1-395e570d9050" />

---

## Table of Contents
1. [The Problem](#the-problem)
2. [What RepoPilot Does](#what-repopilot-does)
3. [How It Works](#how-it-works)
4. [Features and Status](#features-and-status)
5. [Getting Started](#getting-started)
6. [Using the App](#using-the-app)
7. [Project Structure](#project-structure)
8. [Tech Stack](#tech-stack)
9. [How GitHub Copilot Helped](#how-github-copilot-helped)
10. [Limitations](#limitations)
11. [Roadmap](#roadmap)
12. [Security Notes](#security-notes)

---

## The Problem

Popular open-source projects receive a constant stream of issues: bug reports, feature requests, questions, and documentation fixes. Maintainers have to read each one just to decide what it is and how urgent it is. This sorting ("triage") is slow, repetitive work, and it delays the issues that matter most.

## What RepoPilot Does

RepoPilot automates the first pass of triage. Given a public repository URL, it:

1. Fetches the repository's open issues (pull requests are excluded).
2. Sends them to the Gemini API in one batch.
3. Returns a table where every issue has:
   - a **label**: `bug`, `feature`, `question`, or `docs`
   - a **priority**: `high`, `medium`, or `low`
   - a **one-line summary**

This helps a maintainer see at a glance what needs attention first.

## How It Works

```
GitHub repo URL
      |
      v
GitHub REST API  -->  open issues (title, body, author, comments, date)
      |
      v
Gemini API  -->  label + priority + summary for each issue (JSON)
      |
      v
Streamlit dashboard  -->  triaged issue table
```

1. **Parse the URL.** The app extracts the owner and repo name from the link you paste.
2. **Fetch issues.** It calls the public GitHub API for up to 30 open issues and filters out pull requests.
3. **Classify with AI.** All issues are sent to Gemini in a single request, with instructions to answer only in JSON. Sending them together keeps the app fast and within free-tier rate limits.
4. **Display results.** The JSON reply is matched back to each issue by its number and shown in an interactive table. If the AI skips an issue, it appears as "unknown" instead of crashing the app.

## Features and Status

| Feature | Status |
|---|---|
| Fetch open issues from any public repo | Done |
| AI labelling (bug / feature / question / docs) | Done |
| AI priority rating (high / medium / low) | Done |
| One-line AI summaries | Done |
| Error handling (bad URL, GitHub rate limit, AI errors) | Done |
| Live deployment on Streamlit Community Cloud | Done |
| Filters and search | In progress |
| Charts (issues by label and priority) | In progress |
| Export report as CSV / Markdown | Planned |

## Getting Started

### Prerequisites
- Python 3.9 or newer
- A free Gemini API key from [Google AI Studio](https://aistudio.google.com)

### Run locally

```bash
git clone https://github.com/shaun2352008/repopilot.git
cd repopilot
pip install -r requirements.txt
python -m streamlit run app.py
```

Then open the local URL that Streamlit prints (usually http://localhost:8501).

### Provide your API key
Either paste the key into the **sidebar** of the running app, or set it as an environment variable before launching:

```bash
export GEMINI_API_KEY="your-key-here"
```

The key is never written to the code or committed to the repository.

### Changing the AI model
The model name is a single constant at the top of `app.py`:

```python
MODEL = "gemini-3.5-flash"
```

If Google renames or retires a model and you see a "404 Not Found" error, replace it with a current model name from the [Gemini models page](https://ai.google.dev/gemini-api/docs/models).

## Using the App

1. Paste a public repo URL, for example `https://github.com/streamlit/streamlit`.
2. Click **Fetch issues**. A table of raw open issues appears.
3. Click **✨ Analyse with AI**. After a few seconds, the table updates with label, priority, and summary columns.
4. Click any column header to sort, or open the issue link to read the original.

## Project Structure

```
repopilot/
├── app.py             # the whole app: fetching, AI classification, dashboard UI
├── requirements.txt   # Python dependencies
└── README.md
```

## Tech Stack

- **Python**
- **Streamlit** for the web interface
- **GitHub REST API** for issue data
- **Google Gemini API** for classification and summaries
- **pandas** for the results table
- **requests** for HTTP calls
- **GitHub Copilot** as a development assistant
- **Streamlit Community Cloud** for hosting

## Limitations

- Only the 30 most recent open issues are analysed per run, to stay within free API limits.
- Only the first 500 characters of each issue body are sent to the AI, so long issues may be summarised from partial text.
- AI labels and priorities are suggestions, not guarantees, and can be wrong. A human should review them.
- The free Gemini tier has rate limits, so heavy use may show a temporary error.
- GitHub's unauthenticated API allows a limited number of requests per hour.
- Public repositories only.

## Roadmap

- Filters by label and priority, plus keyword search
- Charts showing issue distribution
- CSV and Markdown report export
- Support for more than 30 issues with batching
- Optional GitHub token to raise API limits
- Tests for URL parsing and response handling

## Security Notes

- The Gemini API key is entered at runtime or stored as a secret on the hosting platform. It is never committed to this repository.
- If you fork this project, keep your own key out of the code and out of screenshots.

---

Built for Hacktoberfest Hack Day 2026 (VVCE Vector Flow Club), Track 2: AI Agents & Open-Source Development.
