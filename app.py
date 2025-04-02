from flask import Flask, render_template, request, redirect, url_for
from playwright.sync_api import sync_playwright
import sqlite3
from model import save_to_db, init_db  # 같이 추가
import math

app = Flask(__name__)

# ✅ DB에서 결과를 페이지 단위로 불러오기
def fetch_from_db(page, per_page=20):
    conn = sqlite3.connect("cwe.db")
    c = conn.cursor()
    offset = (page - 1) * per_page
    c.execute("SELECT COUNT(*) FROM cwe_results")
    total = c.fetchone()[0]
    total_pages = math.ceil(total / per_page)

    c.execute("SELECT keyword, title, link FROM cwe_results ORDER BY created_at DESC LIMIT ? OFFSET ?", (per_page, offset))
    results = c.fetchall()
    conn.close()
    return results, total_pages

def search_cwe(keyword):
    result_list = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://cwe.mitre.org/")
        page.fill('input[name="search"]', keyword)
        page.keyboard.press("Enter")
        page.wait_for_selector('.gsc-webResult')
        page_num = 1

        while True:
            results = page.locator('a.gs-title')
            count = results.count()
            for i in range(count):
                title = results.nth(i).inner_text()
                if "CWE-" in title:
                    href = results.nth(i).get_attribute("href")
                    result_list.append((title, href))

            next_button = page.locator(f'div.gsc-cursor-page:has-text("{page_num + 1}")')
            if next_button.count() > 0:
                next_button.first.click()
                page.wait_for_timeout(1000)
                page.wait_for_selector('.gsc-webResult')
                page_num += 1
            else:
                break

        browser.close()
    return result_list

@app.route("/reset_db", methods=["POST"])
def reset_db():
    init_db()
    return redirect(url_for("search"))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/search", methods=["POST", "GET"])
def search():
    if request.method == "POST":
        keyword = request.form.get("keyword")
        results = search_cwe(keyword)
        save_to_db(keyword, results)

    # ✅ GET 방식일 수도 있으므로 page 파라미터 처리
    page = int(request.args.get("page", 1))
    db_results, total_pages = fetch_from_db(page)
    return render_template("result.html", results=db_results, page=page, total_pages=total_pages)

if __name__ == "__main__":
    init_db()  # ✅ DB 없으면 생성
    app.run(debug=True)