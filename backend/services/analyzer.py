from groq import Groq
from config import get_settings
from models.response import Complaint, ProblemCluster
import json

settings = get_settings()
client = Groq(api_key=settings.groq_api_key)

def analyze_complaints(product: str, complaints: list[Complaint]) -> list[ProblemCluster]:
    if not complaints:
        return []

    complaints_text = "\n".join([
        f"[{i+1}] (score:{c.score}, source:{c.source}) {c.text[:200]}"
        for i, c in enumerate(complaints[:20])
    ])

    prompt = f"""You are analyzing user complaints about the software product "{product}".

Here are the complaints:
{complaints_text}

Group these complaints into 3-5 themes. For each theme return:
- theme: a short name (e.g. "Sync Issues", "Performance Problems")
- severity: one of "critical", "high", "medium", "low"
- insight: one sentence explaining the core problem and why it matters
- complaint_indices: list of complaint numbers that belong to this theme (e.g. [1, 3, 5])

Respond ONLY with a JSON array. No explanation. No markdown. Example format:
[
  {{
    "theme": "Performance Problems",
    "severity": "high",
    "insight": "Users frequently report slow load times especially with large databases.",
    "complaint_indices": [1, 4, 7]
  }}
]"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    raw = response.choices[0].message.content.strip()

    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    clusters_data = json.loads(raw)

    clusters = []
    for cluster in clusters_data:
        indices = [i - 1 for i in cluster.get("complaint_indices", [])]
        matched = [complaints[i] for i in indices if 0 <= i < len(complaints)]

        clusters.append(ProblemCluster(
            theme=cluster["theme"],
            severity=cluster["severity"],
            insight=cluster["insight"],
            complaint_count=len(matched),
            complaints=matched[:5]
        ))

    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    clusters.sort(key=lambda c: severity_order.get(c.severity, 4))

    return clusters
