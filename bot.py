import discord
from discord import app_commands
from discord.ui import Button, View, Select
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# ID do canal de logs
LOG_CHANNEL_ID = 1362542074250920086

# ID do cargo que pode limpar as ações
CARGO_ADMIN_ID = 1227919320898736180  # Substitua pelo ID do cargo correto

# URL da logo da Unidade Tática
LOGO_URL = "https://cdn.discordapp.com/attachments/1195135499455697068/1303085173809741884/logo_tatica.png?ex=6802ae23&is=68015ca3&hm=d5b239755157a9e6b81482b9cbac289d1eb0d6755c690c904b58c5a25c1eb141&"

# Dicionário com as ações e suas vagas
ACOES_VAGAS = {
    "Fleeca": 10,
    "Joalheria": 8,
    "Loja de Conveniência": 5,
    "Ammu-Nation": 3,
    "Fábrica": 7,
    "Banco Paleto": 11,
    "Yellow Jack": 5,
    "Maze Bank": 9
}

class ResultadoSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Vitória", emoji="🏆", value="vitoria"),
            discord.SelectOption(label="Derrota", emoji="💀", value="derrota"),
            discord.SelectOption(label="Empate", emoji="🤝", value="empate")
        ]
        super().__init__(placeholder="Selecione o resultado...", options=options, custom_id="resultado_select")

class FinalizarView(View):
    def __init__(self, acao_nome: str, comando_id: int, participantes: list, negociador: int = None):
        super().__init__(timeout=None)
        self.acao_nome = acao_nome
        self.comando_id = comando_id
        self.participantes = participantes
        self.negociador = negociador
        self.add_item(ResultadoSelect())

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.data["custom_id"] == "resultado_select":
            if interaction.user.id != self.comando_id:
                await interaction.response.send_message("Apenas o comando pode finalizar a ação!", ephemeral=True)
                return False

            resultado = interaction.data["values"][0]
            emoji_resultado = {"vitoria": "🏆", "derrota": "💀", "empate": "🤝"}[resultado]
            
            # Criar embed do resultado
            embed = discord.Embed(
                title=f"{emoji_resultado} Ação Finalizada: {self.acao_nome}",
                color=discord.Color.gold()
            )
            embed.add_field(name="Resultado", value=f"{emoji_resultado} {resultado.title()}", inline=False)
            embed.add_field(name="Comando", value=f"<@{self.comando_id}>", inline=False)
            
            # Lista detalhada de participantes
            participantes_texto = []
            for p in self.participantes:
                if p == self.comando_id:
                    participantes_texto.append(f"<@{p}> (👑 Comando)")
                elif p == self.negociador:
                    participantes_texto.append(f"<@{p}> (👨‍💼 Negociador)")
                else:
                    participantes_texto.append(f"<@{p}>")
            
            embed.add_field(name="Participantes", value="\n".join(participantes_texto), inline=False)
            
            await interaction.message.edit(embed=embed, view=None)
            await interaction.response.send_message(f"Ação finalizada com {resultado}!", ephemeral=True)

            # Log detalhado de finalização
            log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
            if log_channel:
                log_embed = discord.Embed(
                    title="📝 Log de Ação",
                    color=discord.Color.gold(),
                    timestamp=datetime.now()
                )
                log_embed.add_field(name="Ação Finalizada", value=self.acao_nome, inline=False)
                log_embed.add_field(name="Resultado", value=f"{emoji_resultado} {resultado.title()}", inline=False)
                log_embed.add_field(name="Comando", value=f"<@{self.comando_id}>", inline=False)
                log_embed.add_field(name="Total de Participantes", value=str(len(self.participantes)), inline=False)
                log_embed.add_field(name="Lista de Participantes", value="\n".join(participantes_texto), inline=False)
                await log_channel.send(embed=log_embed)

        return True

