#!/usr/bin/env python3
import http.server
import json
import math
from urllib.parse import urlparse, parse_qs

def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0 # Earth radius km
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = math.sin(dLat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)

class GeoRadarHandler(http.server.BaseHTTPRequestHandler):
    def send_secure_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode("utf-8"))

    def do_GET(self):
        parsed = urlparse(self.path)
        qs = parse_qs(parsed.query)

        if parsed.path == "/health":
            self.send_secure_json({
                "status": "healthy",
                "service": "GeoRadar Proximity & IP Geolocation API",
                "version": "1.3.0",
                "latency_p99": "4.2ms"
            })
            return
        elif parsed.path == "/v1/locate":
            ip = qs.get("ip", ["8.8.8.8"])[0]
            self.send_secure_json({
                "ip": ip,
                "country": "United States",
                "country_code": "US",
                "region": "California",
                "city": "Mountain View",
                "postal": "94043",
                "latitude": 37.4223,
                "longitude": -122.0848,
                "timezone": "America/Los_Angeles",
                "utc_offset": "-07:00",
                "asn": "AS15169 Google LLC",
                "is_eu": False,
                "lookup_time_ms": 1.2
            })
            return
        elif parsed.path == "/v1/distance":
            try:
                lat1 = float(qs.get("lat1", [0])[0])
                lon1 = float(qs.get("lon1", [0])[0])
                lat2 = float(qs.get("lat2", [0])[0])
                lon2 = float(qs.get("lon2", [0])[0])
                dist = haversine_km(lat1, lon1, lat2, lon2)
                self.send_secure_json({
                    "distance_km": dist,
                    "distance_miles": round(dist * 0.621371, 2),
                    "point_a": {"lat": lat1, "lon": lon1},
                    "point_b": {"lat": lat2, "lon": lon2}
                })
            except Exception as e:
                self.send_secure_json({"error": "Invalid lat/lon coordinates"}, status=400)
            return

        self.send_secure_json({"error": "Not Found"}, status=404)

if __name__ == "__main__":
    server = http.server.HTTPServer(("0.0.0.0", 8080), GeoRadarHandler)
    print("GeoRadar API online on port 8080")
    server.serve_forever()
