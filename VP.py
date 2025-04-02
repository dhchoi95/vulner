from flask import Flask, render_template, request
from playwright.sync_api import sync_playwright

app = Flask(__name__)

# 브라우저 실행
p = sync_playwright().start()
browser = p.chromium.launch(headless=False)
context = browser.new_context()
page = context.new_page()

def login():
    page.goto("http://192.168.20.79/#/login?redirect=%2Fproject")
    page.fill('input[name="username"]', "eogjs95@nextchip.com")
    page.fill('input[name="password"]', "choi1022!")
    page.click('text=로그인')
    page.wait_for_timeout(3000)

def open_doc(title):
    container = page.locator("div.loading-wrapper.el-row")
    container.wait_for(timeout=10000)
    target = container.locator(f"text={title}")
    if target.count() > 0:
        target.first.click(click_count=2)
    else:
        print(f"❌ {title} 메뉴 항목을 찾을 수 없습니다")

def open_task(menu_name):
    container = page.locator("div.el-scrollbar__view")
    container.wait_for(timeout=10000)
    task_item = container.locator(f"text={menu_name}")
    if task_item.count() > 0:
        task_item.first.click(click_count=2)
    else:
        print(f"❌ {menu_name} 메뉴 항목을 찾을 수 없습니다")

# 첫 페이지 - 입력받는 UI
@app.route("/")
def index():
    return render_template("index.html")

# 문서 열기 요청 처리
@app.route('/open_doc', methods=['POST'])
def open_doc_route():
    title = request.form.get('title')
    try:
        open_doc(title)  # 함수 호출
        return f"📄 문서 '{title}' 열기 완료!"
    except Exception as e:
        return f"❌ 문서 열기 실패: {str(e)}"

@app.route('/open_task', methods=['POST'])
def open_task_route():
    menu = request.form.get('menu')
    try:
        open_task(menu)  # 함수 호출
        return f"🗂 메뉴 '{menu}' 열기 완료!"
    except Exception as e:
        return f"❌ 메뉴 열기 실패: {str(e)}"


if __name__ == "__main__":
    login()
    app.run(debug=True, use_reloader=False, threaded=False)
