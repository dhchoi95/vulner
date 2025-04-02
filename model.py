# model.py
import sqlite3

def init_db():
    conn = sqlite3.connect('cwe.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS cwe_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            keyword TEXT,
            title TEXT,
            link TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_to_db(keyword, results):
    conn = sqlite3.connect('cwe.db')
    c = conn.cursor()
    for title, link in results:
        try:
            c.execute('''
                INSERT INTO cwe_results (keyword, title, link)
                VALUES (?, ?, ?)
            ''', (keyword, title, link))
        except sqlite3.IntegrityError:
            # 중복 링크 무시
            pass
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("✅ DB 초기화 완료 (cwe.db)")
