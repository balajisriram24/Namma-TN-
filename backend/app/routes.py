from datetime import datetime, timezone
import uuid
from flask import Blueprint, jsonify, request, g
from pymongo.errors import DuplicateKeyError
from bson import ObjectId
from .db import complaints, users, client
from .ai import analyze_with_gemini
from .auth import token_required, admin_required, create_token
from werkzeug.security import generate_password_hash, check_password_hash
import re

api = Blueprint("api", __name__)

CATEGORY_PREFIX = {
    "water": "WTR",
    "road": "ROD",
    "drainage": "DRN",
    "waste": "WST",
    "streetlight": "LGT",
    "flooding": "FLD",
    "other": "CIV",
}

VALID_IMAGE_DATA_URL_RE = re.compile(r"^data:image/(png|jpeg|jpg|gif|webp);base64,[A-Za-z0-9+/=]+$")


def is_valid_image_data_url(value):
    if not value or not isinstance(value, str):
        return False
    return bool(VALID_IMAGE_DATA_URL_RE.match(value.strip()))

def make_id(category):
    prefix = CATEGORY_PREFIX.get(category, "CIV")
    return f"TN-{prefix}-{datetime.now(timezone.utc).strftime('%y%m%d')}-{uuid.uuid4().hex[:4].upper()}"

def serialize(doc):
    if not doc:
        return None
    doc = dict(doc)
    doc.pop("_id", None)
    if isinstance(doc.get("created_at"), datetime):
        doc["created_at"] = doc["created_at"].isoformat()
    if isinstance(doc.get("updated_at"), datetime):
        doc["updated_at"] = doc["updated_at"].isoformat()
    # Convert ObjectId to string for JSON serialization
    if isinstance(doc.get("user_id"), ObjectId):
        doc["user_id"] = str(doc["user_id"])
    return doc

@api.get("/health")
def health():
    try:
        client.admin.command("ping")
        return jsonify({"status": "ok", "database": "connected"})
    except Exception as exc:
        return jsonify({"status": "degraded", "database": "unavailable", "error": str(exc)}), 503

@api.post("/ai/analyze")
def analyze():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    if len(message) < 5:
        return jsonify({"error": "Please describe the problem in a little more detail."}), 400
    return jsonify(analyze_with_gemini(message))

@api.post("/complaints")
def create_complaint():
    # Require authentication (token) — frontend must send Authorization header
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return jsonify({"error": "Authentication required"}), 401
    # token validation delegated to token_required decorator below; for simplicity, reuse it
    return _create_complaint_internal()


@token_required
def _create_complaint_internal():
    data = request.get_json(silent=True) or {}
    required = ["message", "category", "severity", "district", "area"]
    missing = [key for key in required if not str(data.get(key, "")).strip()]
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

    proof_image = data.get("proof_image")
    if proof_image is not None and proof_image != "":
        if not isinstance(proof_image, str):
            return jsonify({"error": "Proof image must be a valid image data URL."}), 400
        if not is_valid_image_data_url(proof_image):
            return jsonify({"error": "Proof image must be a valid PNG, JPG, GIF, or WebP data URL."}), 400

    category = data["category"]
    if category not in CATEGORY_PREFIX:
        return jsonify({"error": "Invalid category."}), 400
    if data["severity"] not in {"low", "medium", "high"}:
        return jsonify({"error": "Invalid severity."}), 400

    doc = {
        "complaint_id": make_id(category),
        "message": data["message"].strip(),
        "category": category,
        "severity": data["severity"],
        "district": data["district"].strip(),
        "area": data["area"].strip(),
        "duration": (data.get("duration") or "").strip(),
        "proof_image": (proof_image or "").strip(),
        "status": "Submitted",
        "user_id": ObjectId(g.user.get("user_id")),
        "created_at": datetime.now(timezone.utc),
    }

    try:
        complaints.insert_one(doc)
    except DuplicateKeyError:
        return jsonify({"error": "Could not create a unique complaint ID. Please retry."}), 409

    return jsonify(serialize(doc)), 201

@api.get("/complaints/<complaint_id>")
def get_complaint(complaint_id):
    doc = complaints.find_one({"complaint_id": complaint_id.upper()})
    if not doc:
        return jsonify({"error": "Complaint not found."}), 404
    return jsonify(serialize(doc))


@api.get("/complaints")
@admin_required
def list_complaints():
    docs = complaints.find().sort("created_at", -1)
    return jsonify([serialize(doc) for doc in docs])


@api.get("/complaints/my")
@token_required
def my_complaints():
    uid = g.user.get("user_id")
    try:
        oid = ObjectId(uid)
    except Exception:
        return jsonify({"error": "Invalid user id"}), 400
    docs = complaints.find({"user_id": oid}).sort("created_at", -1)
    return jsonify([serialize(doc) for doc in docs])

@api.patch("/complaints/<complaint_id>")
@admin_required
def update_status(complaint_id):
    data = request.get_json(silent=True) or {}
    status = data.get("status")
    if status not in {"Submitted", "In Progress", "Resolved"}:
        return jsonify({"error": "Invalid status."}), 400

    result = complaints.update_one(
        {"complaint_id": complaint_id.upper()},
        {"$set": {"status": status, "updated_at": datetime.now(timezone.utc)}}
    )
    if result.matched_count == 0:
        return jsonify({"error": "Complaint not found."}), 404

    doc = complaints.find_one({"complaint_id": complaint_id.upper()})
    return jsonify(serialize(doc))


# Authentication endpoints
@api.post("/auth/register")
def register():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    phone = (data.get("phone") or "").strip()
    password = data.get("password") or ""
    if not (name and email and phone and password):
        return jsonify({"error": "Missing required fields."}), 400
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify({"error": "Invalid email."}), 400
    if users.find_one({"email": email}):
        return jsonify({"error": "Email already registered."}), 409
    pw_hash = generate_password_hash(password)
    doc = {
        "name": name,
        "email": email,
        "phone": phone,
        "password_hash": pw_hash,
        "role": "citizen",
        "created_at": datetime.now(timezone.utc)
    }
    users.insert_one(doc)
    user = users.find_one({"email": email})
    token = create_token(user)
    user.pop("password_hash", None)
    user = serialize(user)
    return jsonify({"user": user, "token": token}), 201


@api.post("/auth/login")
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    if not (email and password):
        return jsonify({"error": "Missing credentials."}), 400
    user = users.find_one({"email": email})
    if not user:
        return jsonify({"error": "Invalid credentials."}), 401
    if not check_password_hash(user.get("password_hash", ""), password):
        return jsonify({"error": "Invalid credentials."}), 401
    token = create_token(user)
    user.pop("password_hash", None)
    user = serialize(user)
    return jsonify({"user": user, "token": token})


@api.get("/auth/me")
@token_required
def me():
    uid = g.user.get("user_id")
    try:
        user = users.find_one({"_id": ObjectId(uid)})
    except Exception:
        return jsonify({"error": "User not found."}), 404
    if not user:
        return jsonify({"error": "User not found."}), 404
    user.pop("password_hash", None)
    return jsonify(serialize(user))


@api.post("/auth/logout")
@token_required
def logout():
    # Token is validated by decorator; client clears localStorage
    return jsonify({"status": "ok"})
