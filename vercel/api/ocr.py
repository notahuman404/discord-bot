from http.server import BaseHTTPRequestHandler
import json
import io
import base64
import numpy as np
from PIL import Image
import easyocr

# Loaded once per cold start; reused across warm invocations
reader = easyocr.Reader(['en'])


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)

        try:
            data = json.loads(body)
            image_b64 = data['image']  # base64-encoded image string
            image_bytes = base64.b64decode(image_b64)
            image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
            image_np = np.array(image)

            result = reader.readtext(image_np, detail=0)
            response_body = {'result': result}
            status_code = 200
        except Exception as e:
            response_body = {'error': str(e)}
            status_code = 500

        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response_body).encode())

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'status': 'ok'}).encode())
