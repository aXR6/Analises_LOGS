from flask import Flask, render_template_string
from log_analyzer.log_db import LogDB

app = Flask(__name__)
TEMPLATE = """
<!doctype html>
<title>Monitor de Logs</title>
<h1>Eventos Recentes</h1>
<table border=1>
<tr><th>ID</th><th>Timestamp</th><th>Host</th><th>Severidade</th><th>Anomalia</th><th>Mensagem</th></tr>
{% for row in logs %}
<tr>
<td>{{row[0]}}</td><td>{{row[1]}}</td><td>{{row[2]}}</td>
<td>{{row[5]}}{{ '*' if row[7] else '' }}</td><td>{{'%.2f'|format(row[6])}}</td><td>{{row[3]}}</td>
</tr>
{% endfor %}
</table>
"""

@app.route('/')
def index():
    db = LogDB()
    logs = list(db.fetch_logs(limit=50))
    db.close()
    return render_template_string(TEMPLATE, logs=logs)

if __name__ == '__main__':
    app.run(debug=True)