class CriarAcaoButton(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Button(
            label="Criar Ação",
            style=discord.ButtonStyle.success,
            custom_id="criar_acao"
        ))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.data["custom_id"] == "criar_acao":
            embed = discord.Embed(
                title="🎯 Painel de Ações",
                description="Selecione a ação que deseja criar",
                color=discord.Color.dark_grey()
            )
            
            # Criar lista de ações disponíveis como botões
            view = View(timeout=None)
            acoes = [
                ("Fleeca", "🏦"),
                ("Joalheria", "💎"),
                ("Loja de Conveniência", "🏪"),
                ("Ammu-Nation", "🔫"),
                ("Fábrica", "🏭"),
                ("Banco Paleto", "🏛️"),
                ("Yellow Jack", "🍺"),
                ("Maze Bank", "💰")
            ]
            
            for acao, emoji in acoes:
                button = Button(
                    label=f"{emoji} {acao} ({ACOES_VAGAS[acao]})",
                    style=discord.ButtonStyle.secondary,
                    custom_id=f"acao_{acao}"
                )
                button.callback = self.acao_callback
                view.add_item(button)
            
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        return True

    async def acao_callback(self, interaction: discord.Interaction):
        acao = interaction.data["custom_id"].replace("acao_", "")
        vagas_totais = ACOES_VAGAS[acao]
        
        embed = discord.Embed(
            title=f"💎 Ação em Andamento: {acao}",
            description="🚨 Atenção! A ação está sendo preparada.",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=LOGO_URL)
        embed.add_field(name="👮‍♂️ Comando", value=interaction.user.mention, inline=False)
        
        # Lista detalhada de participantes
        participantes_texto = [f"<@{interaction.user.id}> (👑 Comando)"]
        
        embed.add_field(
            name="👥 Vagas para operadores",
            value=f"🔢 1 / {vagas_totais} operadores\n\n**Participantes:**\n" + "\n".join(participantes_texto),
            inline=False
        )
        
        view = OperadoresView(acao, vagas_totais, [interaction.user.id])  # Comando já entra como operador
        await interaction.response.send_message(embed=embed, view=view)

        # Enviar log de criação da ação
        log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            log_embed = discord.Embed(
                title="📝 Log de Ação",
                color=discord.Color.yellow(),
                timestamp=datetime.now()
            )
            log_embed.add_field(name="Ação Criada", value=acao, inline=False)
            log_embed.add_field(name="Criada por", value=interaction.user.mention, inline=False)
            await log_channel.send(embed=log_embed)

