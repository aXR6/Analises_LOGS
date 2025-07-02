# Analise de Logs com rsyslog

Este projeto coleta logs gerados pelo `rsyslog`, armazena em um banco de dados
PostgreSQL e fornece dois paineis de monitoramento. A classificacao de severidade
dos logs utiliza o modelo **byviz/bylastic_classification_logs** disponivel no
Hugging Face. Esse modelo organiza os eventos em **ERROR**, **WARNING** e **INFO**,
conforme descrito na [documentacao do projeto](https://huggingface.co/byviz/bylastic_classification_logs).
Adicionalmente, e calculada uma pontuacao de anomalia com o modelo
**teoogherghi/Log-Analysis-Model-DistilBert**.

Painéis disponíveis:

- **Painel de terminal** utilizando a biblioteca `rich`.
 - **Painel web** simples utilizando Flask.

Logs contendo termos como `denied`, `attack` ou `malware` geram alertas imediatos
exibidos no terminal e sao marcados como maliciosos no banco de dados.

Para configuracoes de alto desempenho do `rsyslog` em ambientes Debian 12
consulte [docs/rsyslog_optimization.md](docs/rsyslog_optimization.md).

## Requisitos

- Python 3.8+
- Dependências listadas em `requirements.txt`

## Instalacao

```bash
pip install -r requirements.txt
```

Copie o arquivo `.env.example` para `.env` e preencha as credenciais do banco.
Todas as informações sensíveis devem ficar apenas nesse arquivo, já que o
codigo fonte não define mais valores padrão.

## Personalizando modelos

Os nomes dos modelos carregados podem ser alterados livremente por variáveis de
ambiente no arquivo `.env`. Os parâmetros `SEVERITY_MODEL` e `ANOMALY_MODEL`
definem, respectivamente, o classificador de severidade e o detector de
anomalias. Também é possível ajustar o `ANOMALY_THRESHOLD` para controlar em
que pontuação uma linha é marcada como suspeita.

## Uso

1. Configure o `rsyslog` para gravar seus eventos em `rsyslog.log` (ou no caminho
   definido na variavel `LOG_FILE` do `.env`) na raiz do
    projeto. Para uma configuracao mais eficiente, consulte o arquivo
    [docs/rsyslog_optimization.md](docs/rsyslog_optimization.md) e salve o
    conteudo sugerido em `/etc/rsyslog.d/50-log_analyzer.conf`. Certifique-se de
    definir o template antes da `action` para evitar erros de configuracao.

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
A aplicacao web ficará disponivel em `http://localhost:5000`. A listagem possui
paginacao de 100 registros e filtros por severidade. O nome do software
responsavel por cada evento tambem é exibido e pode ser utilizado como filtro ao
clicar sobre ele.
Como opcao, execute `python menu.py` para gerenciar todas as funcionalidades a partir de um menu interativo.
O menu tambem permite alternar entre execucao em **CPU** ou **GPU** para a
analise com modelos LLM.

## Estrutura de diretorios

- `log_analyzer/` - codigo fonte principal
- `rsyslog.log` - arquivo lido pelo coletor (configuravel via `.env`)
- `schema.sql` - definicao da tabela utilizada no PostgreSQL
- `.env.example` - arquivo de exemplo com variaveis de configuracao do banco

## Alertas

Linhas que contenham termos como `denied`, `attack` ou `malware` sao
classificadas como **MALICIOUS** e geram uma mensagem de alerta no terminal.
Adicionalmente, entradas cujo `anomaly_score` ultrapassa o valor definido em
`ANOMALY_THRESHOLD` tambem sao tratadas como suspeitas.

## Detecao de Anomalias Semanticas

Para detectar padroes incomuns no texto dos logs e possivel executar o modulo
`log_analyzer.semantic_anomaly`. O utilitario gera embeddings utilizando o
modelo `all-MiniLM-L6-v2` da biblioteca *sentence-transformers* e aplica o
algoritmo DBSCAN para identificar mensagens atipicas.

```bash
python -m log_analyzer.semantic_anomaly caminho/para/arquivo.log
```

Linhas rotuladas com o cluster `-1` sao tratadas como anomalias.

## Analise com modelos LLM

E possivel enviar uma entrada especifica do banco para analise por um modelo
da **Hugging Face**. Defina `HUGGINGFACE_MODEL` e `DEVICE_TYPE` no `.env` e
utilize o painel web para acionar a analise ou execute manualmente:

```bash
python -m log_analyzer.llm_analysis ID_DO_LOG
```
O resultado da analise e armazenado na tabela `log_analysis`, ligado ao
registro original. Alem disso, o log analisado juntamente com o resumo gerado
eh copiado para a tabela `analyzed_logs` para facilitar consultas futuras.

## Monitoramento de Tráfego de Rede

Um monitor adicional utiliza o modelo **caffeinatedcherrychic/mistral-based-NIDS**
para classificar eventos de rede como ataques DoS, Port Scan, Brute Force ou
PingScan. As entradas sao registradas na tabela `network_events` e podem ser
acompanhadas pela aba "Trafego de rede" do painel web.
