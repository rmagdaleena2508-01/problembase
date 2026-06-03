from fastapi import APIRouter, HTTPException
from models.request import SearchRequest
from models.response import SearchResponse
from services.aggregator import aggregate_complaints
from services.analyzer import analyze_complaints
from services.cache import get_cached, save_cached

router = APIRouter(prefix="/search", tags=["search"])

@router.post("/", response_model=SearchResponse)
async def search(request: SearchRequest):
    if not request.product.strip():
        raise HTTPException(status_code=400, detail="Product name cannot be empty")

    # Check cache first
    cached = get_cached(request.product)
    if cached:
        print(f"Cache hit for: {request.product}")
        return cached

    print(f"Cache miss for: {request.product} — scraping now")

    try:
        complaints = aggregate_complaints(request.product, request.limit)

        if not complaints:
            raise HTTPException(status_code=404, detail=f"No complaints found for '{request.product}'")

        clusters = analyze_complaints(request.product, complaints)

        result = SearchResponse(
            product=request.product,
            total_complaints=len(complaints),
            clusters=clusters,
            status="success"
        )

        # Save to cache
        save_cached(request.product, result)

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
