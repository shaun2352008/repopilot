"""RepoPilot - Milestone 1: fetch open issues from a public GitHub repo and show them."""

import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="RepoPilot", page_icon="🧭", layout="wide")
st.title("🧭 RepoPilot")
st.caption("AI issue-triage dashboard for GitHub repos")


def parse_repo(url: str):
    """Turn 'https://github.com/owner/repo' into ('owner', 'repo')."""
    parts = url.strip().rstrip("/").replace("https://github.com/", "").split("/")
    if len(parts) < 2 or not parts[0] or not parts[1]:
        return None
    return parts[0], parts[1]


@st.cache_data(show_spinner=False)
def fetch_issues(owner: str, repo: str, limit: int = 50):
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


repo_url = st.text_input("GitHub repo URL", placeholder="https://github.com/pallets/flask")

if st.button("Fetch issues", type="primary"):
    parsed = parse_repo(repo_url)
    if not parsed:
        st.error("Please enter a URL like https://github.com/owner/repo")
    else:
        try:
            with st.spinner("Fetching issues..."):
                data = fetch_issues(*parsed)
            if not data:
                st.info("No open issues found.")
            else:
                st.success(f"Fetched {len(data)} open issues from {parsed[0]}/{parsed[1]}")
                st.dataframe(pd.DataFrame(data), use_container_width=True)
        except requests.HTTPError as e:
            st.error(f"GitHub API error: {e}. The repo may not exist, or you hit the rate limit.")
        except requests.RequestException as e:
            st.error(f"Network error: {e}")
