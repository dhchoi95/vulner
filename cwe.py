from playwright.sync_api import sync_playwright

def search_cwe(keyword):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://cwe.mitre.org/")

        # 키워드 입력 및 검색 실행
        page.fill('input[name="search"]', keyword)
        page.keyboard.press("Enter")

        page.wait_for_selector('.gsc-webResult')
        page_num = 1

        while True:
            print(f"\n📄 페이지 {page_num} 처리 중...\n")

            # 검색 결과 중 CWE 항목만 추출
            results = page.locator('a.gs-title')
            count = results.count()
            for i in range(count):
                title = results.nth(i).inner_text()
                if "CWE-" in title:
                    href = results.nth(i).get_attribute("href")
                    print(f"[✔] {title} → {href}")

            # 다음 페이지 버튼 탐색
            next_button = page.locator(f'div.gsc-cursor-page:has-text("{page_num + 1}")')
            if next_button.count() > 0:
                next_button.first.click()
                page.wait_for_timeout(1000)
                page.wait_for_selector('.gsc-webResult')
                page_num += 1
            else:
                print("\n✅ 마지막 페이지까지 완료")
                break

        browser.close()

# 🔍 사용자 키워드 입력 받기
if __name__ == "__main__":
    keyword = input("검색할 키워드를 입력하세요: ")
    search_cwe(keyword)
