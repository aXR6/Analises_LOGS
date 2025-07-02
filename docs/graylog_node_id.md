# Resolucao para erro de Node ID no Graylog

Se o container do Graylog reiniciar repetidamente com mensagens semelhantes a
`AccessDeniedException: /etc/graylog/server`, significa que o processo nao
consegue escrever o arquivo `node-id`. Defina a variavel `GRAYLOG_NODE_ID_FILE`
para um diretorio gravavel. Um caminho recomendado eh
`/usr/share/graylog/data/config/node-id`.

Exemplo de configuracao no `docker-compose.yml`:

```yaml
services:
  graylog:
    environment:
      - GRAYLOG_NODE_ID_FILE=/usr/share/graylog/data/config/node-id
```

Esse diretorio ja existe dentro da imagem e possui permissoes suficientes para
criar o arquivo, evitando que o servico encerre por `NodeIdPersistenceException`.
