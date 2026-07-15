from flask import Flask, render_template, request
import joblib
import pandas as pd
import sqlite3
from urllib.parse import urlparse
from datetime import datetime

from feature_extraction import extract_features, normalize_url
from whois_lookup import get_whois_info
from database import save_scan_result

app = Flask(__name__)

model = joblib.load("phishing_model.pkl")


def extract_domain(url):
    url = normalize_url(url)

    parsed = urlparse(url)
    domain = parsed.netloc.lower()

    if domain.startswith("www."):
        domain = domain[4:]

    return domain


@app.route("/", methods=["GET", "POST"])
def home():
    result = None
    confidence = None
    url = None
    whois_info = None

    if request.method == "POST":
        url = normalize_url(request.form["url"])

        features = extract_features(url)
        features_df = pd.DataFrame([features])

        prediction = model.predict(features_df)[0]
        probabilities = model.predict_proba(features_df)[0]
        confidence = round(max(probabilities) * 100, 2)

        if prediction == 1:
            result = "Phishing"
        else:
            result = "Legitimate"

        domain = extract_domain(url)
        whois_info = get_whois_info(domain)

        scan_result = {
            "url": url,
            "domain": domain,
            "result": result,
            "confidence": confidence,
            "registrar": whois_info.get("registrar"),
            "creation_date": whois_info.get("creation_date"),
            "expiry_date": whois_info.get("expiry_date"),
            "country": whois_info.get("country"),
            "domain_age": whois_info.get("domain_age"),
            "scan_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        save_scan_result(scan_result)

    return render_template(
        "index.html",
        result=result,
        confidence=confidence,
        url=url,
        whois_info=whois_info
    )


@app.route("/history")
def history():
    conn = sqlite3.connect("scan_results.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            url,
            result,
            confidence,
            registrar,
            country,
            domain_age,
            scan_time
        FROM scans
        ORDER BY id DESC
    """)

    scans = cursor.fetchall()
    conn.close()

    return render_template("history.html", scans=scans)


@app.route("/dashboard")
def dashboard():
    conn = sqlite3.connect("scan_results.db")

    df = pd.read_sql_query(
        "SELECT * FROM scans",
        conn
    )

    conn.close()

    total_scans = len(df)

    total_phishing = len(
        df[df["result"] == "Phishing"]
    )

    total_legitimate = len(
        df[df["result"] == "Legitimate"]
    )

    average_confidence = round(
        df["confidence"].mean(),
        2
    )

    recent_scans = df.tail(5).iloc[::-1].values.tolist()

    # Timeline chart data
    df["scan_time"] = pd.to_datetime(df["scan_time"])

    phishing_df = df[df["result"] == "Phishing"]

    timeline_data = phishing_df.groupby(
        phishing_df["scan_time"].dt.date
    ).size()

    timeline_labels = [
        str(date)
        for date in timeline_data.index
    ]

    timeline_values = timeline_data.values.tolist()

    return render_template(
        "dashboard.html",
        total_scans=total_scans,
        total_phishing=total_phishing,
        total_legitimate=total_legitimate,
        average_confidence=average_confidence,
        recent_scans=recent_scans,
        phishing_count=total_phishing,
        legitimate_count=total_legitimate,
        timeline_labels=timeline_labels,
        timeline_values=timeline_values
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)