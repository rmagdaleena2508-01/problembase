from scrapers.hackernews import scrape_hackernews
from scrapers.github import scrape_github
from models.response import Complaint

def aggregate_complaints(product: str, limit: int = 10) -> list[Complaint]:
    print(f"Scraping HackerNews for: {product}")
    hn_complaints = scrape_hackernews(product, limit)

    print(f"Scraping GitHub for: {product}")
    gh_complaints = scrape_github(product, limit)

    all_complaints = hn_complaints + gh_complaints

    # Sort by score descending — highest upvoted complaints first
    all_complaints.sort(key=lambda c: c.score, reverse=True)

    print(f"Total complaints found: {len(all_complaints)}")
    return all_complaints
