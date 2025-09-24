"""
    IMPORTAÇÃO DAS BIBLIOTECAS
"""
from PIL import Image
import os
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import sys
import numpy as np
from tensorflow.keras.models import load_model


"""
    CONFIGURAÇÃO DO BOT
"""
# Lê o token como parâmetro
if len(sys.argv) < 2:
    print("Erro: Forneça o token do seu bot como um argumento na linha de comando.")
    print("Exemplo: python bot_telegram.py SEU_TOKEN_AQUI")
    sys.exit(1)

MEU_TOKEN = sys.argv[1]

# Pasta para imagens enviadas pelo usuário
pasta_imgs = './Telegram_Imagens_Recebidas/'

print('Carregando BOT usando o token ', MEU_TOKEN)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


"""
    CARREGAMENTO DO MODELO DE IA
"""
print("Carregando modelo do Teachable Machine...")
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
model = load_model('keras_model.h5', compile=False)
class_names = open('labels.txt', 'r', encoding='utf-8').readlines()
print("Modelo carregado com sucesso.")


"""
    FUNÇÕES DE RESPOSTA (HANDLERS)
"""
async def start(update, context):
    await update.message.reply_text('Olá! Me envie uma imagem da sua mão fazendo uma das combinações do jokenpo e eu vou tentar classificá-la.')

async def help_command(update, context):
    await update.message.reply_text('Este bot classifica imagens usando um modelo de IA. Apenas me envie uma foto.')

async def processa_imagem(update, context):
    # Cria o diretório se ele não existir
    if not os.path.exists(pasta_imgs):
        os.makedirs(pasta_imgs)
        
    try:
        # Pega o objeto da foto
        photo_file = await update.message.photo[-1].get_file()
        
        # Baixa a imagem para um caminho específico
        file_path = os.path.join(pasta_imgs, f"{photo_file.file_id}.jpg")
        await photo_file.download_to_drive(file_path)
        print('Processando arquivo ', file_path)

        # Abre a imagem
        imagem_pil = Image.open(file_path).convert('RGB')

        # --- PREPARAÇÃO DA IMAGEM PARA O MODELO ---
        data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
        size = (224, 224)
        image_resized = imagem_pil.resize(size)
        image_array = np.asarray(image_resized)
        normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1
        data[0] = normalized_image_array

        # --- CLASSIFICAÇÃO DA IMAGEM ---
        prediction = model.predict(data)
        index = np.argmax(prediction)
        class_name = class_names[index]
        confidence_score = prediction[0][index]

        # --- ENVIO DA RESPOSTA ---
        classe_limpa = class_name[2:].strip()
        resposta = (
            f'Classificação: *{classe_limpa}*\n'
            f'Confiança: *{confidence_score:.2%}*'
        )
        await update.message.reply_text(resposta, parse_mode='Markdown')

    except Exception as e:
        logger.error(f"Erro ao processar imagem: {e}")
        await update.message.reply_text("Ocorreu um erro ao classificar sua imagem. Tente novamente.")


"""
    FUNÇÃO PRINCIPAL
"""
def main():
    #   A inicialização do bot agora usa Application.builder()
    application = Application.builder().token(MEU_TOKEN).build()
    
    print("Bot configurado. Aguardando mensagens...")

    #   Adiciona os handlers diretamente no 'application'
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.PHOTO, processa_imagem))

    #   O bot é iniciado com run_polling()
    application.run_polling()


if __name__ == '__main__':
    print('Bot respondendo, use CRTL+C para parar')
    main()