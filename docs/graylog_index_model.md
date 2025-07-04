# Definindo um Index Set para o projeto

Este documento descreve um modelo de **index set** adequado aos campos
que o projeto envia ao Graylog. Para maiores detalhes sobre o modelo de
index do Graylog consulte a [documentação oficial](https://go2docs.graylog.org/current/setting_up_graylog/index_model.html).

## Campos esperados

Os eventos encaminhados ao Graylog pelo coletor e pelo NIDS contêm os
seguintes campos adicionais no formato GELF:

- `_program` – nome do processo que gerou o log
- `_category` – categoria atribuída pelo classificador
- `_severity` – nível de severidade
- `_anomaly_score` – pontuação de anomalia (float)
- `_malicious` – marca se o log contém termos suspeitos (boolean)
- `_semantic_outlier` – indica anomalia semântica (boolean)
- `_label` – rótulo gerado pelo modelo NIDS (eventos de rede)
- `_score` – confiança do NIDS (float)
- `_source` – origem do evento de rede
- `source_service` – campo definido via pipeline para identificar o serviço
- `src_ip`, `src_port`, `dst_ip`, `dst_port`, `protocol` – campos de rede

Esses nomes podem ser utilizados na criação do mapping do índice.

## Exemplo de configuração

1. Acesse **System > Indices** no Graylog e clique em **Create index set**.
2. Preencha os campos conforme o exemplo:
   - **Title**: `Logs IA`
   - **Description**: `Mensagens analisadas e eventos de rede do projeto de análise de logs`
   - **Index prefix**: `ia_logs`
   - **Shards**: `1`
   - **Replicas**: `0`
   - **Field type refresh interval**: `1s`
3. Em **Rotation & Retention** mantenha a opção **Data Tiering** com a
   estratégia _Index Time Size Optimizing_, que é o padrão recomendado.
   Defina a **Maximum number of indices** para `20` ou ajuste conforme a
   capacidade de retenção desejada.
4. Na seção **Retention** escolha a opção `Delete` para remover índices
   antigos automaticamente quando o limite for atingido.
5. Salve o index set e associe-o ao input GELF criado anteriormente.

Com essas configurações o Graylog criará índices com prefixo `ia_logs_` e
manterá os campos personalizados enviados pelo projeto. A rotação
automática garante que apenas os últimos 20 índices serão mantidos,
liberando espaço em disco de maneira constante.
