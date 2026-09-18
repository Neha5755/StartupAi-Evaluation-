"""StartupReady AI backend - standard-library Python API.

Run with: python app.py
"""
from __future__ import annotations

import json
import mimetypes
import os
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

PORT = int(os.environ.get("PORT", "3001"))
DATA_FILE = Path(__file__).parent / "data" / "assessment.json"
FRONTEND_DIR = Path(__file__).parent.parent / "frontend"

CATEGORIES = [
    ("Vision & Innovation", ["startupName", "industry", "summary", "vision"]),
    ("Market Opportunity", ["market", "customer", "tam", "competitors"]),
    ("Product Readiness", ["productStatus", "features", "roadmap"]),
    ("Technology", ["stack", "security", "scaling"]),
    ("Business Model", ["revenueModel", "pricing", "cac", "ltv"]),
    ("Team", ["founders", "team", "hiring"]),
    ("Financial Health", ["revenue", "burn", "runway", "forecast"]),
    ("Legal & Compliance", ["incorporated", "privacy", "ip"]),
    ("Sales & GTM", ["channels", "salesCycle", "conversion"]),
    ("Traction", ["customers", "mrr", "growth"]),
    ("ESG", ["environment", "social", "sdgs"]),
    ("Investment Readiness", ["funding", "useOfFunds", "pitchDeck"]),
]


def load_assessment() -> dict:
    if not DATA_FILE.exists():
        return {"values": {}, "uploads": {}, "updatedAt": None}
    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"values": {}, "uploads": {}, "updatedAt": None}


def save_assessment(assessment: dict) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(json.dumps(assessment, indent=2), encoding="utf-8")


def has_value(value: object) -> bool:
    return value is not None and str(value).strip() != ""


def build_scorecard(values: dict) -> dict:
    scores = []
    for label, fields in CATEGORIES:
        filled = sum(has_value(values.get(field)) for field in fields)
        score = round(35 + (filled / len(fields)) * 65)
        scores.append({"label": label, "score": score, "filled": filled, "total": len(fields)})

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
    return {"overall": overall, "scores": scores, "verdict": verdict, "recommendations": recommendations}


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
                "STARTUPREADY AI EXECUTIVE REPORT", "=" * 36,
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
        if urlparse(self.path).path != "/api/analyze":
            return self.send_json({"error": "Route not found"}, HTTPStatus.NOT_FOUND)
        try:
            incoming = self.read_json()
            values = incoming.get("values", load_assessment()["values"])
            scorecard = build_scorecard(values)
            self.send_json({
                "score": scorecard["overall"],
                "headline": "Your case is taking shape.",
                "insight": f"Current readiness is {scorecard['overall']}/100. Add measurable proof, customer evidence and a dated next milestone.",
                "actions": ["Add one measurable outcome.", "Attach evidence where available.", "Assign an owner and deadline."],
            })
        except (ValueError, json.JSONDecodeError) as error:
            self.send_json({"error": str(error)}, HTTPStatus.BAD_REQUEST)

    def log_message(self, format: str, *args: object) -> None:
        print(f"[StartupReady] {self.address_string()} - {format % args}")


if __name__ == "__main__":
    print(f"StartupReady Python API running at http://localhost:{PORT}")
    ThreadingHTTPServer(("", PORT), StartupReadyHandler).serve_forever()
