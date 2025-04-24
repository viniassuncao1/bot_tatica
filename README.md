# Bot de Ações Discord

Este é um bot para Discord que gerencia ações com sistema de vagas para operadores.

## Configuração

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

2. Configure o arquivo `.env`:
- Substitua `seu_token_aqui` pelo token do seu bot do Discord

3. Configure os canais no arquivo `bot.py`:
- Substitua `channel_ids = [123456789]` pelos IDs dos canais onde você quer que o bot funcione
- Substitua `LOG_CHANNEL_ID = 123456789` pelo ID do canal onde você quer que os logs sejam enviados

4. Execute o bot:
```bash
python bot.py
```

## Funcionamento

1. O bot automaticamente criará um botão "Assumir posição" nos canais configurados
2. Ao clicar no botão, será aberto o painel de ações com todas as opções disponíveis:
   - Fleeca 🏦
   - Joalheria 💎
   - Loja de Conveniência 🏪
   - Ammu-Nation 🔫
   - Fábrica 🏭
   - Banco Paleto 🏛️
   - Yellow Jack 🍺
   - Maze Bank 💰
3. Ao selecionar uma ação, o bot criará uma embed com:
   - Nome da ação
   - Nome do comando (quem criou)
   - Sistema de vagas para operadores (máximo 4)
4. Os usuários podem clicar no botão "Entrar como Operador" para participar

## Sistema de Logs

O bot registra automaticamente no canal de logs:
- 🔵 Inicialização do sistema
- 🟡 Criação de novas ações (quem criou e qual ação)
- 🟢 Entrada de operadores (quem entrou e em qual ação)

## Funcionalidades

- Botão permanente para criar ações
- Lista de ações com ícones
- Sistema de entrada como operador
- Limite de 4 operadores por ação
- Contagem de vagas preenchidas
- Verificação de participantes duplicados
- Interface intuitiva com botões
- Sistema completo de logs
- Limpeza automática de mensagens antigas do bot 