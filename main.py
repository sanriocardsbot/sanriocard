import os
import json
import asyncio
import logging
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.error import TelegramError
import random
import time
import sqlite3
from typing import Dict, List, Optional, Tuple
import re

# CONFIGURAÇÕES - Railway vai usar variáveis de ambiente
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', "7638112023:AAEB8Pt7lJd65cjYypLS7HV_WHN44YaMuCo")
CHANNEL_ID = int(os.getenv('CHANNEL_ID', '-1002704327397'))
ADMIN_ID = int(os.getenv('ADMIN_ID', '7413426450'))

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Caminho do banco de dados (Railway persiste em /app/data)
DB_PATH = os.getenv('DATABASE_PATH', '/app/data/sanrio_bot.db')

class Database:
    def __init__(self):
        # Criar diretório se não existir
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        self.init_db()
    
    def init_db(self):
        """Inicializar banco de dados"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Tabela de usuários
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                docinhos INTEGER DEFAULT 20,
                lacinhos INTEGER DEFAULT 50,
                sugar_hearts INTEGER DEFAULT 0,
                total_cards INTEGER DEFAULT 0,
                is_vip BOOLEAN DEFAULT FALSE,
                bio TEXT DEFAULT 'Sem biografia definida',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                warns INTEGER DEFAULT 0,
                is_banned BOOLEAN DEFAULT FALSE,
                married_card_id INTEGER DEFAULT NULL
            )
        ''')
        
        # Tabela de cartas dos usuários
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_cards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                card_id INTEGER,
                count INTEGER DEFAULT 1,
                is_favorite BOOLEAN DEFAULT FALSE,
                is_not_tradeable BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Tabela de wishlist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS wishlist (
                user_id INTEGER,
                card_id INTEGER,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, card_id)
            )
        ''')
        
        # Tabela de cooldowns
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cooldowns (
                user_id INTEGER,
                command TEXT,
                last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, command)
            )
        ''')
        
        # Tabela de imagens
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT, -- 'card', 'collection', 'universe', 'wishlist'
                reference_id INTEGER, -- card_id, collection_id, etc
                file_id TEXT,
                file_path TEXT,
                added_by INTEGER,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de trocas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_user INTEGER,
                to_user INTEGER,
                offer_card_id INTEGER,
                offer_quantity INTEGER,
                want_card_id INTEGER,
                want_quantity INTEGER,
                status TEXT DEFAULT 'pending', -- pending, accepted, rejected, expired
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP
            )
        ''')
        
        # Tabela de configurações do bot
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bot_config (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("✅ Banco de dados inicializado com sucesso!")
    
    def user_exists(self, user_id: int) -> bool:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM users WHERE user_id = ?', (user_id,))
        exists = cursor.fetchone() is not None
        conn.close()
        return exists
    
    def create_user(self, user_id: int, username: str):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO users (user_id, username, docinhos, lacinhos, sugar_hearts)
            VALUES (?, ?, 20, 50, 0)
        ''', (user_id, username))
        conn.commit()
        conn.close()
    
    def get_user(self, user_id: int) -> Dict:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'user_id': row[0],
                'username': row[1],
                'docinhos': row[2],
                'lacinhos': row[3],
                'sugar_hearts': row[4],
                'total_cards': row[5],
                'is_vip': bool(row[6]),
                'bio': row[7],
                'warns': row[9],
                'is_banned': bool(row[10]),
                'married_card_id': row[11]
            }
        return None
    
    def update_user_currency(self, user_id: int, docinhos: int = 0, lacinhos: int = 0, sugar_hearts: int = 0):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users 
            SET docinhos = MAX(0, docinhos + ?), 
                lacinhos = MAX(0, lacinhos + ?), 
                sugar_hearts = MAX(0, sugar_hearts + ?)
            WHERE user_id = ?
        ''', (docinhos, lacinhos, sugar_hearts, user_id))
        
        # Verificar se virou VIP (1000+ corações)
        cursor.execute('SELECT sugar_hearts FROM users WHERE user_id = ?', (user_id,))
        hearts = cursor.fetchone()[0]
        if hearts >= 1000:
            cursor.execute('UPDATE users SET is_vip = TRUE WHERE user_id = ?', (user_id,))
        
        conn.commit()
        conn.close()
    
    def check_cooldown(self, user_id: int, command: str, cooldown_seconds: int) -> bool:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT last_used FROM cooldowns WHERE user_id = ? AND command = ?
        ''', (user_id, command))
        
        row = cursor.fetchone()
        if not row:
            conn.close()
            return True
        
        last_used = datetime.fromisoformat(row[0])
        now = datetime.now()
        time_diff = (now - last_used).total_seconds()
        
        conn.close()
        return time_diff >= cooldown_seconds
    
    def set_cooldown(self, user_id: int, command: str):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO cooldowns (user_id, command, last_used)
            VALUES (?, ?, ?)
        ''', (user_id, command, datetime.now().isoformat()))
        conn.commit()
        conn.close()
    
    def add_card_to_user(self, user_id: int, card_id: int):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar se já tem a carta
        cursor.execute('SELECT count FROM user_cards WHERE user_id = ? AND card_id = ?', (user_id, card_id))
        row = cursor.fetchone()
        
        if row:
            cursor.execute('UPDATE user_cards SET count = count + 1 WHERE user_id = ? AND card_id = ?', (user_id, card_id))
        else:
            cursor.execute('INSERT INTO user_cards (user_id, card_id, count) VALUES (?, ?, 1)', (user_id, card_id))
        
        # Atualizar total de cartas
        cursor.execute('UPDATE users SET total_cards = total_cards + 1 WHERE user_id = ?', (user_id,))
        
        conn.commit()
        conn.close()
    
    def get_user_card_count(self, user_id: int, card_id: int) -> int:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT count FROM user_cards WHERE user_id = ? AND card_id = ?', (user_id, card_id))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else 0
    
    def ban_user(self, user_id: int):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET is_banned = TRUE WHERE user_id = ?', (user_id,))
        conn.commit()
        conn.close()
    
    def get_bot_stats(self) -> Dict:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        stats = {}
        cursor.execute('SELECT COUNT(*) FROM users')
        stats['total_users'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM users WHERE is_banned = TRUE')
        stats['banned_users'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM users WHERE is_vip = TRUE')
        stats['vip_users'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT SUM(total_cards) FROM users')
        stats['total_cards'] = cursor.fetchone()[0] or 0
        
        conn.close()
        return stats

class CardSystem:
    def __init__(self):
        self.collections = self._init_collections()
        self.cards = self._init_cards()
    
    def _init_collections(self):
        return {
            'asia': [
                {'id': 1, 'name': 'TWICE', 'universe': 'asia'},
                {'id': 2, 'name': 'BLACKPINK', 'universe': 'asia'},
                {'id': 3, 'name': 'LE SSERAFIM', 'universe': 'asia'},
                {'id': 4, 'name': 'aespa', 'universe': 'asia'},
                {'id': 5, 'name': 'RIIZE', 'universe': 'asia'},
                {'id': 6, 'name': '&TEAM', 'universe': 'asia'}
            ],
            'music': [
                {'id': 11, 'name': 'Taylor Swift', 'universe': 'music'},
                {'id': 12, 'name': 'Ariana Grande', 'universe': 'music'}
            ],
            'cinema': [
                {'id': 15, 'name': 'Marvel', 'universe': 'cinema'},
                {'id': 16, 'name': 'Disney', 'universe': 'cinema'}
            ],
            'anime': [
                {'id': 19, 'name': 'Naruto', 'universe': 'anime'},
                {'id': 20, 'name': 'One Piece', 'universe': 'anime'}
            ],
            'diversi': [
                {'id': 23, 'name': 'Celebridades', 'universe': 'diversi'},
                {'id': 24, 'name': 'Influencers', 'universe': 'diversi'}
            ]
        }
    
    def _init_cards(self):
        cards = {}
        
        # TWICE (IDs 1-9) - SOMENTE ELAS TÊM CORES ESPECIAIS
        twice_members = [
            {'id': 1, 'name': 'Dahyun', 'rarity': 'gold', 'collection_id': 1, 'collection_name': 'TWICE'},
            {'id': 2, 'name': 'Chaeyoung', 'rarity': 'gold', 'collection_id': 1, 'collection_name': 'TWICE'},
            {'id': 3, 'name': 'Mina', 'rarity': 'silver', 'collection_id': 1, 'collection_name': 'TWICE'},
            {'id': 4, 'name': 'Nayeon', 'rarity': 'silver', 'collection_id': 1, 'collection_name': 'TWICE'},
            {'id': 5, 'name': 'Jeongyeon', 'rarity': 'silver', 'collection_id': 1, 'collection_name': 'TWICE'},
            {'id': 6, 'name': 'Tzuyu', 'rarity': 'silver', 'collection_id': 1, 'collection_name': 'TWICE'},
            {'id': 7, 'name': 'Sana', 'rarity': 'silver', 'collection_id': 1, 'collection_name': 'TWICE'},
            {'id': 8, 'name': 'Momo', 'rarity': 'silver', 'collection_id': 1, 'collection_name': 'TWICE'},
            {'id': 9, 'name': 'Jihyo', 'rarity': 'silver', 'collection_id': 1, 'collection_name': 'TWICE'}
        ]
        
        for card in twice_members:
            cards[card['id']] = card
        
        return cards
    
    def get_collections_by_universe(self, universe: str):
        return self.collections.get(universe, [])
    
    def pull_random_card(self, collection_id: int):
        collection_cards = [card for card in self.cards.values() if card['collection_id'] == int(collection_id)]
        if not collection_cards:
            return None
        
        # Probabilidades de raridade: 15% ouro, 35% prata, 50% bronze
        rand = random.randint(1, 100)
        if rand <= 15:
            target_rarity = 'gold'
        elif rand <= 50:
            target_rarity = 'silver'
        else:
            target_rarity = 'bronze'
        
        # Filtrar por raridade desejada
        rarity_cards = [card for card in collection_cards if card['rarity'] == target_rarity]
        
        # Se não houver cartas da raridade, pegar qualquer uma
        if not rarity_cards:
            rarity_cards = collection_cards
        
        return random.choice(rarity_cards)
    
    def get_card_by_id(self, card_id: int):
        return self.cards.get(card_id)

class SanrioCardsBot:
    def __init__(self):
        self.db = Database()
        self.cards = CardSystem()
        logger.info("🎀 SanrioCardsBot inicializado!")

    async def check_channel_membership(self, user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Verificar se usuário está no canal"""
        try:
            member = await context.bot.get_chat_member(CHANNEL_ID, user_id)
            return member.status in ['member', 'administrator', 'creator']
        except TelegramError:
            return False

    async def check_user_access(self, user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Verificar acesso do usuário (canal + não banido)"""
        user_data = self.db.get_user(user_id)
        if user_data and user_data['is_banned']:
            return False
        return await self.check_channel_membership(user_id, context)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /start"""
        user_id = update.effective_user.id
        username = update.effective_user.username or "Usuário"

        if not await self.check_user_access(user_id, context):
            await update.message.reply_text(
                "✋🏻 Parece que você não está em nosso canal. É necessário estar no canal para usar este comando.\n\n"
                "Entre em: https://t.me/sanriocardbot"
            )
            return

        # Registrar usuário se não existir
        if not self.db.user_exists(user_id):
            self.db.create_user(user_id, username)
            logger.info(f"✅ Novo usuário registrado: {user_id} (@{username})")

        welcome_text = (
            "🌟 Bem-vindo ao SanrioCardsBot!\n\n"
            "Você está prestes a entrar em um universo onde o K-pop encontra a fofura Sanrio, "
            "com cartas colecionáveis de tirar o fôlego.\n\n"
            "Comece com /docinho e ganhe seus primeiros docinhos! 🍬\n\n"
            "Use /ajuda para ver todos os comandos disponíveis!"
        )

        await update.message.reply_text(welcome_text)

    async def perfil(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /perfil"""
        user_id = update.effective_user.id

        if not await self.check_user_access(user_id, context):
            await update.message.reply_text(
                "✋🏻 Parece que você não está em nosso canal. É necessário estar no canal para usar este comando."
            )
            return

        user_data = self.db.get_user(user_id)
        if not user_data:
            await update.message.reply_text("❌ Usuário não encontrado. Use /start primeiro.")
            return

        username = update.effective_user.username or "Usuário"

        perfil_text = (
            f"🎀 Nick: @{username}\n"
            f"📝 Bio: {user_data['bio']}\n"
            f"📦 Cartas: {user_data['total_cards']}\n"
            f"💖 Corações de Açúcar: {user_data['sugar_hearts']}\n"
            f"🍭 Docinhos: {user_data['docinhos']}\n"
        )

        if user_data['is_vip']:
            perfil_text += "👑 Status: VIP Sanrio\n"

        await update.message.reply_text(perfil_text)

    async def docinho(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /docinho - Sistema principal de puxar cartas"""
        user_id = update.effective_user.id

        if not await self.check_user_access(user_id, context):
            await update.message.reply_text(
                "✋🏻 Parece que você não está em nosso canal. É necessário estar no canal para usar este comando."
            )
            return

        user_data = self.db.get_user(user_id)
        if not user_data:
            await update.message.reply_text("❌ Use /start primeiro.")
            return

        # Verificar cooldown de 6 horas para docinhos grátis
        if self.db.check_cooldown(user_id, 'free_docinhos', 6 * 3600):
            bonus_docinhos = 12 if user_data['is_vip'] else 10  # VIP ganha +2
            self.db.update_user_currency(user_id, docinhos=bonus_docinhos)
            self.db.set_cooldown(user_id, 'free_docinhos')
            user_data['docinhos'] += bonus_docinhos

        if user_data['docinhos'] < 1:
            await update.message.reply_text(
                "😢 Você não tem docinhos suficientes!\n"
                "Aguarde 6 horas para ganhar mais docinhos gratuitos!"
            )
            return

        # Mostrar saldo e universos
        keyboard = [
            [InlineKeyboardButton("🍥 Asialand", callback_data="universe_asia")],
            [InlineKeyboardButton("🥡 Animeland", callback_data="universe_anime")],
            [InlineKeyboardButton("🎬 Cineland", callback_data="universe_cinema")],
            [InlineKeyboardButton("🎡 Diversiland", callback_data="universe_diversi")],
            [InlineKeyboardButton("🎸 Musiland", callback_data="universe_music")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        docinho_text = f"🎀 Você possui {user_data['docinhos']} docinhos!\n\nEscolha um universo para explorar:"

        await update.message.reply_text(docinho_text, reply_markup=reply_markup)

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Gerenciar callbacks dos botões"""
        query = update.callback_query
        await query.answer()

        user_id = query.from_user.id
        data = query.data

        if not await self.check_user_access(user_id, context):
            await query.edit_message_text(
                "✋🏻 Parece que você não está em nosso canal. É necessário estar no canal para usar este comando."
            )
            return

        if data.startswith("universe_"):
            await self.show_collections(query, data.split("_")[1])
        elif data.startswith("collection_"):
            parts = data.split("_", 2)
            await self.pull_card(query, parts[1], parts[2])

    async def show_collections(self, query, universe):
        """Mostrar coleções de um universo"""
        collections = self.cards.get_collections_by_universe(universe)

        keyboard = []
        for collection in collections:
            emoji = "🍭" if collection['name'] == "TWICE" else ""
            button_text = f"{collection['name']} {emoji}".strip()
            callback_data = f"collection_{universe}_{collection['id']}"
            keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])

        reply_markup = InlineKeyboardMarkup(keyboard)

        universe_names = {
            'asia': '🍥 Asialand',
            'anime': '🥡 Animeland', 
            'cinema': '🎬 Cineland',
            'diversi': '🎡 Diversiland',
            'music': '🎸 Musiland'
        }

        await query.edit_message_text(
            text=f"Escolha uma coleção de {universe_names.get(universe, universe)}:",
            reply_markup=reply_markup
        )

    async def pull_card(self, query, universe, collection_id):
        """Puxar uma carta"""
        user_id = query.from_user.id
        user_data = self.db.get_user(user_id)

        if user_data['docinhos'] < 1:
            await query.edit_message_text("😢 Você não tem docinhos suficientes!")
            return

        # Deduzir docinho
        self.db.update_user_currency(user_id, docinhos=-1)

        # Puxar carta aleatória
        card = self.cards.pull_random_card(collection_id)
        if not card:
            await query.edit_message_text("❌ Erro ao puxar carta.")
            return

        # Adicionar carta ao usuário
        self.db.add_card_to_user(user_id, card['id'])
        user_card_count = self.db.get_user_card_count(user_id, card['id'])

        # Mensagens bonitas exatamente como solicitado
        if card['rarity'] == 'gold':
            if random.choice([True, False]):
                char_text = "🎀 My Melody achou uma carta muito especial para sua coleção."
                char_emoji = "🐰"
            else:
                char_text = "🎀 Cinnamoroll tem um achadinho doce para você!"
                char_emoji = "🐶"
        else:  # silver ou bronze
            char_text = "🎀 Hello Kitty trouxe uma carta linda para a sua coleção!"
            char_emoji = "🐈"

        # Emoji de raridade
        rarity_emojis = {'gold': '🥇', 'silver': '🥈', 'bronze': '🥉'}
        rarity_emoji = rarity_emojis[card['rarity']]

        # EMOJI ESPECIAL SOMENTE PARA TWICE
        heart_emoji = ""
        if card['collection_name'] == "TWICE":
            heart_colors = {
                'Dahyun': '🤍', 'Chaeyoung': '❤️', 'Mina': '🩵',
                'Nayeon': '🩵', 'Jeongyeon': '💚', 'Tzuyu': '💙',
                'Sana': '💜', 'Momo': '🩷', 'Jihyo': '🧡'
            }
            heart_emoji = f" {heart_colors.get(card['name'], '')}"

        username = query.from_user.username or "Usuário"

        # Formato exato das mensagens
        card_text = (
            f"{char_text}\n\n"
            f"{rarity_emoji}{card['id']}. {card['name']}{heart_emoji}\n"
            f"💗 {card['collection_name']}\n\n"
            f"{char_emoji} {username} — {user_card_count}x"
        )

        await query.edit_message_text(card_text)
        logger.info(f"🃏 {username} puxou carta: {card['name']} (ID: {card['id']})")

    async def ajuda(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /ajuda - Mostrar todos os comandos"""
        ajuda_text = (
            "📖 Comandos do SanrioCardsBot\n\n"
            
            "🎮 PRINCIPAIS:\n"
            "/start - Iniciar o bot\n"
            "/docinho - Ganhar cartas e docinhos\n"
            "/perfil - Ver seu perfil\n\n"
            
            "🛠️ ADMIN (apenas @thvartic):\n"
            "/stats - Estatísticas do bot\n"
            "/ban [user_id] - Banir usuário\n\n"
            
            "💖 Desenvolvido com amor para a comunidade!\n"
            "🆘 Suporte: @sanriocrdsuportebot"
        )
        
        await update.message.reply_text(ajuda_text)

    # COMANDOS ADMINISTRATIVOS
    async def admin_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /stats - Estatísticas do bot (Admin)"""
        if update.effective_user.id != ADMIN_ID:
            return

        stats = self.db.get_bot_stats()
        
        stats_text = (
            f"📊 Estatísticas do SanrioCardsBot\n\n"
            f"👥 Total de Usuários: {stats['total_users']}\n"
            f"🚫 Usuários Banidos: {stats['banned_users']}\n"
            f"👑 Usuários VIP: {stats['vip_users']}\n"
            f"🃏 Total de Cartas: {stats['total_cards']}\n\n"
            f"🚀 Bot rodando no Railway!"
        )
        
        await update.message.reply_text(stats_text)

    async def admin_ban(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /ban - Banir usuário (Admin)"""
        if update.effective_user.id != ADMIN_ID:
            return

        if not context.args:
            await update.message.reply_text("Use: /ban [user_id]")
            return

        try:
            target_user_id = int(context.args[0])
        except ValueError:
            await update.message.reply_text("❌ ID inválido.")
            return

        self.db.ban_user(target_user_id)
        await update.message.reply_text(f"🚫 Usuário {target_user_id} banido.")
        logger.info(f"🚫 Admin baniu usuário: {target_user_id}")

def main():
    """Função principal"""
    logger.info("🚀 Iniciando SanrioCardsBot no Railway...")
    
    bot = SanrioCardsBot()
    
    # Criar aplicação
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Comandos principais
    application.add_handler(CommandHandler("start", bot.start))
    application.add_handler(CommandHandler("perfil", bot.perfil))
    application.add_handler(CommandHandler("docinho", bot.docinho))
    application.add_handler(CommandHandler("ajuda", bot.ajuda))
    
    # Comandos administrativos
    application.add_handler(CommandHandler("stats", bot.admin_stats))
    application.add_handler(CommandHandler("ban", bot.admin_ban))
    
    # Callback handlers
    application.add_handler(CallbackQueryHandler(bot.handle_callback))
    
    # Executar bot
    logger.info("🎀 SanrioCardsBot iniciado com sucesso!")
    application.run_polling()

if __name__ == '__main__':
    main()
