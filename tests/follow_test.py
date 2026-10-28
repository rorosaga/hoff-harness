"""End-to-end check that a point stays on a moving web target, reports the click, and
puts itself away. Needs macOS, Chrome with browser-harness connected, and
hoff-harness-website's demos/record.py (for the guest window and the hand):

    uv run --with pyobjc-framework-Cocoa --with pyobjc-framework-Quartz \
        --with pyobjc-framework-ApplicationServices --with pillow python3 tests/follow_test.py
"""
import functools, http.server, json, os, subprocess, sys, threading, time

HERE = os.path.dirname(os.path.abspath(__file__))
HOFF = os.path.join(HERE, "..", "skills", "hoff-harness", "scripts", "hoff-harness")
sys.argv = ["x"]
sys.path.insert(0, os.path.expanduser("~/code/hoff-harness-website/demos"))
import record as r  # noqa: E402

PORT = 8766
URL = f"http://localhost:{PORT}/scroll-dialog.html"
srv = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), functools.partial(http.server.SimpleHTTPRequestHandler, directory=HERE))
threading.Thread(target=srv.serve_forever, daemon=True).start()

fails = []
def check(name, ok, detail=""):
    print(("ok   " if ok else "FAIL ") + name + (f"  ({detail})" if detail else ""), flush=True)
    if not ok:
        fails.append(name)

def status():
    return r.overlay_status()

def page(js):
    r.web_js(f"localhost:{PORT}", js)

def point(*extra):
    return subprocess.Popen([HOFF, "point", "--tab", f"localhost:{PORT}", "--css", "#target", "--title", "Step 1 of 1",
                             "--say", "Click Save changes.", *extra], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

hidden = r.only("Google Chrome")
try:
    r.chrome_guest(URL, bounds=(156, 110, 1200, 750))
    time.sleep(1.5)

    # 1. scrolling the dialog, the window moving, scrolling it out of view and back, then the click
    p = point("--wait-click", "--timeout", "40")
    time.sleep(4)
    s0 = status()
    check("points at the target, scrolled into view", bool(s0.get("ring")), str(s0.get("ring")))
    page("document.getElementById('dialog').scrollTop += 60")
    time.sleep(0.8)
    s1 = status()
    dy = s1["ring"][1] - s0["ring"][1] if s1.get("ring") else None
    check("follows a scroll inside the dialog", dy is not None and abs(dy + 60) < 3, f"moved {dy}")
    subprocess.run(["browser-harness"], input=r.GUEST_PY + """
for t in guest:
    wid = cdp("Browser.getWindowForTarget", targetId=t["targetId"])["windowId"]
    cdp("Browser.setWindowBounds", windowId=wid, bounds={"left": 236, "top": 110})
""", text=True, capture_output=True)
    time.sleep(1.0)
    s2 = status()
    dx = s2["ring"][0] - s1["ring"][0] if s2.get("ring") else None
    check("follows the window when it moves", dx is not None and abs(dx - 80) < 3, f"moved {dx}")
    page("window.hoffWas = document.getElementById('dialog').scrollTop; document.getElementById('dialog').scrollTop += 500")
    time.sleep(0.8)
    s3 = status()
    check("scrolled out of view: no ring, still shown", s3.get("ring") is None and s3.get("shown"), str(s3.get("ring")))
    page("document.getElementById('dialog').scrollTop = window.hoffWas")
    time.sleep(0.8)
    s4 = status()
    check("scrolled back: the ring is back on it", bool(s4.get("ring")) and abs(s4["ring"][1] - s2["ring"][1]) < 3, str(s4.get("ring")))
    x, y, w, h = s4["ring"]
    r.person.click((x + w / 2, y + h / 2), 0.6)
    out = p.communicate(timeout=10)[0]
    check("the click is reported", p.returncode == 0 and "clicked" in out, out.strip().splitlines()[-1])
    time.sleep(0.4)
    check("it says Done", status().get("talking") is True)
    time.sleep(1.8)
    check("then puts itself away", status().get("shown") is False)

    # 2. the dialog closes without a click on the target
    page("location.reload()")
    time.sleep(2)
    p = point("--wait-click", "--timeout", "40")
    time.sleep(4)
    page("document.getElementById('dialog').remove()")
    t0 = time.time()
    out = p.communicate(timeout=10)[0]
    check("a target that goes away ends the wait (exit 10)", p.returncode == 10, f"exit {p.returncode} after {time.time() - t0:.1f}s")
    time.sleep(0.5)
    check("and the guide is put away", status().get("shown") is False)
finally:
    subprocess.run([HOFF, "hide"])
    r.chrome_guest_close()
    r.chrome_restore()
    r.show_again(hidden)
    srv.shutdown()

print("\n" + ("all passed" if not fails else f"{len(fails)} failed: {', '.join(fails)}"))
sys.exit(1 if fails else 0)
