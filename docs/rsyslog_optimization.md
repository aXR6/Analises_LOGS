# Otimizacao do rsyslog no Debian 12

Este documento descreve um exemplo de configuracao do **rsyslog** focada em desempenho para integracao com este projeto.

1. Ative os modulos basicos e o suporte ao *systemd journal*:

```conf
module(load="imuxsock")
module(load="imklog")
module(load="imjournal")
```

2. Configure um `workDirectory` para filas em disco e defina uma fila principal com threads dedicadas:

```conf
global(workDirectory="/var/spool/rsyslog")
main_queue(
    queue.type="LinkedList"
    queue.size="10000"
    queue.workerThreads="2"
    queue.dequeueBatchSize="500"
    queue.highWatermark="8000"
    queue.lowWatermark="2000"
    queue.spoolDirectory="/var/spool/rsyslog"
)
```

3. Utilize escrita assincrona para reduzir bloqueios de I/O ao enviar eventos para o arquivo lido pelo coletor:

```conf
action(
    type="omfile"
    file="/caminho/para/projeto/rsyslog.log"
    template="LogAnalyzerFormat"
    asyncWriting="on"
)
```

4. Defina um `template` em formato RFC 3339 para que o parser consiga extrair os campos de forma eficiente:

```conf
template(name="LogAnalyzerFormat" type="string" string="%timestamp:::date-rfc3339% %HOSTNAME% %syslogtag%%msg%\n")
```

Salve o trecho acima em `/etc/rsyslog.d/50-log_analyzer.conf`, reinicie o `rsyslog` com `sudo systemctl restart rsyslog` e execute o coletor normalmente.
