"""
Bot do Telegram para jogar Jokenpo (Pedra, Papel, Tesoura) usando uma IA
para classificar a imagem da mão do usuário.
"""

# --- IMPORTAÇÃO DAS BIBLIOTECAS ---
from PIL import Image
import os
import logging
import sys
import numpy as np
import random
from tensorflow.keras.models import load_model
from rembg import remove
from rembg.session_factory import new_session # Otimização: para escolher um modelo mais leve
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# --- CONSTANTES E CONFIGURAÇÕES GLOBAIS ---
# Tenta pegar o token da linha de comando
TOKEN = sys.argv[1] if len(sys.argv) > 1 else None

# Nomes de pastas e arquivos para fácil manutenção
PASTA_IMAGENS_RECEBIDAS = './Telegram_Imagens_Recebidas/'
PASTA_IMAGENS_PROCESSADAS = './Imagens_Processadas_Sem_Fundo/'
ARQUIVO_MODELO = 'keras_model.h5'
ARQUIVO_LABELS = 'labels.txt'

# Configurações do modelo de IA e do jogo
TAMANHO_IMAGEM = (224, 224)
# OTIMIZAÇÃO: Usaremos o modelo 'u2netp', que é mais rápido que o padrão
MODELO_REMBG = "u2netp" 

# Regras do jogo em um dicionário para código mais limpo
REGRAS_VITORIA = {
    "Pedra": "Tesoura",
    "Tesoura": "Papel",
    "Papel": "Pedra"
}

# --- CONFIGURAÇÃO DO LOGGING ---
# Define como as mensagens de status e erro serão exibidas no terminal
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


# --- FUNÇÕES AUXILIARES ---

def classifica_imagem(imagem_pil, context):
    """
    Prepara e classifica uma imagem usando o modelo Keras.
    Recebe uma imagem (formato PIL) e o contexto do bot.
    Retorna a classe prevista e o score de confiança.
    """
    # Pega o modelo e as classes que foram carregados no início
    model = context.bot_data['modelo_keras']
    nomes_classes = context.bot_data['nomes_classes']

    # Prepara um array numpy no formato que o modelo espera
    data = np.ndarray(shape=(1, TAMANHO_IMAGEM[0], TAMANHO_IMAGEM[1], 3), dtype=np.float32)
    
    # Redimensiona a imagem para o tamanho exigido pelo modelo
    # OTIMIZAÇÃO: Image.Resampling.NEAREST é o algoritmo mais rápido de resize
    image_resized = imagem_pil.convert("RGB").resize(TAMANHO_IMAGEM, Image.Resampling.NEAREST)
    
    # Normaliza os pixels da imagem para o intervalo [-1, 1]
    image_array = np.asarray(image_resized)
    normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1
    data[0] = normalized_image_array

    # Executa a predição
    prediction = model.predict(data, verbose=0)
    index = np.argmax(prediction)
    
    return nomes_classes[index], prediction[0][index]


# --- HANDLERS (COMANDOS DO BOT) ---

async def start(update, context):
    """Função executada quando o usuário envia /start."""
    await update.message.reply_text('Olá! Envie uma imagem da sua mão (pedra, papel ou tesoura) e eu jogarei Jokenpo com você.')

async def help_command(update, context):
    """Função executada quando o usuário envia /help."""
    await update.message.reply_text('Este bot usa uma IA para reconhecer sua jogada. Apenas envie uma foto!')