class OperadoresView(View):
    def __init__(self, acao_nome: str, vagas_totais: int, participantes: list):
        super().__init__(timeout=None)
        self.participantes = participantes
        self.acao_nome = acao_nome
        self.vagas_totais = vagas_totais
        self.negociador = None
        
        # Botões para todos os usuários
        self.add_item(Button(
            label="Entrar como Operador",
            style=discord.ButtonStyle.success,
            custom_id="entrar_operador"
        ))
        
        self.add_item(Button(
            label="Entrar como Negociador",
            style=discord.ButtonStyle.success,
            custom_id="entrar_negociador"
        ))
        
        self.add_item(Button(
            label="Sair da Operação",
            style=discord.ButtonStyle.danger,
            custom_id="sair_operador"
        ))

        # Botões apenas para o comando
        iniciar_btn = Button(
            label="Iniciar Ação",
            style=discord.ButtonStyle.primary,
            custom_id="iniciar_acao"
        )
        iniciar_btn.callback = self.iniciar_callback  # Adicionar callback para iniciar ação
        self.add_item(iniciar_btn)

        excluir_btn = Button(
            label="Excluir Ação",
            style=discord.ButtonStyle.danger,
            custom_id="excluir_acao"
        )
        excluir_btn.callback = self.excluir_callback  # Adicionar callback para excluir ação
        self.add_item(excluir_btn)

    async def iniciar_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.participantes[0]:
            await interaction.response.send_message("Apenas o comando pode iniciar a ação!", ephemeral=True)
            return

        # Criar nova view apenas com botão de finalizar para o comando
        view = View(timeout=None)
        finalizar_btn = Button(
            label="Finalizar Ação",
            style=discord.ButtonStyle.primary,
            custom_id="finalizar_acao"
        )
        finalizar_btn.callback = self.finalizar_callback
        view.add_item(finalizar_btn)
        
        embed = discord.Embed(
            title=f"💎 Ação em Andamento: {self.acao_nome}",
            description="🚨 Atenção! A ação já está em curso.",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=LOGO_URL)
        embed.add_field(name="👮‍♂️ Comando", value=f"<@{self.participantes[0]}>", inline=False)
        
        # Lista detalhada de participantes
        participantes_texto = []
        for p in self.participantes:
            if p == self.participantes[0]:
                participantes_texto.append(f"<@{p}> (👑 Comando)")
            elif p == self.negociador:
                participantes_texto.append(f"<@{p}> (👨‍💼 Negociador)")
            else:
                participantes_texto.append(f"<@{p}>")
        
        embed.add_field(
            name="🛡️ Operadores Participantes",
            value="\n".join(participantes_texto),
            inline=False
        )
        
        await interaction.message.edit(embed=embed, view=view)
        await interaction.response.send_message("Ação iniciada com sucesso!", ephemeral=True)

        # Enviar log de início da ação
        log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            log_embed = discord.Embed(
                title="📝 Log de Ação",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            log_embed.add_field(name="Ação Iniciada", value=self.acao_nome, inline=False)
            log_embed.add_field(name="Comando", value=f"<@{self.participantes[0]}>", inline=False)
            log_embed.add_field(name="Total de Operadores", value=str(len(self.participantes)), inline=False)
            await log_channel.send(embed=log_embed)

    async def excluir_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.participantes[0]:
            await interaction.response.send_message("Apenas o comando pode excluir a ação!", ephemeral=True)
            return

        # Excluir a mensagem da ação
        await interaction.message.delete()
        await interaction.response.send_message(f"Ação **{self.acao_nome}** foi excluída com sucesso!", ephemeral=True)

        # Enviar log de exclusão
        log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            log_embed = discord.Embed(
                title="📝 Log de Ação",
                color=discord.Color.red(),
                timestamp=datetime.now()
            )
            log_embed.add_field(name="Ação Excluída", value=self.acao_nome, inline=False)
            log_embed.add_field(name="Excluída por", value=interaction.user.mention, inline=False)
            await log_channel.send(embed=log_embed)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # Verificar se é um botão de comando (iniciar/finalizar/excluir)
        if interaction.data["custom_id"] in ["iniciar_acao", "finalizar_acao", "excluir_acao"]:
            # Se não for o comando, mostrar mensagem e bloquear
            if interaction.user.id != self.participantes[0]:
                await interaction.response.send_message("Apenas o comando pode usar este botão!", ephemeral=True)
                return False

        if interaction.data["custom_id"] == "entrar_operador":
            if interaction.user.id in self.participantes:
                await interaction.response.send_message("Você já está participando desta ação!", ephemeral=True)
                return False
            
            if len(self.participantes) >= self.vagas_totais:
                await interaction.response.send_message("Todas as vagas já foram preenchidas!", ephemeral=True)
                return False
            
            self.participantes.append(interaction.user.id)
            
            embed = discord.Embed(
                title=f"💎 Ação em Andamento: {self.acao_nome}",
                description="🚨 Atenção! A ação está sendo preparada.",
                color=discord.Color.blue()
            )
            embed.set_thumbnail(url=LOGO_URL)
            embed.add_field(name="👮‍♂️ Comando", value=f"<@{self.participantes[0]}>", inline=False)
            
            # Lista detalhada de participantes
            participantes_texto = []
            for p in self.participantes:
                if p == self.participantes[0]:
                    participantes_texto.append(f"<@{p}> (👑 Comando)")
                elif p == self.negociador:
                    participantes_texto.append(f"<@{p}> (👨‍💼 Negociador)")
                else:
                    participantes_texto.append(f"<@{p}>")
            
            embed.add_field(
                name="👥 Vagas para operadores",
                value=f"🔢 {len(self.participantes)} / {self.vagas_totais} operadores\n\n**Participantes:**\n" + "\n".join(participantes_texto),
                inline=False
            )
            
            await interaction.message.edit(embed=embed)
            await interaction.response.send_message("Você entrou como operador!", ephemeral=True)

            # Enviar log de entrada na ação
            log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
            if log_channel:
                log_embed = discord.Embed(
                    title="📝 Log de Ação",
                    color=discord.Color.green(),
                    timestamp=datetime.now()
                )
                log_embed.add_field(name="Ação", value=self.acao_nome, inline=False)
                log_embed.add_field(name="Operador Entrou", value=interaction.user.mention, inline=False)
                log_embed.add_field(name="Total de Operadores", value=f"{len(self.participantes)}/{self.vagas_totais}", inline=False)
                await log_channel.send(embed=log_embed)

        elif interaction.data["custom_id"] == "entrar_negociador":
            if self.negociador:
                await interaction.response.send_message("Já existe um negociador nesta ação!", ephemeral=True)
                return False
                
            if interaction.user.id in self.participantes:
                await interaction.response.send_message("Você já está participando desta ação!", ephemeral=True)
                return False
            
            if len(self.participantes) >= self.vagas_totais:
                await interaction.response.send_message("Todas as vagas já foram preenchidas!", ephemeral=True)
                return False
            
            self.negociador = interaction.user.id
            self.participantes.append(interaction.user.id)
            
            embed = discord.Embed(
                title=f"💎 Ação em Andamento: {self.acao_nome}",
                description="🚨 Atenção! A ação está sendo preparada.",
                color=discord.Color.blue()
            )
            embed.set_thumbnail(url=LOGO_URL)
            embed.add_field(name="👮‍♂️ Comando", value=f"<@{self.participantes[0]}>", inline=False)
            
            # Lista detalhada de participantes
            participantes_texto = []
            for p in self.participantes:
                if p == self.participantes[0]:
                    participantes_texto.append(f"<@{p}> (👑 Comando)")
                elif p == self.negociador:
                    participantes_texto.append(f"<@{p}> (👨‍💼 Negociador)")
                else:
                    participantes_texto.append(f"<@{p}>")
            
            embed.add_field(
                name="👥 Vagas para operadores",
                value=f"🔢 {len(self.participantes)} / {self.vagas_totais} operadores\n\n**Participantes:**\n" + "\n".join(participantes_texto),
                inline=False
            )
            
            await interaction.message.edit(embed=embed)
            await interaction.response.send_message("Você entrou como negociador!", ephemeral=True)

            # Enviar log de entrada como negociador
            log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
            if log_channel:
                log_embed = discord.Embed(
                    title="📝 Log de Ação",
                    color=discord.Color.green(),
                    timestamp=datetime.now()
                )
                log_embed.add_field(name="Ação", value=self.acao_nome, inline=False)
                log_embed.add_field(name="Negociador Entrou", value=interaction.user.mention, inline=False)
                log_embed.add_field(name="Total de Operadores", value=f"{len(self.participantes)}/{self.vagas_totais}", inline=False)
                await log_channel.send(embed=log_embed)

        elif interaction.data["custom_id"] == "sair_operador":
            if interaction.user.id not in self.participantes:
                await interaction.response.send_message("Você não está participando desta ação!", ephemeral=True)
                return False
            
            if interaction.user.id == self.participantes[0]:
                await interaction.response.send_message("O comando não pode sair da ação! Use 'Finalizar Ação' para encerrar.", ephemeral=True)
                return False
            
            # Verificar se o usuário que está saindo é o negociador
            if interaction.user.id == self.negociador:
                self.negociador = None
            
            self.participantes.remove(interaction.user.id)
            
            embed = discord.Embed(
                title=f"💎 Ação em Andamento: {self.acao_nome}",
                description="🚨 Atenção! A ação está sendo preparada.",
                color=discord.Color.blue()
            )
            embed.set_thumbnail(url=LOGO_URL)
            embed.add_field(name="👮‍♂️ Comando", value=f"<@{self.participantes[0]}>", inline=False)
            
            # Lista detalhada de participantes
            participantes_texto = []
            for p in self.participantes:
                if p == self.participantes[0]:
                    participantes_texto.append(f"<@{p}> (👑 Comando)")
                elif p == self.negociador:
                    participantes_texto.append(f"<@{p}> (👨‍💼 Negociador)")
                else:
                    participantes_texto.append(f"<@{p}>")
            
            embed.add_field(
                name="👥 Vagas para operadores",
                value=f"🔢 {len(self.participantes)} / {self.vagas_totais} operadores\n\n**Participantes:**\n" + "\n".join(participantes_texto),
                inline=False
            )
            
            await interaction.message.edit(embed=embed)
            await interaction.response.send_message("Você saiu da operação!", ephemeral=True)

            # Enviar log de saída da ação
            log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
            if log_channel:
                log_embed = discord.Embed(
                    title="📝 Log de Ação",
                    color=discord.Color.red(),
                    timestamp=datetime.now()
                )
                log_embed.add_field(name="Ação", value=self.acao_nome, inline=False)
                log_embed.add_field(name="Operador Saiu", value=interaction.user.mention, inline=False)
                log_embed.add_field(name="Total de Operadores", value=f"{len(self.participantes)}/{self.vagas_totais}", inline=False)
                await log_channel.send(embed=log_embed)

        return True

    async def finalizar_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.participantes[0]:
            await interaction.response.send_message("Apenas o comando pode finalizar a ação!", ephemeral=True)
            return

        # Criar view de finalização
        view = FinalizarView(self.acao_nome, self.participantes[0], self.participantes, self.negociador)
        embed = discord.Embed(
            title=f"🎯 Finalizar Ação: {self.acao_nome}",
            description="Selecione o resultado da ação",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=LOGO_URL)
        embed.add_field(name="Comando", value=f"<@{self.participantes[0]}>", inline=False)
        
        # Lista detalhada de participantes
        participantes_texto = []
        for p in self.participantes:
            if p == self.participantes[0]:
                participantes_texto.append(f"<@{p}> (👑 Comando)")
            elif p == self.negociador:
                participantes_texto.append(f"<@{p}> (👨‍💼 Negociador)")
            else:
                participantes_texto.append(f"<@{p}>")
        
        embed.add_field(name="Participantes", value="\n".join(participantes_texto), inline=False)
        
        await interaction.message.edit(view=None)  # Remove os botões antigos
        await interaction.response.send_message(embed=embed, view=view)

        # Enviar log de finalização
        log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            log_embed = discord.Embed(
                title="📝 Log de Ação",
                color=discord.Color.gold(),
                timestamp=datetime.now()
            )
            log_embed.add_field(name="Ação Finalizada", value=self.acao_nome, inline=False)
            log_embed.add_field(name="Comando", value=f"<@{self.participantes[0]}>", inline=False)
            log_embed.add_field(name="Total de Participantes", value=str(len(self.participantes)), inline=False)
            log_embed.add_field(name="Lista de Participantes", value="\n".join(participantes_texto), inline=False)
            await log_channel.send(embed=log_embed)

class Bot(discord.Client):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # Registrar o comando limpar_acoes
        @self.tree.command(name="limpar_acoes", description="Limpa todas as ações do canal (requer cargo específico)")
        async def limpar_acoes(interaction: discord.Interaction):
            # Verificar se o usuário tem o cargo necessário
            if not any(role.id == CARGO_ADMIN_ID for role in interaction.user.roles):
                await interaction.response.send_message("❌ Você não tem permissão para usar este comando!", ephemeral=True)
                return

            channel = interaction.channel
            count = 0

            # Enviar mensagem inicial
            await interaction.response.send_message("🔄 Iniciando limpeza das ações...", ephemeral=True)

            # Limpar mensagens do bot no canal
            async for message in channel.history(limit=100):
                if message.author == self.user:
                    await message.delete()
                    count += 1

            # Recriar a mensagem inicial do sistema
            escala_embed = discord.Embed(
                title="🔫 Escala de Ações BETA",
                description=(
                    "🚨 **Atenção!**\n\n"
                    "👮‍♂️ Apenas 1 Comando e 1 Negociador por ação\n"
                    "🎯 Operadores Táticos serão definidos conforme a ação\n\n"
                    "🛠️ Sistema em fase de desenvolvimento\n"
                    "❗ Em caso de erro, procure: Gestora Ana Bellini"
                ),
                color=discord.Color.blue()
            )
            escala_embed.set_thumbnail(url=LOGO_URL)
            await channel.send(embed=escala_embed, view=CriarAcaoButton())

            # Enviar log da limpeza
            log_channel = self.get_channel(LOG_CHANNEL_ID)
            if log_channel:
                log_embed = discord.Embed(
                    title="📝 Log do Sistema",
                    description=f"Sistema de Ações foi limpo por {interaction.user.mention}\n{count} mensagens foram removidas",
                    color=discord.Color.orange(),
                    timestamp=datetime.now()
                )
                await log_channel.send(embed=log_embed)

            # Atualizar a mensagem de resposta
            await interaction.edit_original_response(content=f"✅ Limpeza concluída! {count} mensagens foram removidas.")

        await self.tree.sync()

    async def on_ready(self):
        print(f'Bot está online como {self.user}')
        channel_ids = [1362542006500589718]
        
        for channel_id in channel_ids:
            channel = self.get_channel(channel_id)
            if channel:
                # Limpar mensagens antigas do bot
                async for message in channel.history(limit=100):
                    if message.author == self.user:
                        await message.delete()
                
                # Enviar mensagem de escala de ações
                escala_embed = discord.Embed(
                    title="🔫 Escala de Ações BETA",
                    description=(
                        "🚨 **Atenção!**\n\n"
                        "👮‍♂️ Apenas 1 Comando e 1 Negociador por ação\n"
                        "🎯 Operadores Táticos serão definidos conforme a ação\n\n"
                        "🛠️ Sistema em fase de desenvolvimento\n"
                        "❗ Em caso de erro, procure: Gestora Ana Bellini"
                    ),
                    color=discord.Color.blue()
                )
                escala_embed.set_thumbnail(url=LOGO_URL)
                await channel.send(embed=escala_embed, view=CriarAcaoButton())

                # Enviar log de inicialização
                log_channel = self.get_channel(LOG_CHANNEL_ID)
                if log_channel:
                    log_embed = discord.Embed(
                        title="📝 Log do Sistema",
                        description="Sistema de Ações foi inicializado",
                        color=discord.Color.blue(),
                        timestamp=datetime.now()
                    )
                    await log_channel.send(embed=log_embed)

client = Bot()
client.run(os.getenv('TOKEN_DISCORD'))