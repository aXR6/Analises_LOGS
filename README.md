# Analise de Logs com rsyslog

Este projeto coleta logs gerados pelo `rsyslog`, armazena em um banco de dados
SQLite e fornece dois paineis de monitoramento:

- **Painel de terminal** utilizando a biblioteca `rich`.
 - **Painel web** simples utilizando Flask.

Logs considerados maliciosos geram alertas imediatos exibidos no terminal.

Para configuracoes de alto desempenho do `rsyslog` em ambientes Debian 12
consulte [docs/rsyslog_optimization.md](docs/rsyslog_optimization.md).

## Requisitos

- Python 3.8+
- Dependências listadas em `requirements.txt`

## Instalacao

```bash
pip install -r requirements.txt
```

## Uso

1. Configure o `rsyslog` para gravar seus eventos em `rsyslog.log` na raiz do
   projeto. Para uma configuracao mais eficiente, consulte o arquivo
   [docs/rsyslog_optimization.md](docs/rsyslog_optimization.md) e salve o
   conteudo sugerido em `/etc/rsyslog.d/50-log_analyzer.conf`.

   Caso prefira uma configuracao minima, o seguinte exemplo tambem funciona:

   ```
   *.* @@127.0.0.1:514
   ```

   Depois de ajustar o `rsyslog`, utilize o utilitario `logger` ou suas
   aplicacoes para gerar eventos.

2. Inicie o coletor que ira ler continuamente o arquivo de log e popular o banco:

```bash
python -m log_analyzer.collector
```

3. Para visualizar no terminal:

```bash
python -m log_analyzer.tui_panel
```

4. Para acessar pelo navegador:

```bash
python -m log_analyzer.web_panel
```

A aplicacao web ficará disponivel em `http://localhost:5000`.

## Estrutura de diretorios

- `log_analyzer/` - codigo fonte principal
- `rsyslog.log` - arquivo lido pelo coletor (pode ser alterado no codigo)
- `logs.db` - banco SQLite criado automaticamente

## Alertas

Linhas que contenham termos como `denied`, `attack` ou `malware` sao
classificadas como **MALICIOUS** e geram uma mensagem de alerta no terminal.
