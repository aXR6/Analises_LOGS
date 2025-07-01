from flask import Flask, render_template_string, jsonify, request
from log_analyzer.log_db import LogDB

app = Flask(__name__)
TEMPLATE = """
<!doctype html>
<html>
<head>
    <title>Monitor de Logs</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class=\"container my-4\">
<h1 class=\"mb-4\">Eventos Recentes</h1>
<div class=\"mb-3\">
  <span class=\"badge bg-info text-dark\">INFO</span>
  <span class=\"badge bg-warning text-dark\">WARNING</span>
  <span class=\"badge bg-danger\">ERROR</span>
  <span class=\"badge bg-danger text-light\">Ataque</span>
</div>
<table id=\"log-table\" class=\"table table-striped\">
<thead>
<tr><th>ID</th><th>Timestamp</th><th>Host</th><th>Severidade</th><th>Anomalia</th><th>Mensagem</th></tr>
</thead>
<tbody>
{% for row in logs %}
<tr class="{% if row[7] %}table-danger{% endif %}">
<td>{{row[0]}}</td><td>{{row[1]}}</td><td>{{row[2]}}</td>
<td class="{{ severity_colors.get(row[5], '') }}">{{row[5]}}{{ '*' if row[7] else '' }}</td><td>{{'%.2f'|format(row[6])}}</td><td>{{row[3]}}</td>
</tr>
{% endfor %}
</tbody>
</table>
<script>
const severityColors = {{ severity_colors | tojson }};
async function fetchLogs() {
  const resp = await fetch('/api/logs');
  if (!resp.ok) return;
  const data = await resp.json();
  const tbody = document.querySelector('#log-table tbody');
  tbody.innerHTML = '';
  for (const row of data.logs) {
    const tr = document.createElement('tr');
    tr.innerHTML = `
        <td>${row[0]}</td>
        <td>${row[1]}</td>
        <td>${row[2]}</td>
        <td class="${severityColors[row[5]] || ''}">${row[5]}${row[7] ? '*' : ''}</td>
        <td>${row[6].toFixed(2)}</td>
        <td>${row[3]}</td>
    `;
    if (row[7]) {
        tr.classList.add('table-danger');
    }
    tbody.appendChild(tr);
  }
}
fetchLogs();
setInterval(fetchLogs, 5000);
</script>
</body>
</html>
"""

@app.route('/')
def index():
    db = LogDB()
    logs = list(db.fetch_logs(limit=50))
    db.close()
    severity_colors = {'INFO': 'text-info', 'WARNING': 'text-warning', 'ERROR': 'text-danger'}
    return render_template_string(TEMPLATE, logs=logs, severity_colors=severity_colors)


@app.route('/api/logs')
def api_logs():
    limit = int(request.args.get('limit', 50))
    db = LogDB()
    logs = list(db.fetch_logs(limit=limit))
    db.close()
    return jsonify({'logs': logs})

if __name__ == '__main__':
    app.run(debug=True)
