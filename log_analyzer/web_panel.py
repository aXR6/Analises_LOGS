from flask import Flask, render_template_string, jsonify, request
from log_analyzer.log_db import LogDB
from log_analyzer.llm_analysis import analyze_log

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
<div class=\"d-flex justify-content-between mb-3\">
  <form id=\"filter-form\" class=\"d-flex gap-2\" method=\"get\">
    <select name=\"severity\" class=\"form-select form-select-sm\">
      <option value=\"\">Todas</option>
      <option value=\"INFO\">INFO</option>
      <option value=\"WARNING\">WARNING</option>
      <option value=\"ERROR\">ERROR</option>
    </select>
    <button class=\"btn btn-sm btn-primary\" type=\"submit\">Filtrar</button>
  </form>
  <div>
    <a href=\"?page={{ page-1 if page>1 else 1 }}{% if severity %}&severity={{ severity }}{% endif %}\" class=\"btn btn-sm btn-secondary\">Anterior</a>
    <a href=\"?page={{ page+1 }}{% if severity %}&severity={{ severity }}{% endif %}\" class=\"btn btn-sm btn-secondary\">Próximo</a>
  </div>
</div>
<table id=\"log-table\" class=\"table table-striped\">
<thead>
<tr><th>ID</th><th>Timestamp</th><th>Host</th><th>Severidade</th><th>Anomalia</th><th>Semantica</th><th>Mensagem</th><th></th></tr>
</thead>
<tbody>
{% for row in logs %}
<tr class="{% if row[7] or row[8] %}table-danger{% endif %}">
<td>{{row[0]}}</td><td>{{row[1]}}</td><td>{{row[2]}}</td>
<td class="{{ severity_colors.get(row[5], '') }}">{{row[5]}}{{ '*' if row[7] else '' }}</td><td>{{'%.2f'|format(row[6])}}</td><td>{{ 'sim' if row[8] else 'nao' }}</td><td>{{row[3]}}</td><td><button class="btn btn-sm btn-outline-primary" onclick="analyzeLog({{row[0]}})">Analisar</button></td>
</tr>
{% endfor %}
</tbody>
</table>
<script>
const severityColors = {{ severity_colors | tojson }};
async function fetchLogs(page = {{ page }}) {
  const params = new URLSearchParams({page: page, severity: '{{ severity or '' }}'});
  const resp = await fetch('/api/logs?' + params.toString());
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
        <td>${row[8] ? 'sim' : 'nao'}</td>
        <td>${row[3]}</td>
        <td><button class="btn btn-sm btn-outline-primary" onclick="analyzeLog(${row[0]})">Analisar</button></td>
    `;
    if (row[7] || row[8]) {
        tr.classList.add('table-danger');
    }
    tbody.appendChild(tr);
  }
}
async function analyzeLog(id) {
  const resp = await fetch('/api/analyze/' + id);
  if (!resp.ok) { alert('erro ao analisar'); return; }
  const data = await resp.json();
  alert(data.result);
}
fetchLogs();
setInterval(fetchLogs, 5000);
</script>
</body>
</html>
"""

@app.route('/')
def index():
    page = int(request.args.get('page', 1))
    severity = request.args.get('severity')
    db = LogDB()
    logs = list(db.fetch_logs(limit=100, page=page, severity=severity))
    db.close()
    severity_colors = {'INFO': 'text-info', 'WARNING': 'text-warning', 'ERROR': 'text-danger'}
    return render_template_string(
        TEMPLATE,
        logs=logs,
        severity_colors=severity_colors,
        page=page,
        severity=severity,
    )


@app.route('/api/logs')
def api_logs():
    limit = int(request.args.get('limit', 100))
    page = int(request.args.get('page', 1))
    severity = request.args.get('severity')
    host = request.args.get('host')
    search = request.args.get('search')
    db = LogDB()
    logs = list(
        db.fetch_logs(
            limit=limit,
            page=page,
            severity=severity,
            host=host,
            search=search,
        )
    )
    db.close()
    return jsonify({'logs': logs})


@app.route('/api/analyze/<int:log_id>')
def api_analyze(log_id: int):
    result = analyze_log(log_id)
    return jsonify({'result': result})

if __name__ == '__main__':
    app.run(debug=True)
