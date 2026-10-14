"""StartupReady backend - standard-library Python API.

Run with: python app.py
"""
from __future__ import annotations

import json
import mimetypes
import os
import hashlib
import secrets
import re
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

PORT = int(os.environ.get("PORT", "3001"))
DATA_FILE = Path(__file__).parent / "data" / "assessment.json"
USERS_FILE = Path(__file__).parent / "data" / "users.json"
FRONTEND_DIR = Path(__file__).parent.parent / "frontend"

CATEGORIES = [
    ("Startup Overview", ["startupName", "summary"]),
    ("Problem & Solution", ["problem", "solution"]),
    ("Market Opportunity", ["customer", "tam"]),
    ("Product Readiness", ["productStatus", "features"]),
    ("Technology", ["stack", "security"]),
    ("Business Model", ["revenueModel", "pricing"]),
    ("Team", ["founders", "team"]),
    ("Financial Health", ["revenue", "runway"]),
    ("Legal & Compliance", ["incorporated", "privacy"]),
    ("Sales & GTM", ["channels", "salesCycle"]),
    ("Traction", ["customers", "mrr"]),
    ("ESG", ["environment", "social"]),
    ("Investment Readiness", ["funding", "useOfFunds"]),
    ("Risk Assessment", ["marketRisk", "controls"]),
]

# These examples appear only when an empty input receives focus. They are not
# stored as user answers and therefore never bypass step validation.
SAMPLE_EXAMPLES = {
        "startupName": "GreenLoop",
        "summary": "GreenLoop helps apartment communities reduce waste through smart sorting and reward tracking.",
        "problem": "Apartment residents lack clear sorting guidance and building managers cannot measure waste diversion.",
        "solution": "A mobile app and QR-enabled bins guide sorting, track participation and provide building dashboards.",
        "customer": "Mid-size apartment communities in Indian metro cities",
        "tam": "$1.2B",
        "productStatus": "MVP",
        "features": "QR bin scanning, sorting guidance, resident rewards, manager dashboard and monthly impact reports.",
        "stack": "Python backend, HTML/CSS/JavaScript frontend, JSON storage and Render hosting.",
        "security": "Role-based access, password hashing, HTTPS, encrypted backups and privacy-by-design practices.",
        "revenueModel": "Subscription",
        "pricing": "Property managers pay ₹12 per apartment per month, with an annual community plan.",
        "founders": "One founder has 6 years in property operations; the other has 5 years building mobile products.",
        "team": "Two founders, one full-stack engineer, one product designer and a part-time waste operations advisor.",
        "revenue": "540000",
        "runway": "14",
        "incorporated": "Yes",
        "privacy": "Published",
        "channels": "Direct founder-led sales, property-management partners and sustainability consultants.",
        "salesCycle": "30 to 45 days",
        "customers": "8",
        "mrr": "45000",
        "environment": "Each active community reports kilograms of waste diverted from landfill each month.",
        "social": "Residents receive accessible recycling education and local waste workers receive clearer sorting inputs.",
        "funding": "15000000",
        "useOfFunds": "45% product and engineering, 35% sales and customer success, 20% pilot operations and working capital.",
        "marketRisk": "Property managers may delay adoption; mitigate with short pilots and quantified waste-diversion reports.",
        "controls": "Founders review a monthly risk register, assign owners and maintain a quarterly contingency plan.",
}


def blank_assessment() -> dict:
    """Return empty answers with a separate, non-validating example template."""
    return {
        "values": {},
        "uploads": {},
        "examples": json.loads(json.dumps(SAMPLE_EXAMPLES)),
        "templateVersion": 2,
        "updatedAt": None,
    }


def load_assessment() -> dict:
    if not DATA_FILE.exists():
        return blank_assessment()
    try:
        assessment = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        # Version 2 separates example hints from real answers. Older seeded
        # records are deliberately reset so they cannot unlock every step.
        if assessment.get("templateVersion") != 2:
            return blank_assessment()
        assessment.setdefault("values", {})
        assessment.setdefault("uploads", {})
        assessment.setdefault("examples", json.loads(json.dumps(SAMPLE_EXAMPLES)))
        return assessment
    except (OSError, json.JSONDecodeError):
        return blank_assessment()


