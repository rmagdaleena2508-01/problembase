import requests
from models.response import Complaint

HN_SEARCH_URL = "https://hn.algolia.com/api/v1/search"

def scrape_hackernews(product: str, limit: int = 10) -> list[Complaint]:
    complaints = []
    queries = [
        f"{product} problem",
        f"{product} issue",
        f"{product} broken",
    ]

    seen_ids = set()

    for query in queries:
        for tag in ["story", "comment"]:
            try:
                response = requests.get(HN_SEARCH_URL, params={
                    "query": query,
                    "tags": tag,
                    "hitsPerPage": limit
                })
                data = response.json()

                for hit in data.get("hits", []):
                    hit_id = hit.get("objectID")
                    if hit_id in seen_ids:
                        continue
                    seen_ids.add(hit_id)

                    text = hit.get("comment_text") or hit.get("title") or ""
                    text = text.strip()
                    if len(text) < 20:
                        continue

                    url = f"https://news.ycombinator.com/item?id={hit_id}"
                    score = hit.get("points") or 0

                    complaints.append(Complaint(
                        text=text[:500],
                        source="hackernews",
                        url=url,
                        score=score
                    ))

            except Exception as e:
                print(f"HN scrape error: {e}")
                continue

    return complaints
