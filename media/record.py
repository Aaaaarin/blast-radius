"""Record the demo: screenshots for the Devpost gallery plus a raw screen capture."""
import os, subprocess, sys, time, shutil
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "media", "raw")
os.makedirs(RAW, exist_ok=True)
URL = "http://127.0.0.1:8000/"


def demo(arg):
    subprocess.call([sys.executable, "demo.py", arg], cwd=ROOT)


demo("reset")
with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    ctx = b.new_context(viewport={"width": 1280, "height": 720}, record_video_dir=RAW, record_video_size={"width": 1280, "height": 720})
    page = ctx.new_page()
    page.goto(URL)
    page.wait_for_selector("#graph svg")
    time.sleep(4)                                   # 0-4s clean tree
    page.screenshot(path=os.path.join(ROOT, "media", "01-clean.png"))
    demo("break")
    time.sleep(1)
    page.click("#refresh")
    page.wait_for_function("document.querySelector('#t-changed').textContent === '1'")
    time.sleep(5)                                   # 5-11s blast radius lit up
    page.screenshot(path=os.path.join(ROOT, "media", "02-blast-radius.png"))
    page.click("#run-impacted")
    page.wait_for_selector("#result:not([hidden])")
    time.sleep(6)                                   # 12-18s impacted tests fail
    page.screenshot(path=os.path.join(ROOT, "media", "03-impacted-tests-fail.png"))
    page.click("#run-all")
    page.wait_for_function("document.querySelector('#res-label').textContent.includes('(all)')")
    time.sleep(5)                                   # 19-24s full suite for comparison
    page.screenshot(path=os.path.join(ROOT, "media", "04-run-all.png"))
    demo("reset")
    time.sleep(1)
    page.click("#refresh")
    page.wait_for_function("document.querySelector('#t-changed').textContent === '0'")
    time.sleep(3)
    ctx.close()
    b.close()

vids = [f for f in os.listdir(RAW) if f.endswith(".webm")]
shutil.move(os.path.join(RAW, vids[0]), os.path.join(RAW, "screen.webm"))
print("recorded", os.path.join(RAW, "screen.webm"))
