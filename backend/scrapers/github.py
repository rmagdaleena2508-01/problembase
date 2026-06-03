import requests
from config import get_settings
from models.response import Complaint

settings = get_settings()

GITHUB_API = "https://api.github.com/search/issues"

def scrape_github(product: str, limit: int = 10) -> list[Complaint]:
    complaints = []
    headers = {
        "Authorization": f"token {settings.github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    queries = [
        f"{product} bug",
        f"{product} issue",
        f"{product} broken",
    ]

    seen_ids = set()

    for query in queries:
        try:
            response = requests.get(GITHUB_API, headers=headers, params={
                "q": query,
                "sort": "reactions",
                "order": "desc",
                "per_page": limit
            })
            data = response.json()

            for item in data.get("items", []):
                if item["id"] in seen_ids:
                    continue
                seen_ids.add(item["id"])

                text = f"{item['title']} {item.get('body') or ''}".strip()
                if len(text) < 20:
                    continue

                complaints.append(Complaint(
                    text=text[:500],
                    source="github",
                    url=item["html_url"],
                    score=item.get("reactions", {}).get("total_count", 0)
                ))

        except Exception as e:
            print(f"GitHub scrape error: {e}")
            continue

    return complaints