async def processa_imagem(update, context):
    """Função principal, executada quando o usuário envia uma foto."""
    # Garante que as pastas de destino existam
    os.makedirs(PASTA_IMAGENS_RECEBIDAS, exist_ok=True)
    os.makedirs(PASTA_IMAGENS_PROCESSADAS, exist_ok=True)
        
    try:
        # Baixa a foto enviada pelo usuário
        photo_file = await update.message.photo[-1].get_file()
        file_path = os.path.join(PASTA_IMAGENS_RECEBIDAS, f"{photo_file.file_id}.jpg")
        await photo_file.download_to_drive(file_path)
        logger.info(f"Processando arquivo: {file_path}")
        
        imagem_original = Image.open(file_path)

        # 1. PRÉ-CLASSIFICAÇÃO: Roda a IA na imagem original para um teste rápido
        logger.info("Realizando pré-classificação...")
        classe_inicial, confianca_inicial = classifica_imagem(imagem_original, context)
        jogada_inicial = classe_inicial[2:].strip()

        # Se a imagem não parece uma jogada válida, avisa o usuário e para aqui
        if jogada_inicial == "Nenhum(a)":
            logger.info("Pré-classificação: 'Nenhum(a)'. Processo interrompido.")
            resposta = f'Sua jogada foi classificada como *{jogada_inicial}*. (Confiança: *{confianca_inicial:.2%}*)'
            await update.message.reply_text(resposta, parse_mode='Markdown')
            return

        # 2. PROCESSAMENTO: Se a imagem passou no teste, remove o fundo para ter mais precisão
        logger.info("Imagem parece válida. Removendo fundo...")
        # OTIMIZAÇÃO: Usa a sessão pré-carregada do rembg para mais velocidade
        imagem_sem_fundo = remove(imagem_original, session=context.bot_data['sessao_rembg'])

        # SALVAMENTO: Salva a imagem com fundo transparente na pasta de processados
        nome_base_arquivo = os.path.splitext(os.path.basename(file_path))[0]
        caminho_salvo = os.path.join(PASTA_IMAGENS_PROCESSADAS, f"{nome_base_arquivo}.png")
        imagem_sem_fundo.save(caminho_salvo)
        logger.info(f"Imagem sem fundo salva em: {caminho_salvo}")

        # Prepara a imagem para a classificação final (colando sobre um fundo branco)
        imagem_para_modelo = Image.new("RGB", imagem_sem_fundo.size, (255, 255, 255))
        imagem_para_modelo.paste(imagem_sem_fundo, mask=imagem_sem_fundo.split()[3])

        # 3. CLASSIFICAÇÃO FINAL: Roda a IA novamente, agora na imagem limpa
        logger.info("Realizando classificação final...")
        class_name, confidence_score = classifica_imagem(imagem_para_modelo, context)
        usuario_jogou = class_name[2:].strip()
        
        # JOGO: Lógica do Jokenpo
        opcoes_validas = [label[2:].strip() for label in context.bot_data['nomes_classes'] if "Nenhum" not in label]
        bot_jogou = random.choice(opcoes_validas)
    
        # Determina o resultado usando o dicionário de regras
        if usuario_jogou == bot_jogou:
            resultado = "Resultado: *Empate!* 😐"
        elif REGRAS_VITORIA[usuario_jogou] == bot_jogou:
            resultado = "Resultado: *Você venceu!* 🎉"
        else:
            resultado = "Resultado: *Você perdeu!* 😢"
        
        # Envia a resposta final para o usuário
        resposta = (
            f'Você jogou: *{usuario_jogou}*\n'
            f'O bot jogou: *{bot_jogou}*\n\n'
            f'{resultado}\n\n'
            f'(Confiança da sua jogada: {confidence_score:.2%})'
        )
        await update.message.reply_text(resposta, parse_mode='Markdown')

    except Exception as e:
        logger.error(f"Ocorreu um erro inesperado: {e}", exc_info=True)
        await update.message.reply_text("Desculpe, ocorreu um erro ao processar sua imagem.")


# --- FUNÇÃO PRINCIPAL ---
def main():
    """Função que configura e inicia o bot."""
    if not TOKEN:
        logger.critical("ERRO: O token do bot não foi fornecido na linha de comando.")
        sys.exit(1)

    # Cria a aplicação do bot
    application = Application.builder().token(TOKEN).build()
    
    # CARREGAMENTO DOS MODELOS: Isso é feito uma única vez quando o bot inicia
    try:
        logger.info("Carregando modelos de IA...")
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
        
        # Carrega o modelo Keras para classificação
        application.bot_data['modelo_keras'] = load_model(ARQUIVO_MODELO, compile=False)
        # Carrega as labels (Pedra, Papel, etc.)
        with open(ARQUIVO_LABELS, 'r', encoding='utf-8') as f:
            application.bot_data['nomes_classes'] = f.readlines()
        # OTIMIZAÇÃO: Cria e armazena a sessão do rembg com o modelo rápido
        application.bot_data['sessao_rembg'] = new_session(model_name=MODELO_REMBG)
        
        logger.info("Modelos carregados com sucesso.")
    except FileNotFoundError:
        logger.critical(f"ERRO: Arquivo de modelo '{ARQUIVO_MODELO}' ou de labels '{ARQUIVO_LABELS}' não encontrado.")
        sys.exit(1)

    # REGISTRO DOS HANDLERS: Associa comandos (/start) e tipos de mensagem (PHOTO) a funções
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.PHOTO, processa_imagem))

    # Inicia o bot
    logger.info("Bot configurado e pronto para receber mensagens.")
    application.run_polling()


if __name__ == '__main__':
    main()