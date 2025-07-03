# Configurando Pipelines no Graylog

Este documento descreve os passos para criar e aplicar um **Pipeline** no Graylog. Presume-se que o Graylog esteja em execucao e que ja exista um input configurado, conforme indicado em [docs/graylog_inputs.md](graylog_inputs.md).

## 1. Acessar a interface do Graylog

1. Abra `http://<SEU-SERVIDOR>:9000` no navegador e autentique-se com uma conta de administrador.
2. Verifique se as mensagens estao chegando em **Search** antes de prosseguir.

## 2. Criar regras de Pipeline

1. No menu superior, clique em **System** ➜ **Pipelines**.
2. Selecione **Manage rules** e clique em **Create rule**.
3. Defina um nome (ex.: `parse_logs`) e escreva a condicao (`when`) e a acao (`then`). Um exemplo basico:

```pseudocode
rule "parse_logs"
when
  has_field("message") && regex("service=\\w+", to_string($message.message)).matches
then
  let svc = regex("service=(\\w+)", to_string($message.message));
  set_field("source_service", svc.group[1]);
end
```

Essa regra cria o campo `source_service` ao extrair o valor de `service` da mensagem.

Para eventos de rede enviados pelo `net_sniffer.py` ou ferramentas semelhantes,
pode ser útil extrair endereços IP, portas e protocolo da linha capturada.
Uma regra mais completa ficaria assim:

```pseudocode
rule "parse_network_event"
when
  has_field("message")
then
  let msg = to_string($message.message);
  let svc = regex("service=(\\w+)", msg);
  let ip  = regex("(\d+\.\d+\.\d+\.\d+)\.(\d+) > (\d+\.\d+\.\d+\.\d+)\.(\d+)", msg);
  let proto = regex("proto=(\w+)", msg);
  set_fields(fields: {
    source_service: svc.matches ? svc.group[1] : null,
    src_ip: ip.matches ? ip.group[1] : null,
    src_port: ip.matches ? ip.group[2] : null,
    dst_ip: ip.matches ? ip.group[3] : null,
    dst_port: ip.matches ? ip.group[4] : null,
    protocol: proto.matches ? proto.group[1] : null
  });
end
```

Com ela o Graylog adiciona campos estruturados para os pacotes de rede,
facilitando buscas e o cruzamento com as demais informações de log. As
regras utilizadas neste guia estão disponíveis em
`Graylog/pipeline_rules.conf` e podem ser importadas diretamente na
interface do Graylog.

## 3. Criar o Pipeline

1. Ainda em **Pipelines**, clique em **Create pipeline**.
2. Informe um nome e uma descricao breves.
3. Adicione estagios (stages) e associe a cada um as regras criadas no passo anterior.
4. Salve o pipeline.

## 4. Conectar o Pipeline a um Stream

1. Acesse **Streams** e escolha um stream existente ou crie um novo para as mensagens que deverao passar pelo pipeline.
2. No menu do stream, clique em **Connections**.
3. Selecione o pipeline recem-criado e confirme a conexao.

## 5. Testar e ajustar

1. Envie algumas mensagens para o Graylog e verifique em **Search** se o campo `source_service` ou outras transformacoes aparecem corretamente.
2. Ajuste as regras conforme necessario para garantir que todos os casos sejam tratados.

Seguindo esses passos o Graylog aplicara as transformacoes definidas no pipeline a cada mensagem recebida, facilitando a organizacao e a analise dos logs.
