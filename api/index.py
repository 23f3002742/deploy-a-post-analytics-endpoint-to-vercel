from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
import numpy as np
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Your telemetry data (from the exam download / original JSON)
TELEMETRY_DATA = json.loads("""
[
  {"region": "apac", "service": "support", "latency_ms": 218.87, "uptime_pct": 98.801, "timestamp": 20250301},
  {"region": "apac", "service": "catalog", "latency_ms": 191.79, "uptime_pct": 97.519, "timestamp": 20250302},
  {"region": "apac", "service": "catalog", "latency_ms": 194.55, "uptime_pct": 98.506, "timestamp": 20250303},
  {"region": "apac", "service": "analytics", "latency_ms": 175.63, "uptime_pct": 97.915, "timestamp": 20250304},
  {"region": "apac", "service": "checkout", "latency_ms": 227.95, "uptime_pct": 98.664, "timestamp": 20250305},
  {"region": "apac", "service": "analytics", "latency_ms": 109.85, "uptime_pct": 98.626, "timestamp": 20250306},
  {"region": "apac", "service": "checkout", "latency_ms": 147.65, "uptime_pct": 97.124, "timestamp": 20250307},
  {"region": "apac", "service": "payments", "latency_ms": 132.36, "uptime_pct": 98.319, "timestamp": 20250308},
  {"region": "apac", "service": "catalog", "latency_ms": 113.16, "uptime_pct": 98.431, "timestamp": 20250309},
  {"region": "apac", "service": "analytics", "latency_ms": 214.49, "uptime_pct": 98.062, "timestamp": 20250310},
  {"region": "apac", "service": "support", "latency_ms": 150.63, "uptime_pct": 99.201, "timestamp": 20250311},
  {"region": "apac", "service": "analytics", "latency_ms": 121.78, "uptime_pct": 98.592, "timestamp": 20250312},
  {"region": "emea", "service": "payments", "latency_ms": 155.92, "uptime_pct": 97.945, "timestamp": 20250301},
  {"region": "emea", "service": "analytics", "latency_ms": 156.89, "uptime_pct": 98.131, "timestamp": 20250302},
  {"region": "emea", "service": "recommendations", "latency_ms": 220.5, "uptime_pct": 99.319, "timestamp": 20250303},
  {"region": "emea", "service": "payments", "latency_ms": 106.4, "uptime_pct": 98.497, "timestamp": 20250304},
  {"region": "emea", "service": "payments", "latency_ms": 222.19, "uptime_pct": 97.604, "timestamp": 20250305},
  {"region": "emea", "service": "checkout", "latency_ms": 144.91, "uptime_pct": 97.257, "timestamp": 20250306},
  {"region": "emea", "service": "analytics", "latency_ms": 156.87, "uptime_pct": 99.3, "timestamp": 20250307},
  {"region": "emea", "service": "recommendations", "latency_ms": 183.14, "uptime_pct": 97.362, "timestamp": 20250308},
  {"region": "emea", "service": "support", "latency_ms": 119, "uptime_pct": 98.953, "timestamp": 20250309},
  {"region": "emea", "service": "analytics", "latency_ms": 138.7, "uptime_pct": 98.161, "timestamp": 20250310},
  {"region": "emea", "service": "payments", "latency_ms": 234.76, "uptime_pct": 97.104, "timestamp": 20250311},
  {"region": "emea", "service": "analytics", "latency_ms": 106.69, "uptime_pct": 98.376, "timestamp": 20250312},
  {"region": "amer", "service": "checkout", "latency_ms": 120.9, "uptime_pct": 97.579, "timestamp": 20250301},
  {"region": "amer", "service": "support", "latency_ms": 200.85, "uptime_pct": 98.54, "timestamp": 20250302},
  {"region": "amer", "service": "payments", "latency_ms": 229.96, "uptime_pct": 98.31, "timestamp": 20250303},
  {"region": "amer", "service": "checkout", "latency_ms": 182.84, "uptime_pct": 98.83, "timestamp": 20250304},
  {"region": "amer", "service": "catalog", "latency_ms": 106.76, "uptime_pct": 99.497, "timestamp": 20250305},
  {"region": "amer", "service": "recommendations", "latency_ms": 198.13, "uptime_pct": 99.008, "timestamp": 20250306},
  {"region": "amer", "service": "support", "latency_ms": 180.5, "uptime_pct": 97.654, "timestamp": 20250307},
  {"region": "amer", "service": "analytics", "latency_ms": 198.05, "uptime_pct": 99.136, "timestamp": 20250308},
  {"region": "amer", "service": "recommendations", "latency_ms": 140.2, "uptime_pct": 99.23, "timestamp": 20250309},
  {"region": "amer", "service": "checkout", "latency_ms": 126.1, "uptime_pct": 98.761, "timestamp": 20250310},
  {"region": "amer", "service": "recommendations", "latency_ms": 126.93, "uptime_pct": 98.525, "timestamp": 20250311},
  {"region": "amer", "service": "payments", "latency_ms": 135.84, "uptime_pct": 98.53, "timestamp": 20250312}
]
""")


@app.get("/")
def root():
    return {"status": "ok"}


@app.options("/api/latency")
async def options_handler():
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        },
    )


@app.post("/api/latency")
async def latency_analytics(request: Request):
    body = await request.json()
    regions = body.get("regions", [])
    threshold_ms = body.get("threshold_ms", 180)

    results = []
    for region in regions:
        records = [r for r in TELEMETRY_DATA if r["region"] == region]
        latencies = [r["latency_ms"] for r in records]
        uptimes = [r["uptime_pct"] for r in records]
        results.append(
            {
                "region": region,
                "avg_latency": round(float(np.mean(latencies)), 2),
                "p95_latency": round(float(np.percentile(latencies, 95)), 2),
                "avg_uptime": round(float(np.mean(uptimes)), 3),
                "breaches": int(sum(1 for l in latencies if l > threshold_ms)),
            }
        )

    return {"regions": results}
