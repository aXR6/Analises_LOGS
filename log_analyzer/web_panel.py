from flask import Flask, render_template, jsonify, request, redirect, url_for
from log_analyzer.log_db import LogDB
from log_analyzer.llm_analysis import analyze_log, analyze_network_event
from log_analyzer.attack_detection import count_attack_types, classify_attack
from log_analyzer.attack_detection import extract_ips
import os
from pathlib import Path


app = Flask(__name__)

SEVERITY_COLORS = {
    'INFO': 'text-info',
    'WARNING': 'text-warning',
    'ERROR': 'text-danger'
}

NIDS_COLORS = {
    # Classes used to color network labels. Using Bootstrap badge styles
    # provides good contrast in both light and dark themes.
    'normal': 'badge text-bg-secondary',
    'dos': 'badge text-bg-danger',
    'port scan': 'badge text-bg-warning',
    'brute force': 'badge text-bg-info',
    'pingscan': 'badge text-bg-primary'
}


def get_network_info() -> tuple[list[str], list[str]]:
    """Return active interfaces and those with traffic."""
    interfaces = []
    try:
        interfaces = os.listdir('/sys/class/net')
    except Exception:
        pass
    active: list[str] = []
    activity: list[str] = []
    stats: dict[str, list[str]] = {}
    try:
        with open('/proc/net/dev') as f:
            lines = f.readlines()[2:]
        for line in lines:
            parts = line.split()
            iface = parts[0].strip(':')
            stats[iface] = parts
    except Exception:
        pass
    for iface in interfaces:
        try:
            state = Path(f'/sys/class/net/{iface}/operstate').read_text().strip()
            if state == 'up':
                active.append(iface)
        except Exception:
            pass
        if iface in stats:
            rx = int(stats[iface][1])
            tx = int(stats[iface][9])
            if rx > 0 or tx > 0:
                activity.append(iface)
    return active, activity


@app.route('/')
def index():
    return redirect(url_for('logs_page'))


@app.route('/logs')
def logs_page():
    page = int(request.args.get('page', 1))
    severity = request.args.get('severity')
    program = request.args.get('program')
    db = LogDB()
    logs = []
    for row in db.fetch_logs(limit=100, page=page, severity=severity, program=program):
        attack = classify_attack(row[5])
        logs.append(list(row) + [attack])
    db.close()
    return render_template(
        'logs.html',
        logs=logs,
        severity_colors=SEVERITY_COLORS,
        page=page,
        severity=severity,
        program=program,
        menu='logs'
    )


@app.route('/analyzed')
def analyzed_page():
    return render_template(
        'analyzed.html',
        severity_colors=SEVERITY_COLORS,
        menu='analyzed'
    )


@app.route('/network')
def network_page():
    page = int(request.args.get('page', 1))
    source = request.args.get('source')
    db = LogDB()
    sources = list(db.list_network_sources())
    db.close()
    return render_template(
        'network.html',
        severity_colors=SEVERITY_COLORS,
        label_colors=NIDS_COLORS,
        sources=sources,
        page=page,
        source=source,
        menu='network'
    )


@app.route('/api/analyzed')
def api_analyzed():
    limit = int(request.args.get('limit', 100))
    page = int(request.args.get('page', 1))
    db = LogDB()
    logs = list(db.fetch_analyzed_logs(limit=limit, page=page))
    db.close()
    return jsonify({'logs': logs})


@app.route('/api/analyzed_network')
def api_analyzed_network():
    limit = int(request.args.get('limit', 100))
    page = int(request.args.get('page', 1))
    db = LogDB()
    events = list(db.fetch_analyzed_network_events(limit=limit, page=page))
    db.close()
    return jsonify({'events': events})


@app.route('/api/network')
def api_network():
    limit = int(request.args.get('limit', 100))
    page = int(request.args.get('page', 1))
    source = request.args.get('source')
    label = request.args.get('label')
    db = LogDB()
    events = list(db.fetch_network_events(limit=limit, page=page, source=source, label=label))
    db.close()
    return jsonify({'events': events})


@app.route('/api/logs')
def api_logs():
    limit = int(request.args.get('limit', 100))
    page = int(request.args.get('page', 1))
    severity = request.args.get('severity')
    host = request.args.get('host')
    program = request.args.get('program')
    search = request.args.get('search')
    db = LogDB()
    logs = []
    for row in db.fetch_logs(
        limit=limit,
        page=page,
        severity=severity,
        host=host,
        program=program,
        search=search,
    ):
        attack = classify_attack(row[5])
        logs.append(list(row) + [attack])
    db.close()
    return jsonify({'logs': logs})


@app.route('/api/stats')
def api_stats():
    db = LogDB()
    severity_counts = dict(db.count_by_severity())
    malicious_msgs = list(db.fetch_recent_malicious(limit=200))
    label_counts = dict(db.count_network_by_label())
    db.close()
    attacks = count_attack_types(malicious_msgs)
    active, activity = get_network_info()
    return jsonify({
        'severity': severity_counts,
        'attacks': attacks,
        'interfaces': {'active': active, 'activity': activity},
        'network_labels': label_counts
    })


@app.route('/api/alerts')
def api_alerts():
    db = LogDB()
    rows = list(db.fetch_recent_attack_logs(limit=5))
    db.close()
    alerts = []
    for ts, host, msg in rows:
        attack = classify_attack(msg)
        src, dst = extract_ips(msg)
        if not dst:
            dst = host
        alerts.append({'timestamp': ts, 'src': src, 'dst': dst, 'attack': attack})
    return jsonify({'alerts': alerts})


@app.route('/api/counts')
def api_counts():
    """Return total counts for logs, analyzed logs and network events."""
    db = LogDB()
    counts = {
        'logs': db.count_logs(),
        'analyzed': db.count_analyzed_logs() + db.count_analyzed_network_events(),
        'network': db.count_network_events(),
    }
    db.close()
    return jsonify(counts)


@app.route('/api/analyze/<int:log_id>')
def api_analyze(log_id: int):
    result = analyze_log(log_id)
    return jsonify({'result': result})


@app.route('/api/analyze_network/<int:event_id>')
def api_analyze_network(event_id: int):
    result = analyze_network_event(event_id)
    return jsonify({'result': result})

if __name__ == '__main__':
    app.run(debug=True)
