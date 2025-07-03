# Configurando o painel do Graylog

Este guia detalha como criar um painel no Graylog para acompanhar em tempo real todos os logs recebidos pelo projeto. Pressupõe-se que o Graylog já esteja em execução conforme indicado no [README](../README.md) e que um input GELF esteja configurado de acordo com [docs/graylog_inputs.md](graylog_inputs.md).

## 1. Acessar o Graylog

1. Abra `http://localhost:9000` e faça login com `GRAYLOG_ROOT_USERNAME` e `GRAYLOG_ROOT_PASSWORD` definidos no `docker-compose.yml`.
2. No canto esquerdo, clique em **Search** para verificar se as mensagens estão chegando.
3. Ajuste o período de tempo (ex.: `Last 5 minutes`) para visualizar os eventos recentes.

## 2. Criar um Dashboard

1. No topo da página **Search**, clique em **Create > Dashboard**.
2. Dê um nome como `Visão Geral dos Logs` e salve. O painel será criado vazio.

## 3. Adicionar Widgets

Dentro do dashboard recém-criado, clique em **Add Widget** e selecione os tipos de visualização desejados:

- **Message Table**: apresenta as mensagens em formato de tabela. Marque os campos mais importantes (por exemplo, `timestamp`, `source`, `level` e `message`).
- **Field Charts**: escolha `Histogram` para exibir a frequência de eventos ao longo do tempo ou `Pie Chart` para separar por níveis de severidade.
- **Quick Values**: mostra os valores mais comuns de um campo, útil para identificar hosts ou serviços que geram mais logs.

Cada widget pode ser redimensionado e posicionado livremente no painel. Use a opção **Edit** para configurar filtros específicos (por exemplo, apenas registros com `level:ERROR`).

## 4. Salvar e Compartilhar

1. Após organizar os widgets, clique em **Share** para tornar o painel público ou para gerar uma URL de acesso rápido.
2. Use **Actions > Set as Start Page** se desejar abrir esse dashboard automaticamente ao efetuar login.

## 5. Dicas Adicionais

- Utilize **Streams** para separar diferentes tipos de log (aplicação, sistema, segurança) e crie dashboards específicos para cada fluxo.
- Explore a opção **Alerts & Events** para configurar gatilhos que notifiquem quando determinados padrões surgirem nos logs.
- Caso deseje exportar métricas para outro sistema, acesse **System > Content Packs** e avalie as integrações disponíveis.

Com essas configurações, o painel do Graylog exibirá de forma clara e organizada todos os logs processados, permitindo acompanhar tendências e reagir rapidamente a incidentes.
