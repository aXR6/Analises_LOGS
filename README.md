# Análise de Logs com rsyslog

Este projeto coleta logs gerados pelo `rsyslog`, armazena em um banco PostgreSQL e disponibiliza dois painéis de monitoramento. As mensagens também são indexadas no **Elasticsearch** para consultas rápidas. A severidade e a pontuação de anomalia dos eventos são classificadas por modelos configuráveis, permitindo identificar comportamentos suspeitos de maneira automática.

## Sumário
- [Funcionalidades](#funcionalidades)
- [Requisitos](#requisitos)
- [Instalação](#instala%c3%a7%c3%a3o)
- [Uso](#uso)
- [Personalizando modelos](#personalizando-modelos)
- [Estrutura de diretórios](#estrutura-de-diret%c3%b3rios)
- [Alertas](#alertas)
- [Detecção de Anomalias Semânticas](#detec%c3%a7%c3%a3o-de-anomalias-sem%c3%a2nticas)
- [Análise com modelos LLM](#an%c3%a1lise-com-modelos-llm)
- [Monitoramento de Tráfego de Rede](#monitoramento-de-tr%c3%a1fego-de-rede)
- [Integração com Graylog](#integra%c3%a7%c3%a3o-com-graylog)

## Funcionalidades
- Coleta de logs via `rsyslog` e armazenamento em PostgreSQL.
- Indexação das mensagens no Elasticsearch.
- Painel de terminal utilizando a biblioteca `rich`.
- Painel web simples com Flask.
- Sistema de alertas para termos suspeitos (*denied*, *attack*, *malware*).
- Classificação de severidade e detecção de anomalias através de modelos definidos no `.env`.
- Análise opcional de entradas com modelos de linguagem (LLM) da Hugging Face.
- Monitoramento de tráfego de rede baseado em modelo NIDS.

## Requisitos
- Python 3.8 ou superior.
- Dependências listadas em `requirements.txt` (inclui `bitsandbytes` para modelos quantizados).
- Uma instância do **Elasticsearch** acessível no endereço configurado em `ES_URL`.
- Banco PostgreSQL disponível para receber as tabelas definidas em `schema.sql`.

## Instalação
1. Clone o repositório e acesse a pasta do projeto:
   ```bash
   git clone <repo> && cd Analises_LOGS
   ```
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Copie `.env.example` para `.env` e preencha as credenciais do banco e o endereço do Elasticsearch.
4. Crie o banco de dados e aplique o script `schema.sql`.
5. Ajuste o `rsyslog` conforme [docs/rsyslog_optimization.md](docs/rsyslog_optimization.md) para registrar os eventos em `rsyslog.log` (ou caminho definido em `LOG_FILE`).

## Uso
1. Inicie o coletor que lê continuamente o arquivo de log e popula o banco:
   ```bash
   python -m log_analyzer.collector
   ```
2. Para visualizar os registros no terminal:
   ```bash
   python -m log_analyzer.tui_panel
   ```
   Alertas críticos são destacados em vermelho e as atualizações ocorrem em tempo real.
3. Para acessar pelo navegador:
   ```bash
   python -m log_analyzer.web_panel
   ```
   A aplicação ficará disponível em `http://localhost:5000` com paginação de 100 registros, filtros por severidade e busca textual utilizando o Elasticsearch. O nome do programa é exibido e pode ser usado como filtro ao clicar. Quando novos registros chegam, um balão "+1" indica atividade recente. A barra superior mostra os totais por severidade e, na aba "Tráfego de rede", exibe também a contagem de eventos classificados pelo NIDS.
4. Opcionalmente execute `python menu.py` para controlar todas as funções a partir de um menu interativo (incluindo troca entre **CPU** e **GPU** e seleção da interface de rede).

## Personalizando modelos
Os nomes dos modelos podem ser alterados através das variáveis no `.env`. Utilize `SEVERITY_MODEL` e `ANOMALY_MODEL` para definir classificadores e `ANOMALY_THRESHOLD` para ajustar o ponto de corte. Outros modelos, como `SEMANTIC_MODEL`, `HUGGINGFACE_MODEL` e `NIDS_MODEL`, seguem a mesma lógica e permitem trocar facilmente a inteligência utilizada.

## Estrutura de diretórios
- `log_analyzer/` – código fonte principal.
- `rsyslog.log` – arquivo monitorado pelo coletor (configurável via `.env`).
- `schema.sql` – definição das tabelas PostgreSQL.
- `.env.example` – modelo de configuração do ambiente.
- `logs` – índice Elasticsearch contendo os eventos processados.

## Alertas
Linhas contendo termos suspeitos são marcadas como **MALICIOUS** e geram alerta imediato no terminal. O tipo de ataque identificado fica visível no painel web, juntamente com as ocorrências mais recentes. Mensagens cujo `anomaly_score` ultrapassa o valor de `ANOMALY_THRESHOLD` também são consideradas suspeitas.

## Detecção de Anomalias Semânticas
Para encontrar padrões incomuns no texto dos logs utilize:
```bash
python -m log_analyzer.semantic_anomaly caminho/para/arquivo.log
```
Entradas rotuladas com o cluster `-1` serão tratadas como anomalias.

## Análise com modelos LLM
É possível enviar um registro específico para análise por um modelo da Hugging Face. Defina `HUGGINGFACE_MODEL`, `DEVICE_TYPE` e `LLM_PROMPT` no `.env` e execute:
```bash
python -m log_analyzer.llm_analysis ID_DO_LOG
```
O resultado é gravado nas tabelas `log_analysis` e `analyzed_logs` e pode ser consultado pelo painel web.

## Monitoramento de Tráfego de Rede
Um monitor adicional utiliza o modelo definido em `NIDS_MODEL` para classificar eventos de rede (DoS, Port Scan, Brute Force, etc.). As entradas ficam registradas na tabela `network_events` e podem ser acompanhadas na aba "Tráfego de rede" do painel web. A integração básica pode ser feita com a biblioteca `transformers`:
```python
from transformers import pipeline
import os

classifier = pipeline("text-classification", model=os.getenv("NIDS_MODEL"))
log = {
    # características do fluxo IoT ou rede transformadas em JSON ou vetores
}
result = classifier(log)
print(result)  # ex: {'label': 'Scanning', 'score': 0.87}
```
O dispositivo de rede utilizado na captura é configurado em `NET_INTERFACE` e é possível enviar eventos para análise utilizando o mesmo modelo de logs, armazenando o resultado em `network_analysis` e `analyzed_network_events`.

## Integração com Graylog
O projeto disponibiliza um `docker-compose.yml` na raiz com todos os serviços necessários para executar o Graylog Community (MongoDB e Elasticsearch). Ele reutiliza o PostgreSQL já configurado através das variáveis presentes no `.env`. Defina em `GRAYLOG_ROOT_USERNAME` e `GRAYLOG_ROOT_PASSWORD_SHA2` as credenciais do administrador. Para iniciar execute:

```bash
docker compose up -d
```

A interface ficará disponível em `http://localhost:9000` e os parâmetros adicionais estão definidos em `Graylog/graylog.conf`.

Caso o contêiner reinicie com erro de permissão ao persistir o **Node ID** do
Graylog, defina `GRAYLOG_NODE_ID_FILE` para um local gravável. Um exemplo é
`/usr/share/graylog/data/config/node-id`, que já possui permissões adequadas:

```yaml
graylog:
  environment:
    - GRAYLOG_NODE_ID_FILE=/usr/share/graylog/data/config/node-id
```

Com esse ajuste o arquivo é criado corretamente e o serviço passa a iniciar
normalmente.
