# Análise Inteligente de Logs

Este repositório contém uma solução completa para ingestão, classificação e monitoramento de logs gerados pelo `rsyslog`. O objetivo é identificar eventos suspeitos de maneira automática, armazená-los em um banco PostgreSQL e disponibilizar diferentes painéis de visualização. As mensagens também são indexadas no **Elasticsearch** para buscas rápidas e podem ser encaminhadas ao Graylog para correlação externa.

## Sumário
- [Visão Geral](#visão-geral)
- [Funcionalidades](#funcionalidades)
- [Arquitetura e Funcionamento](#arquitetura-e-funcionamento)
- [Configuração](#configuração)
- [Requisitos](#requisitos)
- [Instalação](#instalação)
- [Uso](#uso)
- [Personalizando Modelos](#personalizando-modelos)
- [Estrutura de Diretórios](#estrutura-de-diretórios)
- [Alertas](#alertas)
- [Detecção de Anomalias Semânticas](#detecção-de-anomalias-semânticas)
- [Análise com Modelos LLM](#análise-com-modelos-llm)
- [Monitoramento de Tráfego de Rede](#monitoramento-de-tráfego-de-rede)
- [Integração com Graylog](#integração-com-graylog)

## Visão Geral
O projeto lê continuamente o arquivo de log definido em `LOG_FILE`, aplica um parser simples e registra cada linha em tabelas PostgreSQL. Em seguida, as entradas são classificadas conforme severidade e grau de anomalia por modelos de IA configuráveis. Todos os registros ficam disponíveis em dois painéis de monitoramento: um de terminal, utilizando a biblioteca `rich`, e outro via web com Flask. Há ainda suporte para enviar os eventos para o Graylog e para o Elasticsearch, permitindo consultas e correlação em tempo real.

## Funcionalidades
- Coleta de logs do `rsyslog` e gravação em banco de dados.
- Classificação de severidade e detecção de anomalias utilizando modelos indicados no `.env`.
- Indexação opcional das mensagens no Elasticsearch.
- Painel de terminal com destaques coloridos e atualização em tempo real.
- Painel web simples com filtros, busca textual e contadores de severidade.
- Geração de alertas para termos suspeitos (*denied*, *attack*, *malware*).
- Monitoramento de tráfego de rede classificado por modelo NIDS.
- Possibilidade de análise individual de registros via modelos de linguagem (LLM).

## Arquitetura e Funcionamento
1. **Coletor (`collector.py`)**: observa o arquivo de log do rsyslog e envia cada linha para o parser.
2. **Parser (`log_parser.py`)**: extrai campos importantes (timestamp, hostname, programa, mensagem) e normaliza os dados.
3. **Banco de dados (`log_db.py`)**: armazena logs, anomalias e análises complementares em tabelas PostgreSQL criadas a partir de `schema.sql`.
4. **Classificadores**: modelos configurados via `.env` avaliam a severidade e o grau de anomalia de cada entrada.
5. **Indexação (`es_client.py`)**: os registros também são enviados ao Elasticsearch para busca e agregações.
6. **Painéis**: `tui_panel.py` exibe um painel em terminal e `web_panel.py` oferece uma interface web simples.
7. **Integrações**: se `GRAYLOG_URL` estiver definido, cada evento é encaminhado ao Graylog no formato GELF. O projeto também inclui scripts para análise semântica, uso de LLMs e monitoramento de rede (`net_sniffer.py`).

## Configuração
Crie um arquivo `.env` baseado em `.env.example` e defina as variáveis principais:

- **Credenciais do PostgreSQL:** `PG_HOST`, `PG_PORT`, `PG_DB`, `PG_USER` e `PG_PASS`.
- **Elasticsearch:** `ES_URL` com o endereço do cluster.
- **Graylog (opcional):** `GRAYLOG_URL` para envio de eventos e variáveis de admin (`GRAYLOG_ROOT_USERNAME`, `GRAYLOG_ROOT_PASSWORD_SHA2`).
- **Modelos de IA:** `SEVERITY_MODEL`, `ANOMALY_MODEL`, `SEMANTIC_MODEL`, `NIDS_MODEL` e `HUGGINGFACE_MODEL`.
- **Arquivos monitorados:** `LOG_FILE` e `NET_LOG_FILE` (para o NIDS), além de `NET_INTERFACE` se utilizar captura direta de rede.
- **Outros ajustes:** `ANOMALY_THRESHOLD`, `DEVICE_TYPE` para seleção de CPU ou GPU e `LLM_PROMPT` para análises via linguagem natural.

Todas as variáveis podem ser exportadas no ambiente ou definidas diretamente no `.env` antes de iniciar os módulos.

## Requisitos
- Python 3.8 ou superior.
- Dependências listadas em `requirements.txt` (inclui `bitsandbytes` para modelos quantizados).
- Instância do **Elasticsearch** acessível pelo endereço configurado em `ES_URL`.
- Banco PostgreSQL disponível para receber as tabelas de `schema.sql`.

## Instalação
1. Clone o repositório e acesse a pasta do projeto:
   ```bash
   git clone <repo> && cd Analises_LOGS
   ```
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Copie `.env.example` para `.env` e ajuste as credenciais e os nomes dos modelos conforme desejado.
4. Crie o banco de dados e aplique o script `schema.sql`.
5. Configure o `rsyslog` seguindo as dicas em [docs/rsyslog_optimization.md](docs/rsyslog_optimization.md) para direcionar as mensagens ao arquivo definido em `LOG_FILE`.

## Uso
1. Inicie o coletor para popular o banco de dados:
   ```bash
   python -m log_analyzer.collector
   ```
2. Abra o painel em terminal:
   ```bash
   python -m log_analyzer.tui_panel
   ```
3. Acesse a interface web:
   ```bash
   python -m log_analyzer.web_panel
   ```
   Ela ficará disponível em `http://localhost:5000` com filtros de severidade, busca textual e contadores gerais. Novos registros aparecem em tempo real com um indicativo de atividade. Na aba "Tráfego de rede" são exibidos os eventos classificados pelo NIDS.
4. O contêiner inicia automaticamente o coletor, o sniffer e o NIDS utilizando a rede do host. Caso prefira um controle manual, execute `python menu.py` para iniciar e parar os serviços, alternar entre **CPU** e **GPU** ou selecionar a interface de rede.

## Personalizando Modelos
Os nomes dos modelos de IA podem ser alterados facilmente pelas variáveis do `.env`. Utilize `SEVERITY_MODEL` e `ANOMALY_MODEL` para classificadores de logs, `SEMANTIC_MODEL` para detecção semântica, `NIDS_MODEL` para tráfego de rede e `HUGGINGFACE_MODEL` para análises pontuais via LLM. Ajuste `ANOMALY_THRESHOLD` para calibrar a pontuação considerada suspeita.

## Estrutura de Diretórios
- `log_analyzer/` – código-fonte principal com todos os módulos.
- `rsyslog.log` – arquivo monitorado pelo coletor (caminho definido em `LOG_FILE`).
- `schema.sql` – definição das tabelas PostgreSQL.
- `.env.example` – modelo de configuração do ambiente.
- `Graylog/` – arquivos utilizados pelo `docker-compose.yml` para iniciar o Graylog.
- `docs/` – documentação complementar com dicas de configuração.
- `logs` – índice Elasticsearch contendo os eventos processados.

## Alertas
Linhas que contenham termos suspeitos são marcadas como **MALICIOUS** e geram alerta imediato nos painéis. Eventos cujo `anomaly_score` ultrapassa `ANOMALY_THRESHOLD` também são destacados e podem ser encaminhados ao Graylog.

## Detecção de Anomalias Semânticas
Para localizar padrões incomuns no texto dos logs execute:
```bash
python -m log_analyzer.semantic_anomaly caminho/para/arquivo.log
```
Entradas rotuladas com o cluster `-1` serão tratadas como anomalias e podem ser revisadas separadamente.

## Análise com Modelos LLM
Registros específicos podem ser analisados por um modelo de linguagem da Hugging Face. Configure `HUGGINGFACE_MODEL`, `DEVICE_TYPE` e `LLM_PROMPT` e rode:
```bash
python -m log_analyzer.llm_analysis ID_DO_LOG
```
O resultado fica disponível nas tabelas `log_analysis` e `analyzed_logs` e também pode ser consultado pelo painel web.

## Monitoramento de Tráfego de Rede
O módulo `net_sniffer.py` pode capturar eventos de rede e utilizar o modelo `NIDS_MODEL` para classificá-los (DoS, Port Scan, Brute Force, etc.). As entradas são salvas em `network_events` e visualizadas na aba "Tráfego de rede" do painel web. A integração básica pode seguir o exemplo abaixo:
```python
from transformers import pipeline
import os

classifier = pipeline("text-classification", model=os.getenv("NIDS_MODEL"))
log = {
    # características do fluxo de rede ou IoT transformadas em JSON
}
print(classifier(log))
```
Se `GRAYLOG_URL` estiver configurado, cada evento classificado também será enviado para o Graylog em formato GELF.

## Integração com Graylog
O repositório inclui um `docker-compose.yml` que sobe o Graylog Community juntamente com MongoDB e Elasticsearch reutilizando o mesmo PostgreSQL configurado no `.env`. Defina `GRAYLOG_ROOT_USERNAME` e `GRAYLOG_ROOT_PASSWORD_SHA2` para iniciar:
```bash
docker compose up -d
```
A interface ficará em `http://localhost:9000` e parâmetros adicionais são definidos em `Graylog/graylog.conf`. Caso o contêiner apresente erro ao gravar o **Node ID**, ajuste `GRAYLOG_NODE_ID_FILE` conforme descrito em [docs/graylog_node_id.md](docs/graylog_node_id.md).

Com o Graylog em execução, defina `GRAYLOG_URL` (padrão `http://localhost:12201/gelf`) para que o coletor e o NIDS enviem cada registro processado. Para criar um input GELF HTTP siga o guia em [docs/graylog_inputs.md](docs/graylog_inputs.md).
Para montar um painel de visualização, consulte [docs/graylog_dashboard.md](docs/graylog_dashboard.md).
Para transformar ou validar mensagens de forma avançada, veja o guia de pipelines em [docs/graylog_pipeline.md](docs/graylog_pipeline.md).
Para definir o index set utilizado pelos eventos, veja o modelo sugerido em [docs/graylog_index_model.md](docs/graylog_index_model.md).
