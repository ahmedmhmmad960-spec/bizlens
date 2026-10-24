"""Dependency-free Chrome DevTools browser smoke for BizLens V1.

Run with FastAPI, Next.js and localhost headless Chrome already started.
Never calls live Base RPC, spends tokens or uses operator credentials.
"""

import base64
import hashlib
import json
import os
import socket
import struct
import time
from urllib.parse import urlsplit
from urllib.request import urlopen

WEB = os.getenv("BIZLENS_WEB_URL", "http://127.0.0.1:3000")
CHROME = "http://127.0.0.1:9223"


class Cdp:
    def __init__(self, websocket_url):
        p = urlsplit(websocket_url)
        if p.scheme != "ws" or p.hostname not in ("127.0.0.1", "localhost"):
            raise ValueError("CDP must be on localhost")
        self.sock = socket.create_connection((p.hostname, p.port), 10)
        self.sock.settimeout(12)
        key = base64.b64encode(os.urandom(16)).decode("ascii")
        expected = base64.b64encode(hashlib.sha1(
            (key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode()
        ).digest()).decode("ascii")
        self.sock.sendall((
            f"GET {p.path or '/'} HTTP/1.1\r\n"
            f"Host: {p.netloc}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n"
        ).encode())
        headers = b""
        while b"\r\n\r\n" not in headers:
            headers += self.sock.recv(4096)
            if len(headers) > 8192:
                raise RuntimeError("CDP handshake too large")
        first, remainder = headers.split(b"\r\n\r\n", 1)
        if b" 101 " not in first or expected.encode() not in first:
            raise RuntimeError("CDP websocket handshake rejected")
        self.pending = remainder
        self.seq = 0

    def recv_bytes(self, count):
        while len(self.pending) < count:
            segment = self.sock.recv(max(count - len(self.pending), 4096))
            if not segment:
                raise RuntimeError("Chrome closed browser inspection socket")
            self.pending += segment
        result, self.pending = self.pending[:count], self.pending[count:]
        return result

    def send_frame(self, opcode, content):
        mask = os.urandom(4)
        size = len(content)
        if size < 126:
            prefix = bytes([0x80 | opcode, 0x80 | size])
        elif size < 65536:
            prefix = bytes([0x80 | opcode, 0x80 | 126]) + struct.pack("!H", size)
        else:
            prefix = bytes([0x80 | opcode, 0x80 | 127]) + struct.pack("!Q", size)
        self.sock.sendall(prefix + mask + bytes(v ^ mask[i % 4] for i, v in enumerate(content)))

    def recv_message(self):
        content = bytearray()
        while True:
            first, second = self.recv_bytes(2)
            opcode, finished = first & 0xF, first & 0x80
            length = second & 0x7F
            if length == 126:
                length = struct.unpack("!H", self.recv_bytes(2))[0]
            elif length == 127:
                length = struct.unpack("!Q", self.recv_bytes(8))[0]
            if length > 8_000_000:
                raise RuntimeError("CDP response exceeds allowed size")
            masked = second & 0x80
            mask = self.recv_bytes(4) if masked else None
            data = self.recv_bytes(length)
            if mask:
                data = bytes(v ^ mask[i % 4] for i, v in enumerate(data))
            if opcode == 9:
                self.send_frame(10, data)
                continue
            if opcode == 8:
                raise RuntimeError("Chrome closed CDP session")
            content.extend(data)
            if finished:
                return json.loads(content.decode())

    def call(self, method, params=None):
        self.seq += 1
        uid = self.seq
        self.send_frame(1, json.dumps({"id": uid, "method": method, "params": params or {}}).encode())
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline:
            item = self.recv_message()
            if item.get("id") == uid:
                if "error" in item:
                    raise RuntimeError(f"CDP {method} error: {item['error'].get('message')}")
                return item.get("result", {})
        raise TimeoutError(f"CDP {method} timed out")

    def js(self, source):
        r = self.call("Runtime.evaluate", {
            "expression": source, "returnByValue": True,
            "awaitPromise": True, "userGesture": True,
        })
        if "exceptionDetails" in r:
            desc = r["exceptionDetails"].get("text", "JS failed")
            raise RuntimeError(f"Browser JS failed: {desc}")
        return r.get("result", {}).get("value")

    def wait(self, javascript, *, label, timeout=35):
        until = time.monotonic() + timeout
        while time.monotonic() < until:
            if self.js(javascript):
                return
            time.sleep(0.25)
        summary = self.js("document.body?.innerText.slice(0,1400)")
        raise AssertionError(f"Browser timed out: {label}; visible text: {summary!r}")


def find_browser():
    for _ in range(60):
        try:
            with urlopen(CHROME + "/json/list", timeout=2) as response:
                entries = json.load(response)
            pages = [x for x in entries if x.get("type") == "page"]
            if pages:
                return pages[0]["webSocketDebuggerUrl"]
        except (OSError, ValueError, KeyError):
            pass
        time.sleep(0.25)
    raise RuntimeError("Chrome CDP socket unavailable")


def screenshot(browser, name):
    folder = os.getenv("BIZLENS_BROWSER_SCREENSHOT_DIR")
    if not folder:
        return
    output = browser.call("Page.captureScreenshot", {
        "format": "png", "captureBeyondViewport": False,
    })
    with open(os.path.join(folder, name), "wb") as handle:
        handle.write(base64.b64decode(output["data"]))


def main():
    browser = Cdp(find_browser())
    try:
        browser.call("Page.enable")
        browser.call("Runtime.enable")
        browser.call("Page.navigate", {"url": WEB})
        browser.wait("!!document.querySelector('#hero-title')", label="SSR landing")
        browser.wait("document.querySelectorAll('button').length > 3", label="landing controls")
        time.sleep(1)  # Allow Next.js to hydrate click handlers after SSR.
        browser.js("Array.from(document.querySelectorAll('button')).find(b=>b.textContent.includes('Try Interactive Demo')).click()")
        browser.wait(
            "!!Array.from(document.querySelectorAll('button')).find(b=>b.textContent.trim().includes('Base / USDC'))",
            label="sample analysis loaded", timeout=50,
        )
        print("BROWSER PASS: Chrome click loads commerce workspace", flush=True)
        browser.js("Array.from(document.querySelectorAll('button')).find(b=>b.textContent.trim().includes('Base / USDC')).click()")
        browser.wait("document.body.innerText.includes('Match an invoice to transaction evidence.')", label="Base panel")
        browser.js("Array.from(document.querySelectorAll('button')).find(b=>b.textContent.includes('Run offline sample')).click()")
        browser.wait("document.body.innerText.includes('SYNTH-003')", label="synthetic Base data")
        visible = browser.js("document.querySelector('.base-evidence-output')?.innerText")
        for expected in (
            "SYNTH-001", "SYNTH-002", "SYNTH-003",
            "unverified", "Amount is below invoice", "Not found in supplied data",
        ):
            assert expected.lower() in visible.lower(), (expected, visible)
        print("BROWSER PASS: three synthetic outcomes are clearly unverified", flush=True)
        screenshot(browser, "base-desktop.png")

        # This smoke never submits a live inspection, even to the disabled API.
        assert browser.js("document.querySelector('input[type=password]') !== null")
        assert browser.js("!document.body.innerText.includes('Send USDC')")
        browser.call("Emulation.setDeviceMetricsOverride", {
            "width": 390, "height": 844, "deviceScaleFactor": 1, "mobile": True,
        })
        time.sleep(0.8)
        metrics = browser.js(
            "({innerWidth: innerWidth, scrollWidth: document.documentElement.scrollWidth, "
            "heading: !!document.querySelector('#base-offline-heading')})"
        )
        assert metrics["heading"] and metrics["scrollWidth"] <= metrics["innerWidth"] + 2, metrics
        print("BROWSER PASS: 390px mobile view and no horizontal overflow", flush=True)
        screenshot(browser, "base-mobile.png")
    finally:
        browser.sock.close()


if __name__ == "__main__":
    main()
