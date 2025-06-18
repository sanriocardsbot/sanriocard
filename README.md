# 🎀 SanrioCardsBot - Versão Completa

Bot de cartas colecionáveis que une K-pop, cinema, anime e muito mais com a fofura dos personagens Sanrio!

## 🚀 Funcionalidades Principais

### 🎮 Sistema de Cartas
- **Raridades**: 🥇 Ouro (15%), 🥈 Prata (35%), 🥉 Bronze (50%)
- **Universos**: 🍥 Asialand, 🥡 Animeland, 🎬 Cineland, 🎡 Diversiland, 🎸 Musiland
- **TWICE Especial**: Cada membro tem cor única no coração

### 💰 Sistema de Economia
- **Docinhos**: Moeda principal (inicia com 20)
- **Lacinhos**: Moeda secundária (inicia com 50)  
- **Corações de Açúcar**: Para virar VIP (1000 = VIP)

### 🛡️ Segurança & Anti-Fraude
- Verificação obrigatória de canal
- Sistema de cooldowns
- Validação de entrada
- Sistema de warns/ban
- Cartas não trocáveis

## 📋 Comandos Disponíveis

### 🎮 PRINCIPAIS
- `/start` - Iniciar o bot
- `/docinho` - Ganhar cartas e docinhos
- `/perfil` - Ver seu perfil
- `/economia` - Ver seu saldo
- `/bonusdiario` - Bônus diário

### 🃏 CARTAS
- `/col [nome]` - Ver coleção específica
- `/carta [id]` - Ver carta específica
- `/cartas` - Ver todas suas cartas
- `/repetidas` - Ver cartas repetidas
- `/minhascolecoes` - Progresso das coleções

### ⭐ FAVORITAS & WISHLIST
- `/favorita [id]` - Definir favorita
- `/favoritas` - Ver favoritas
- `/wl` - Ver wishlist (sua ou de alguém)
- `/addwl [id]` - Adicionar à wishlist
- `/rwl [id]` - Remover da wishlist

### ♻️ TROCAS & DOAÇÕES
- `/trocar [id] [qtd] - [id] [qtd]` - Propor troca
- `/mimo [id] [qtd]` - Doar carta
- `/doarwl` - Doar cartas da wishlist
- `/carinho` - Enviar coração de açúcar

### 🔧 OUTROS
- `/bio` - Definir biografia
- `/nt [id]` - Marcar como não trocável
- `/comprar [qtd]` - Comprar docinhos
- `/ajuda` - Lista de comandos
- `/sobre` - Sobre o bot

## 👑 Comandos Administrativos

### 📊 GESTÃO
- `/stats` - Estatísticas do bot
- `/ban [user_id]` - Banir usuário
- `/unban [user_id]` - Desbanir usuário
- `/warn [user_id]` - Dar advertência

### 💰 ECONOMIA
- `/give [user_id] [tipo] [quantidade]` - Dar moedas
- Tipos: docinhos, lacinhos, hearts

### 🖼️ IMAGENS
- `/addimg [tipo] [id]` - Adicionar imagem
- Tipos: card, collection, universe, wishlist
- Responda a uma foto com o comando

### 📢 COMUNICAÇÃO
- `/broadcast [mensagem]` - Enviar para todos

## 🎯 Coleções Disponíveis

### 🍥 Asialand (K-pop)
- **TWICE** (IDs 1-9) - Cores especiais únicas
- **BLACKPINK** (IDs 10-13)
- **LE SSERAFIM** (IDs 14-18)
- **aespa** (IDs 19-22)
- **RIIZE** (IDs 23-29)
- **&TEAM** (IDs 30-38)
- **NewJeans**, **IVE**, **ITZY**, **NMIXX**

### 🎸 Musiland (Artistas Internacionais)
- Taylor Swift, Ariana Grande, Billie Eilish, Dua Lipa

### 🎬 Cineland (Cinema)
- Marvel, Disney, Harry Potter, Star Wars

### 🥡 Animeland (Anime)
- Naruto, One Piece, Attack on Titan, Demon Slayer

### 🎡 Diversiland (Diversos)
- Celebridades, Influencers, Esportes, Política

## 💖 TWICE Especial

Cada membro do TWICE tem uma cor única no coração:
- Dahyun 🤍 (ID 1)
- Chaeyoung ❤️ (ID 2)
- Mina 🩵 (ID 3)
- Nayeon 🩵 (ID 4)
- Jeongyeon 💚 (ID 5)
- Tzuyu 💙 (ID 6)
- Sana 💜 (ID 7)
- Momo 🩷 (ID 8)
- Jihyo 🧡 (ID 9)

## 🎨 Personagens Sanrio

- **🥇 Ouro**: My Melody 🐰 / Cinnamoroll 🐶
- **🥈 Prata**: Hello Kitty 🐈
- **🥉 Bronze**: Hello Kitty 🐈

## ⚙️ Configuração

1. **Token**: `7638112023:AAEB8Pt7lJd65cjYypLS7HV_WHN44YaMuCo`
2. **Canal**: `-1002704327397`
3. **Admin**: `7413426450` (@thvartic)

## 🚀 Deploy no Railway

Bot de cartas colecionáveis rodando no Railway!

1. Conecte seu GitHub ao Railway
2. Selecione este repositório  
3. Configure as variáveis de ambiente
4. Deploy automático!

## 🔧 Variáveis de Ambiente

- `TELEGRAM_TOKEN`: Token do bot
- `CHANNEL_ID`: ID do canal (-1002704327397)
- `ADMIN_ID`: ID do admin (7413426450)

## 🗄️ Banco de Dados

O bot usa SQLite com as seguintes tabelas:
- `users` - Dados dos usuários
- `user_cards` - Cartas dos usuários
- `wishlist` - Lista de desejos
- `cooldowns` - Controle de tempo
- `images` - Sistema de imagens
- `trades` - Sistema de trocas
- `bot_config` - Configurações

## 🚀 Execução

\`\`\`bash
pip install -r requirements.txt
python main.py
\`\`\`

## 🆘 Suporte

- **Bot de Suporte**: @sanriocrdsuportebot
- **Canal**: https://t.me/sanriocardbot

---

Desenvolvido com 💖 para a comunidade de colecionadores!
