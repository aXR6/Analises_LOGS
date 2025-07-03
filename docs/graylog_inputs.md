# Configurando Inputs no Graylog

Este guia ensina a criar um input no Graylog para receber os logs classificados
pela IA do projeto. O exemplo utiliza o tipo **GELF HTTP**, que é simples de
enviar via `requests` ou `curl`.

1. Acesse `http://localhost:9000` com o usuário definido em
   `GRAYLOG_ROOT_USERNAME`.
2. No menu superior, clique em **System** ➜ **Inputs**.
3. Selecione **GELF HTTP** na lista e clique em **Launch new input**.
4. Marque **Global** para que o input fique ativo em todos os nós e defina um
   título, por exemplo `Logs IA`.
5. Mantenha a porta padrão `12201` e clique em **Save** para inicializar o
   input.

Com o input em execução, os logs podem ser enviados para
`http://localhost:12201/gelf` no formato JSON seguindo a especificação GELF.
Cada registro pode incluir campos adicionais, como `severity` ou
`anomaly_score`, produzidos pela análise da IA.
