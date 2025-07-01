from flask import Flask, render_template_string, jsonify, request, redirect, url_for
from log_analyzer.log_db import LogDB
from log_analyzer.llm_analysis import analyze_log

app = Flask(__name__)

BASE_TEMPLATE = """
<!doctype html>
<html>
<head>
    <title>Log Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
<nav class=\"navbar navbar-dark bg-dark mb-4\">
  <div class=\"container-fluid d-flex justify-content-between\">
    <span class=\"navbar-brand mb-0 h1\">Log Dashboard</span>
    <ul class=\"navbar-nav flex-row gap-3\">
      <li class=\"nav-item\"><a href=\"{{ url_for('logs_page') }}\" class=\"nav-link {% if menu=='logs' %}active text-white{% else %}text-secondary{% endif %}\">Logs</a></li>
      <li class=\"nav-item\"><a href=\"{{ url_for('analyzed_page') }}\" class=\"nav-link {% if menu=='analyzed' %}active text-white{% else %}text-secondary{% endif %}\">Analisados</a></li>
    </ul>
  </div>
</nav>
<div class=\"container my-4\">
{% block content %}{% endblock %}
</div>
<script src=\"https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js\"></script>
</body>
</html>
"""

LOGS_TEMPLATE = """
{% extends base %}
{% block content %}
<h2 class=\"mb-4\">Eventos Recentes</h2>
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
<tr><th>ID</th><th>Timestamp</th><th>Host</th><th>Programa</th><th>Severidade</th><th>Anomalia</th><th>Semantica</th><th>Mensagem</th><th></th></tr>
</thead>
<tbody>
{% for row in logs %}
<tr class="{% if row[8] or row[9] %}table-danger{% endif %}">
<td>{{row[0]}}</td><td>{{row[1]}}</td><td>{{row[2]}}</td><td><a href="?program={{row[3]}}">{{row[3]}}</a></td>
<td class="{{ severity_colors.get(row[6], '') }}">{{row[6]}}{{ '*' if row[8] else '' }}</td><td>{{'%.2f'|format(row[7])}}</td><td>{{ 'sim' if row[9] else 'nao' }}</td><td>{{row[4]}}</td><td><button class="btn btn-sm btn-outline-primary" onclick="analyzeLog({{row[0]}})">Analisar</button></td>
</tr>
{% endfor %}
</tbody>
</table>
<!-- Modal -->
<div class="modal fade" id="analysisModal" tabindex="-1" aria-hidden="true">
  <div class="modal-dialog modal-lg">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title">Resultado da Análise</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
      </div>
      <div class="modal-body" id="analysis-content"></div>
    </div>
</div>
</div>
</div>
<script>
const severityColors = {{ severity_colors | tojson }};
async function fetchLogs(page = {{ page }}) {
  const params = new URLSearchParams({page: page, severity: '{{ severity or '' }}', program: '{{ program or '' }}'});
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
        <td><a href="?program=${row[3]}">${row[3]}</a></td>
        <td class="${severityColors[row[6]] || ''}">${row[6]}${row[8] ? '*' : ''}</td>
        <td>${row[7].toFixed(2)}</td>
        <td>${row[9] ? 'sim' : 'nao'}</td>
        <td>${row[4]}</td>
        <td><button class="btn btn-sm btn-outline-primary" onclick="analyzeLog(${row[0]})">Analisar</button></td>
    `;
    if (row[8] || row[9]) {
        tr.classList.add('table-danger');
    }
    tbody.appendChild(tr);
  }
}
async function analyzeLog(id) {
  const resp = await fetch('/api/analyze/' + id);
  if (!resp.ok) { alert('erro ao analisar'); return; }
  const data = await resp.json();
  const modalBody = document.getElementById('analysis-content');
  modalBody.textContent = data.result;
  const modal = new bootstrap.Modal(document.getElementById('analysisModal'));
  modal.show();
}
fetchLogs();
setInterval(fetchLogs, 5000);
</script>
{% endblock %}
"""

ANALYZED_TEMPLATE = """
{% extends base %}
{% block content %}
<h2 class=\"mb-4\">Logs Analisados</h2>
<table id=\"analyzed-table\" class=\"table table-striped\">
<thead>
<tr><th>ID Original</th><th>Timestamp</th><th>Programa</th><th>Severidade</th><th>Anomalia</th><th>Mensagem</th><th>Resumo</th></tr>
</thead>
<tbody></tbody>
</table>
<script>
async function fetchAnalyzed(page=1) {
  const resp = await fetch('/api/analyzed?page='+page);
  if (!resp.ok) return;
  const data = await resp.json();
  const tbody = document.querySelector('#analyzed-table tbody');
  tbody.innerHTML = '';
  for (const row of data.logs) {
    const tr = document.createElement('tr');
    tr.innerHTML = `
        <td>${row[0]}</td>
        <td>${row[1]}</td>
        <td>${row[3]}</td>
        <td>${row[6]}</td>
        <td>${row[7].toFixed(2)}</td>
        <td>${row[4]}</td>
        <td>${row[10]}</td>`;
    tbody.appendChild(tr);
  }
}
fetchAnalyzed();
</script>
{% endblock %}
"""

@app.route('/')
def index():
    return redirect(url_for('logs_page'))


@app.route('/logs')
def logs_page():
    page = int(request.args.get('page', 1))
    severity = request.args.get('severity')
    program = request.args.get('program')
    db = LogDB()
    logs = list(db.fetch_logs(limit=100, page=page, severity=severity, program=program))
    db.close()
    severity_colors = {'INFO': 'text-info', 'WARNING': 'text-warning', 'ERROR': 'text-danger'}
    return render_template_string(
        LOGS_TEMPLATE,
        base=BASE_TEMPLATE,
        logs=logs,
        severity_colors=severity_colors,
        page=page,
        severity=severity,
        program=program,
        menu='logs'
    )


@app.route('/analyzed')
def analyzed_page():
    return render_template_string(
        ANALYZED_TEMPLATE,
        base=BASE_TEMPLATE,
        menu='analyzed'
    )


@app.route('/api/analyzed')
def api_analyzed():
    limit = int(request.args.get('limit', 100))
    page = int(request.args.get('page', 1))
    db = LogDB()
    logs = list(db.fetch_analyzed_logs(limit=limit, page=page))
    db.close()
    return jsonify({'logs': logs})


@app.route('/api/logs')
def api_logs():
    limit = int(request.args.get('limit', 100))
    page = int(request.args.get('page', 1))
    severity = request.args.get('severity')
    host = request.args.get('host')
    program = request.args.get('program')
    search = request.args.get('search')
    db = LogDB()
    logs = list(
        db.fetch_logs(
            limit=limit,
            page=page,
            severity=severity,
            host=host,
            program=program,
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
