import sqlite3

def create_database():
    conn = sqlite3.connect("scan_results.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT,
            domain TEXT,
            result TEXT,
            confidence REAL,
            registrar TEXT,
            creation_date TEXT,
            expiry_date TEXT,
            country TEXT,
            domain_age INTEGER,
            scan_time TEXT
        )
    """)

    conn.commit()
    conn.close()


def save_scan_result(scan_result):
    conn = sqlite3.connect("scan_results.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO scans (
            url, domain, result, confidence, registrar,
            creation_date, expiry_date, country, domain_age, scan_time
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        scan_result["url"],
        scan_result["domain"],
        scan_result["result"],
        float(scan_result["confidence"]),
        scan_result["registrar"],
        str(scan_result["creation_date"]),
        str(scan_result["expiry_date"]),
        scan_result["country"],
        scan_result["domain_age"],
        scan_result["scan_time"]
    ))

    conn.commit()
    conn.close()