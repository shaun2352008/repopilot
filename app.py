"""RepoPilot - Milestone 2: fetch GitHub issues, then let Gemini label and prioritise them."""

import json
import os

import pandas as pd
import requests
import streamlit as st

# If the AI step errors with "model not found", change this to another model
# name listed at https://ai.google.dev/gemini-api/docs/models
MODEL = "gemini-2.5-flash"
MAX_ISSUES = 30

st.set_page_config(page_title="RepoPilot", page_icon="🧭", layout="wide")
st.title("🧭 RepoPilot")
st.caption("AI issue-triage dashboard for GitHub repos")

# ---------- Sidebar: API key ----------
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input(
        "Gemini API key",
        type="password",
        value=os.environ.get("GEMINI_API_KEY", ""),
        help="Get a free key from Google AI Studio. It is never saved to GitHub.",
    )


# ---------- Helper functions ----------
def parse_repo(url: str):
    """Turn 'https://github.com/owner/repo' into ('owner', 'repo')."""
    parts = url.strip().rstrip("/").replace("https://github.com/", "").split("/")
    if len(parts) < 2 or not parts[0] or not parts[1]:
        return None
    return parts[0], parts[1]


def fetch_issues(owner: str, repo: str, limit: int = MAX_ISSUES):
    """Fetch open issues (not pull requests) using the GitHub API."""
    api = f"https://api.github.com/repos/{owner}/{repo}/issues"
    resp = requests.get(api, params={"state": "open", "per_page": limit}, timeout=15)
    resp.raise_for_status()
    issues = [i for i in resp.json() if "pull_request" not in i]
    return [
        {
            "number": i["number"],
            "title": i["title"],
            "body": (i["body"] or "")[:1000],
            "author": i["user"]["login"],
            "comments": i["comments"],
            "created": i["created_at"][:10],
            "url": i["html_url"],
        }
        for i in issues
    ]


def classify_issues(issues, api_key: str):
    """Send all issues to Gemini in ONE request and get back label, priority, summary."""
    items = [
        {"number": i["number"], "title": i["title"], "body": i["body"][:500]}
        for i in issues
    ]
    prompt = (
        "You are a triage assistant for a GitHub repository. For each issue below, return:\n"
        '- "label": one of bug, feature, question, docs\n'
        '- "priority": one of high, medium, low (high = breaks things for many users or '
        "security; low = minor or cosmetic)\n"
        '- "summary": one short sentence (max 15 words)\n\n'
        "Respond ONLY with a JSON array, one object per issue, with keys: "
        '"number", "label", "priority", "summary".\n\n'
        f"Issues:\n{json.dumps(items)}"
    )
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
    resp = requests.post(
        url,
        headers={"x-goog-api-key": api_key, "Content-Type": "application/json"},
        json={
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseMimeType": "application/json", "temperature": 0.2},
        },
        timeout=90,
    )
    resp.raise_for_status()
    text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
    text = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return {r["number"]: r for r in json.loads(text)}


# ---------- Step 1: fetch ----------
repo_url = st.text_input("GitHub repo URL", placeholder="https://github.com/streamlit/streamlit")

if st.button("Fetch issues", type="primary"):
    parsed = parse_repo(repo_url)
    if not parsed:
        st.error("Please enter a URL like https://github.com/owner/repo")
    else:
        try:
            with st.spinner("Fetching issues..."):
                st.session_state["issues"] = fetch_issues(*parsed)
                st.session_state["repo"] = f"{parsed[0]}/{parsed[1]}"
                st.session_state.pop("df", None)  # clear old AI results
        except requests.HTTPError as e:
            st.error(f"GitHub API error: {e}. The repo may not exist, or you hit the rate limit.")
        except requests.RequestException as e:
            st.error(f"Network error: {e}")

# ---------- Step 2: AI labelling ----------
issues = st.session_state.get("issues")
if issues is not None:
    if not issues:
        st.info("No open issues found in this repo. Try a busier one.")
    else:
        st.success(f"Fetched {len(issues)} open issues from {st.session_state['repo']}")

        if st.button("✨ Analyse with AI"):
            if not api_key:
                st.error("Paste your Gemini API key in the sidebar first.")
            else:
                try:
                    with st.spinner("Gemini is reading the issues..."):
                        results = classify_issues(issues, api_key)
                    rows = []
                    for i in issues:
                        r = results.get(i["number"], {})
                        rows.append(
                            {
                                "number": i["number"],
                                "title": i["title"],
                                "label": r.get("label", "unknown"),
                                "priority": r.get("priority", "unknown"),
                                "summary": r.get("summary", ""),
                                "comments": i["comments"],
                                "created": i["created"],
                                "url": i["url"],
                            }
                        )
                    st.session_state["df"] = pd.DataFrame(rows)
                except requests.HTTPError as e:
                    st.error(
                        f"Gemini error: {e}. Check your API key, the MODEL name at the top "
                        "of app.py, or wait a minute if you hit the free-tier limit."
                    )
                except (KeyError, IndexError, json.JSONDecodeError):
                    st.error("The AI reply was not in the expected format. Click Analyse again.")

        if "df" in st.session_state:
            st.subheader("AI-triaged issues")
            st.dataframe(st.session_state["df"], use_container_width=True)
        else:
            st.subheader("Raw issues")
            st.dataframe(pd.DataFrame(issues).drop(columns=["body"]), use_container_width=True)
