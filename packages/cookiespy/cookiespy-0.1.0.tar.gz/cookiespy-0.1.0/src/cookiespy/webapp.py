from flask import Flask, request, render_template_string, send_file
from cookiespy import fetch_cookies
from cookiespy.exporter import export_to_json, export_to_csv

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>CookieSpy Web</title>
</head>
<body>
    <h2>CookieSpy Web Interface</h2>
    <form method="post">
        <input type="text" name="url" placeholder="Masukkan URL" size="50" required>
        <button type="submit">Fetch Cookies</button>
    </form>
    {% if cookies %}
        <h3>Cookies:</h3>
        <pre>{{ cookies }}</pre>
        <a href="/export/json">Export JSON</a> | 
        <a href="/export/csv">Export CSV</a>
    {% endif %}
</body>
</html>
"""

cookies_cache = {}

@app.route("/", methods=["GET", "POST"])
def index():
    global cookies_cache
    cookies = None
    if request.method == "POST":
        url = request.form.get("url")
        cookies = fetch_cookies(url)
        cookies_cache = cookies
    return render_template_string(HTML_TEMPLATE, cookies=cookies)

@app.route("/export/<fmt>")
def export(fmt):
    if not cookies_cache:
        return "Tidak ada cookies untuk diexport"
    if fmt == "json":
        filename = export_to_json(cookies_cache)
        return send_file(filename, as_attachment=True)
    elif fmt == "csv":
        filename = export_to_csv(cookies_cache)
        return send_file(filename, as_attachment=True)
    return "Format tidak dikenali"
    
if __name__ == "__main__":
    app.run(debug=True)