def save_assessment(assessment: dict) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(json.dumps(assessment, indent=2), encoding="utf-8")


def load_users() -> list[dict]:
    try:
        return json.loads(USERS_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []


def save_users(users: list[dict]) -> None:
    USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    USERS_FILE.write_text(json.dumps(users, indent=2), encoding="utf-8")


def password_hash(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000).hex()


def public_user(user: dict) -> dict:
    return {"name": user["name"], "email": user["email"]}


def has_value(value: object) -> bool:
    return value is not None and str(value).strip() != ""


def evidence_strength(field: str, value: object) -> int:
    """Award one quality point for a detailed answer beyond the demo hint."""
    text = str(value).strip()
    if not text or text == SAMPLE_EXAMPLES.get(field, ""):
        return 0
    if field in {"productStatus", "revenueModel", "incorporated", "privacy"}:
        return 1
    if text.replace(".", "", 1).replace(",", "").isdigit():
        return int(float(text.replace(",", "")) > 0)
    words = text.split()
    return int(len(text) >= 80 or (len(words) >= 10 and any(char.isdigit() for char in text)))


def build_scorecard(values: dict) -> dict:
    scores = []
    for label, fields in CATEGORIES:
        filled = sum(has_value(values.get(field)) for field in fields)
        completion_score = 35 + (filled / len(fields)) * 41
        evidence = sum(evidence_strength(field, values.get(field)) for field in fields)
        evidence_bonus = (evidence / len(fields)) * 24 if filled == len(fields) else 0
        score = round(min(100, completion_score + evidence_bonus))
        scores.append({
            "label": label,
            "score": score,
            "filled": filled,
            "total": len(fields),
            "evidence": evidence,
        })

    overall = round(sum(item["score"] for item in scores) / len(scores))
    verdict = (
        "Seed / Pre-Series A Ready" if overall >= 82
        else "Building Funding Readiness" if overall >= 68
        else "Foundation Stage"
    )
    recommendations = []
    for index, item in enumerate(sorted(scores, key=lambda item: item["score"])[:3]):
        recommendations.append({
            "priority": "High" if index == 0 else "Medium",
            "area": item["label"],
            "improvement": f"Add {max(1, item['total'] - item['filled'])} more evidence-backed responses.",
            "impact": f"+{max(3, round((100 - item['score']) / 7))} points",
            "effort": "1-2 days" if index == 0 else "2-4 hours",
            "owner": "Founder" if index == 0 else "Functional lead",
        })
    return {
        "overall": overall,
        "scores": scores,
        "verdict": verdict,
        "recommendations": recommendations,
        "scoringNote": "Complete essentials establish a 76/100 baseline. Detailed, evidence-backed answers can raise the score to 100.",
    }


class StartupReadyHandler(BaseHTTPRequestHandler):
    def end_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, PUT, POST, OPTIONS")
        super().end_headers()

    def send_json(self, body: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        content = json.dumps(body).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def read_json(self) -> dict:
        size = int(self.headers.get("Content-Length", 0))
        if size > 1_000_000:
            raise ValueError("Request body is too large")
        raw = self.rfile.read(size)
        return json.loads(raw or b"{}")

    def do_OPTIONS(self) -> None:
        self.send_response(HTTPStatus.NO_CONTENT)
        self.end_headers()

    def do_GET(self) -> None:
        route = urlparse(self.path).path
        assessment = load_assessment()
        if route == "/api/health":
            return self.send_json({"ok": True, "runtime": "Python standard library"})
        if route == "/api/assessment":
            return self.send_json(assessment)
        if route == "/api/scorecard":
            return self.send_json(build_scorecard(assessment["values"]))
        if route == "/api/report":
            card = build_scorecard(assessment["values"])
            lines = [
                "STARTUPREADY EXECUTIVE REPORT", "=" * 36,
                f"Startup: {assessment['values'].get('startupName', 'Your Startup')}",
                f"Funding readiness: {card['overall']}/100", card["verdict"], "", "CATEGORY SCORES",
            ]
            lines.extend(f"{item['label']}: {item['score']}/100" for item in card["scores"])
            lines.extend(["", "PRIORITY ACTIONS"])
            lines.extend(f"[{item['priority']}] {item['area']}: {item['improvement']}" for item in card["recommendations"])
            content = "\n".join(lines).encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Disposition", 'attachment; filename="startupready-report.txt"')
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            return self.wfile.write(content)
        if route.startswith("/api/"):
            return self.send_json({"error": "Route not found"}, HTTPStatus.NOT_FOUND)
        self.serve_frontend_file(route)

    def serve_frontend_file(self, route: str) -> None:
        """Serve the browser app from frontend/ for one-service deployment."""
        requested = "index.html" if route in {"", "/"} else unquote(route).lstrip("/")
        candidate = (FRONTEND_DIR / requested).resolve()
        try:
            candidate.relative_to(FRONTEND_DIR.resolve())
        except ValueError:
            return self.send_json({"error": "Not found"}, HTTPStatus.NOT_FOUND)
        if not candidate.is_file():
            return self.send_json({"error": "Not found"}, HTTPStatus.NOT_FOUND)
        content = candidate.read_bytes()
        content_type = mimetypes.guess_type(candidate.name)[0] or "application/octet-stream"
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_PUT(self) -> None:
        if urlparse(self.path).path != "/api/assessment":
            return self.send_json({"error": "Route not found"}, HTTPStatus.NOT_FOUND)
        try:
            incoming = self.read_json()
            current = load_assessment()
            current["values"] = {**current["values"], **incoming.get("values", {})}
            current["uploads"] = {**current["uploads"], **incoming.get("uploads", {})}
            current["updatedAt"] = datetime.now(timezone.utc).isoformat()
            save_assessment(current)
            self.send_json({"saved": True, "assessment": current, "scorecard": build_scorecard(current["values"])})
        except (ValueError, json.JSONDecodeError) as error:
            self.send_json({"error": str(error)}, HTTPStatus.BAD_REQUEST)

    def do_POST(self) -> None:
        route = urlparse(self.path).path
        if route == "/api/auth/signup":
            return self.signup()
        if route == "/api/auth/login":
            return self.login()
        return self.send_json({"error": "Route not found"}, HTTPStatus.NOT_FOUND)

    def signup(self) -> None:
        try:
            incoming = self.read_json()
            name = str(incoming.get("name", "")).strip()
            email = str(incoming.get("email", "")).strip().lower()
            password = str(incoming.get("password", ""))
            if len(name) < 2 or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
                raise ValueError("Enter a valid name and email address.")
            if len(password) < 8:
                raise ValueError("Password must contain at least 8 characters.")
            users = load_users()
            if any(user["email"] == email for user in users):
                return self.send_json({"error": "An account already exists for this email."}, HTTPStatus.CONFLICT)
            salt = secrets.token_hex(16)
            user = {"name": name, "email": email, "salt": salt, "passwordHash": password_hash(password, salt)}
            users.append(user)
            save_users(users)
            self.send_json({"user": public_user(user)}, HTTPStatus.CREATED)
        except (ValueError, json.JSONDecodeError) as error:
            self.send_json({"error": str(error)}, HTTPStatus.BAD_REQUEST)

    def login(self) -> None:
        try:
            incoming = self.read_json()
            email = str(incoming.get("email", "")).strip().lower()
            password = str(incoming.get("password", ""))
            if not email or not password:
                raise ValueError("Email address and password are required.")
            user = next((entry for entry in load_users() if entry["email"] == email), None)
            if not user or not secrets.compare_digest(password_hash(password, user["salt"]), user["passwordHash"]):
                return self.send_json({"error": "Incorrect email or password."}, HTTPStatus.UNAUTHORIZED)
            self.send_json({"user": public_user(user)})
        except (ValueError, json.JSONDecodeError) as error:
            self.send_json({"error": str(error)}, HTTPStatus.BAD_REQUEST)

    def log_message(self, format: str, *args: object) -> None:
        print(f"[StartupReady] {self.address_string()} - {format % args}")


if __name__ == "__main__":
    print(f"StartupReady Python API running at http://localhost:{PORT}")
    ThreadingHTTPServer(("", PORT), StartupReadyHandler).serve_forever()
