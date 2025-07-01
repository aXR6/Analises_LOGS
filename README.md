# Analise de Logs com rsyslog

Este projeto coleta logs gerados pelo `rsyslog`, armazena em um banco de dados
SQLite e fornece dois paineis de monitoramento:

- **Painel de terminal** utilizando a biblioteca `rich`.
- **Painel web** simples utilizando Flask.

Logs considerados maliciosos geram alertas imediatos exibidos no terminal.

## Requisitos

- Python 3.8+
- Dependências listadas em `requirements.txt`

## Instalacao

```bash
pip install -r requirements.txt
```

## Uso

1. Configure o `rsyslog` para gravar seus eventos em `rsyslog.log` na raiz do
   projeto. Um exemplo simples de configuracao em `/etc/rsyslog.d/50-default.conf`:
   
   ```
   *.* @@127.0.0.1:514
   ```
   
   Em seguida, direcione para arquivo local usando o utilitario `logger` ou uma
   configuracao personalizada conforme a necessidade.

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
