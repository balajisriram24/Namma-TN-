import json
import re
from google import genai
from .config import Config

CATEGORIES = {
    "water": ["water", "தண்ணீர்", "குடிநீர்", "தண்ணி", "pipeline", "pipe", "supply", "leakage"],
    "road": ["road", "ரோடு", "சாலை", "pothole", "பள்ளம்", "பாதை", "damage", "damaged"],
    "drainage": ["drain", "drainage", "சாக்கடை", "கழிவுநீர்", "sewage", "open drain", "blocked drain"],
    "waste": ["garbage", "குப்பை", "waste", "குப்பைகள்", "dumping", "bin", "trash"],
    "streetlight": ["streetlight", "street light", "தெருவிளக்கு", "light", "விளக்கு", "lamp"],
    "flooding": ["flood", "flooding", "வெள்ளம்", "நீர்த்தேக்கம்", "waterlogging", "தண்ணி தேங்கி", "rainwater", "மழைநீர்"],
}

def local_fallback(text):
    lower = text.lower()
    scores = {key: sum(word.lower() in lower for word in words) for key, words in CATEGORIES.items()}
    category = max(scores, key=scores.get)
    if scores[category] == 0:
        category = "other"

    high = ["danger", "dangerous", "critical", "overflow", "school", "hospital",
            "blocked", "பெரிய", "ஆபத்து", "முழுசா", "முழுவதும்"]
    severity = "high" if any(w in lower for w in high) else "medium"
    if any(w in lower for w in ["small", "minor", "சிறிய"]):
        severity = "low"

    # Location is intentionally collected by the UI rather than inferred.
    return {
        "category": category,
        "severity": severity,
        "needs_location": True,
        "reason": "Local fallback classification"
    }

def analyze_with_gemini(text):
    if not Config.GEMINI_API_KEY:
        return local_fallback(text)

    try:
        client = genai.Client(api_key=Config.GEMINI_API_KEY)
        prompt = f"""
You are NammaTN, a Tamil Nadu civic issue assistant.
Understand the citizen message in Tamil, Tanglish, or English.

Return ONLY valid JSON:
{{
  "category": "water|road|drainage|waste|streetlight|flooding|other",
  "severity": "low|medium|high",
  "needs_location": true
}}

Rules:
- Do not invent a district or exact location.
- Use "other" if the message is not one of the six civic categories.
- Use high severity for safety hazards, major blockage/overflow, or issues near sensitive public places.
Citizen message:
{text}
"""
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        raw = (response.text or "").strip()
        raw = re.sub(r"^```json\s*|\s*```$", "", raw).strip()
        data = json.loads(raw)
        allowed_categories = set(CATEGORIES) | {"other"}
        if data.get("category") not in allowed_categories:
            raise ValueError("Invalid category from model")
        if data.get("severity") not in {"low", "medium", "high"}:
            raise ValueError("Invalid severity from model")
        data["needs_location"] = True
        return data
    except Exception as exc:
        print(f"Gemini fallback: {exc}")
        return local_fallback(text)
