
import time

import httpx

import os

from dotenv import load_dotenv

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("github-mcp-server")

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

GITHUB_OWNER = "abhmrya"
GITHUB_REPO = "mcp-lab"

GITHUB_API = "https://api.github.com"

# Cache format: {key: (saved_time, response_data)}
cache = {}

CACHE_TTL = 60  # Cache valid for 60 seconds


def github_get(endpoint: str, params: dict | None = None) -> dict:
    """Fetch GitHub API data with caching and error handling."""

    params = params or {}
    cache_key = (endpoint, tuple(sorted(params.items())))

    # Check cache
    cached_item = cache.get(cache_key)

    if cached_item:
        saved_time, cached_data = cached_item

        if time.time() - saved_time < CACHE_TTL:
            return cached_data

        del cache[cache_key]

    # Cache miss: Call GitHub API
    try:
        response = httpx.get(
            f"{GITHUB_API}{endpoint}",
            params=params,
            headers={"Accept": "application/vnd.github+json"},
            timeout=10.0,
        )

        if response.status_code == 404:
            raise ValueError("GitHub resource not found.")

        if response.status_code == 403:
            if response.headers.get("X-RateLimit-Remaining") == "0":
                raise ValueError("GitHub API rate limit exceeded.")
            raise ValueError("GitHub access forbidden.")

        response.raise_for_status()
        data = response.json()

        # Save successful response
        cache[cache_key] = (time.time(), data)

        return data

    except httpx.TimeoutException as exc:
        raise RuntimeError("GitHub API request timed out.") from exc

    except httpx.HTTPStatusError as exc:
        raise RuntimeError(
            f"GitHub API returned HTTP {exc.response.status_code}."
        ) from exc

    except httpx.RequestError as exc:
        raise RuntimeError("Could not connect to GitHub API.") from exc


@mcp.tool()
def get_github_user(username: str) -> dict:
    """Get public GitHub profile information."""

    data = github_get(f"/users/{username}")

    return {
        "username": data["login"],
        "name": data["name"],
        "public_repos": data["public_repos"],
        "followers": data["followers"],
        "profile_url": data["html_url"],
    }


@mcp.tool()
def search_github_repositories(query: str) -> list[dict]:
    """Search public GitHub repositories."""

    data = github_get(
        "/search/repositories",
        params={"q": query, "per_page": 5},
    )

    return [
        {
            "name": repo["full_name"],
            "description": repo["description"],
            "stars": repo["stargazers_count"],
            "url": repo["html_url"],
        }
        for repo in data["items"]
    ]


@mcp.tool()
def get_github_rate_limit() -> dict:
    """Check current GitHub API rate limits."""

    data = github_get("/rate_limit")

    return {
        "core": data["resources"]["core"],
        "search": data["resources"]["search"],
    }



@mcp.tool()
def create_github_issue(
    title: str,
    body: str,
    confirm: bool,
) -> dict:
    """Create an issue in the configured GitHub repository.

    Set confirm=True only after the user approves the issue.
    """

    if not confirm:
        return {
            "success": False,
            "message": "Issue creation cancelled. User confirmation required.",
        }

    if not GITHUB_TOKEN:
        raise RuntimeError("GITHUB_TOKEN is not configured.")

    if not title.strip():
        raise ValueError("Issue title cannot be empty.")

    url = (
        f"https://api.github.com/repos/"
        f"{GITHUB_OWNER}/{GITHUB_REPO}/issues"
    )

    response = httpx.post(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        json={
            "title": title,
            "body": body,
        },
        timeout=10.0,
    )

    response.raise_for_status()

    issue = response.json()

    return {
        "success": True,
        "issue_number": issue["number"],
        "title": issue["title"],
        "url": issue["html_url"],
    }



@mcp.tool()
def list_github_issues(state: str = "open") -> list[dict]:
    """List issues from the configured GitHub repository."""

    if state not in ("open", "closed", "all"):
        raise ValueError("State must be open, closed, or all.")

    url = (
        f"https://api.github.com/repos/"
        f"{GITHUB_OWNER}/{GITHUB_REPO}/issues"
    )

    headers = {
        "Accept": "application/vnd.github+json",
    }

    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    response = httpx.get(
        url,
        params={"state": state, "per_page": 10},
        headers=headers,
        timeout=10.0,
    )

    response.raise_for_status()

    issues = response.json()

    return [
        {
            "number": issue["number"],
            "title": issue["title"],
            "state": issue["state"],
            "url": issue["html_url"],
        }
        for issue in issues
        if "pull_request" not in issue
    ]




if __name__ == "__main__":
    mcp.run()
