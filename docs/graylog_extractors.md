# Criando extratores no Graylog

Este guia apresenta um passo a passo para criar **extratores** no Graylog com base nas mensagens geradas por este projeto. Para informações mais detalhadas consulte a [documentação oficial](https://go2docs.graylog.org/current/making_sense_of_your_log_data/extractors.html).

## 1. Acessar os extratores

1. Abra `http://localhost:9000` e autentique-se com o usuário administrador.
2. No menu **System** ➔ **Inputs**, localize o input **GELF HTTP** criado previamente.
3. Clique em **Manage extractors** para visualizar e adicionar novos extratores.

## 2. Extrator para falhas de autenticação (Regex)

As mensagens do `sshd` podem indicar tentativas de login malsucedidas, como no exemplo abaixo:

```
Failed password for invalid user admin from 1.2.3.4 port 22 ssh2
```

Para extrair o nome do usuário, o IP de origem e a porta:

1. Em **Manage extractors**, clique em **Add extractor** e selecione o tipo **Regular expression**.
2. Informe um título como `ssh_login_fail` e escolha o campo **message** como fonte.
3. Utilize o padrão:
   ```
   Failed password for (?:invalid user )?(?<username>\w+) from (?<src_ip>\d+\.\d+\.\d+\.\d+) port (?<port>\d+)
   ```
4. Marque **Store as field** e salve os campos `username`, `src_ip` e `port`.
5. Clique em **Try** para testar o extrator e, se os valores estiverem corretos, confirme em **Save**.

## 3. Extrator para eventos de rede (Grok)

O módulo `net_sniffer.py` registra linhas no estilo do `tcpdump`, por exemplo:

```
IP 192.168.1.10.5678 > 10.0.0.5.80: Flags [S], seq 12345, length 0
```

Para separar endereços e portas:

1. No mesmo menu de extratores, clique em **Add extractor** e escolha **Grok pattern**.
2. Defina o campo **message** como fonte e adote o seguinte padrão:
   ```
   IP %{IP:src_ip}.%{INT:src_port} > %{IP:dst_ip}.%{INT:dst_port}: %{GREEDYDATA:packet_info}
   ```
3. Salve o extrator para que `src_ip`, `src_port`, `dst_ip`, `dst_port` e `packet_info` apareçam em cada mensagem.

## 4. Verificando os resultados

Retorne à tela **Search** e envie alguns logs para o Graylog. Os campos extraídos ficarão disponíveis para filtros, widgets de dashboard e regras de pipeline. Caso deseje realizar ajustes ou adicionar novos padrões, repita os passos acima em **Manage extractors**.

## 5. Importação via JSON

Se preferir importar extratores já prontos, utilize o menu **Actions > Import Extractors** dentro de **Manage extractors** e cole o conteúdo do arquivo `Graylog/extractors.json` deste repositório. Os campos serão criados automaticamente.
