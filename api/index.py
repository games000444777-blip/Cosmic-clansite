from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from urllib.request import urlopen, Request
import json

URL = "https://talented-caribou-69877.upstash.io"
TOKEN = "gQAAAAAAARD1AAIncDE2Yjk4NGJkM2ViZTI0YTkyOTM2MTM4NzY0MzY1ODM5MHAxNjk4Nzc"

def redis(cmd, *args):
    path = "/".join(str(a) for a in args)
    req = Request(
        f"{URL}/{cmd}/{path}",
        headers={"Authorization": f"Bearer {TOKEN}"}
    )
    with urlopen(req) as r:
        return json.loads(r.read()).get("result")

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        action = query.get("action", [None])[0]
        nick = query.get("nick", [""])[0].lower().strip()

        res = {"ok": False}

        if action == "register":
            redis("SET", f"req:{nick}", "pending")
            redis("LPUSH", "queue", nick)
            res = {"ok": True}

        elif action == "status":
            res = {"status": redis("GET", f"req:{nick}") or "pending"}

        elif action == "get_job":
            res = {"nick": redis("RPOP", "queue")}

        elif action == "set_res":
            status = query.get("status", [""])[0]
            redis("SET", f"req:{nick}", status)
            res = {"ok": True}

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(res).encode())
