from rich.console import Console
from rich.table import Table
from time import sleep
from log_analyzer.log_db import LogDB

console = Console()

def display_loop(refresh: int = 2):
    db = LogDB()
    try:
        while True:
            console.clear()
            table = Table(title="Resumo de Logs")
            table.add_column("Categoria")
            table.add_column("Quantidade", justify="right")
            for cat, count in db.count_by_category():
                table.add_row(cat, str(count))
            console.print(table)

            logs_table = Table(title="Ultimos Eventos")
            logs_table.add_column("ID")
            logs_table.add_column("Timestamp")
            logs_table.add_column("Host")
            logs_table.add_column("Severidade")
            logs_table.add_column("Anomalia")
            logs_table.add_column("Mensagem")
            for row in db.fetch_logs(limit=10):
                log_id, ts, host, msg, category, severity, anomaly_score, mal = row
                tag = "*" if mal else ""
                logs_table.add_row(str(log_id), str(ts), host, severity + tag, f"{anomaly_score:.2f}", msg)
            console.print(logs_table)
            sleep(refresh)
    finally:
        db.close()

if __name__ == '__main__':
    display_loop()
