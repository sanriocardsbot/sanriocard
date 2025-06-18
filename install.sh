#!/bin/bash
# Script de instalação do SanrioCardsBot

echo "🎀 Instalando SanrioCardsBot..."

# Instalar dependências
echo "📦 Instalando dependências Python..."
pip install -r requirements.txt

# Criar diretórios necessários
echo "📁 Criando estrutura de pastas..."
mkdir -p assets/cards
mkdir -p assets/collections
mkdir -p assets/universe
mkdir -p assets/wishlist

echo "✅ Instalação concluída!"
echo "🔧 O bot está configurado e pronto para uso"
echo "🚀 Execute com: python main.py"
echo ""
echo "📋 Comandos administrativos disponíveis:"
echo "  /stats - Estatísticas do bot"
echo "  /ban [user_id] - Banir usuário"
echo "  /unban [user_id] - Desbanir usuário"
echo "  /warn [user_id] - Dar advertência"
echo "  /give [user_id] [tipo] [quantidade] - Dar moedas"
echo "  /addimg [tipo] [id] - Adicionar imagem"
echo "  /broadcast [mensagem] - Enviar para todos"
echo ""
echo "🎀 SanrioCardsBot pronto para uso!"
