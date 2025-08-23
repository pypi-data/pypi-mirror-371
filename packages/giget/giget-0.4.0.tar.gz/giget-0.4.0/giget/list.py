#!/usr/bin/env python3
import sys
import requests
from urllib.parse import urlparse

# ANSI colors for pretty output
BLUE = "\033[94m"
GREEN = "\033[92m"
RESET = "\033[0m"
CYAN = "\033[96m"
YELLOW = "\033[93m"

def parse_github_url(url: str):
    """Extract owner, repo, and path from a GitHub URL."""
    parsed = urlparse(url)
    parts = parsed.path.strip("/").split("/")
    if len(parts) < 2:
        raise ValueError("Invalid GitHub URL. Format: https://github.com/<owner>/<repo>[/path]")
    owner, repo = parts[0], parts[1].replace(".git", "")
    repo_path = "/".join(parts[2:]) if len(parts) > 2 else ""
    return owner, repo, repo_path

def fetch_contents(owner, repo, path, token=None):
    """Fetch contents of a GitHub directory via API."""
    api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"
    resp = requests.get(api_url, headers=headers)
    resp.raise_for_status()
    return resp.json()

def print_tree(data, prefix=""):
    """Recursively print GitHub folder structure like `tree`."""
    for idx, item in enumerate(data):
        connector = "└── " if idx == len(data) - 1 else "├── "
        if item["type"] == "dir":
            print(prefix + connector + BLUE + item["name"] + RESET)
            sub_data = fetch_contents(owner, repo, item["path"])
            new_prefix = prefix + ("    " if idx == len(data) - 1 else "│   ")
            print_tree(sub_data, new_prefix)
        else:
            print(prefix + connector + GREEN + item["name"] + RESET)

def list_github_folder(url: str, token: str = None):
    """List files/folders in a GitHub repo folder in tree format."""
    global owner, repo
    owner, repo, repo_path = parse_github_url(url)
    data = fetch_contents(owner, repo, repo_path, token)
    
    print(f"{CYAN}{repo}/{repo_path if repo_path else ''}{RESET}")
    print_tree(data)

# if __name__ == "__main__":
#     if len(sys.argv) < 3 or sys.argv[1] != "list":
#         print("Usage: giget list <url>")
#         sys.exit(1)
    
#     url = sys.argv[2]
#     list_github_folder(url)
