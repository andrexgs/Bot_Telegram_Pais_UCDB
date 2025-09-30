# Bot de Jokenpo para Telegram com IA

Este projeto é um bot para o Telegram que joga "Pedra, Papel e Tesoura" (Jokenpo) contra o usuário. O bot utiliza uma rede neural convolucional (criada com TensorFlow/Keras) para classificar uma imagem da mão do usuário e identificar a jogada.

Para aumentar a precisão da classificação, o bot primeiro remove o fundo da imagem enviada antes de passá-la para o modelo de IA.

---

### ✨ Funcionalidades

-   **Classificação de Imagens:** Reconhece as jogadas de "Pedra", "Papel" e "Tesoura" a partir de fotos.
-   **Lógica de Jogo Jokenpo:** Joga uma rodada contra o usuário e determina o vencedor.
-   **Remoção Automática de Fundo:** Utiliza a biblioteca `rembg` para isolar a mão na imagem, melhorando a acurácia do modelo.
-   **Pré-Classificação:** Realiza uma análise rápida na imagem original para descartar fotos que claramente não são jogadas válidas, economizando processamento.
-   **Interação Simples:** Responde aos comandos `/start`, `/help` e processa qualquer imagem enviada.

---

### 📂 Estrutura do Projeto

-   `bot_telegram.py`: Script original (v1). Uma versão mais simples do bot que classifica a imagem original sem remover o fundo, podendo resultar em menor acurácia.
-   `bot_telegramv2.py`: Script principal (v2) e recomendado. Contém a lógica mais avançada, incluindo um pré-processamento que remove o fundo da imagem antes da classificação, garantindo maior precisão.
-   `requirements.txt`: Arquivo que lista todas as dependências (bibliotecas) Python necessárias para o projeto. Facilita a instalação do ambiente com o comando *pip install -r requirements.txt.*
-   `keras_model.h5`: O modelo de Inteligência Artificial (rede neural) já treinado. É o "cérebro" responsável por analisar a imagem e identificar a jogada (pedra, papel ou tesoura).
-   `labels.txt`: Um arquivo de texto que contém os nomes das possíveis classificações que o modelo pode prever, em uma ordem correspondente à saída do modelo.
-   `Telegram_Imagens_Recebidas/`: Pasta onde as imagens originais enviadas pelos usuários via Telegram são salvas temporariamente para processamento.
-   `Imagens_Processadas_Sem_Fundo/`: Diretório usado pelo *bot_telegramv2.py* para armazenar as imagens após a remoção do fundo, prontas para serem analisadas pelo modelo de IA.

---

### 🚀 Instalação e Configuração

Siga os passos abaixo para configurar e executar o projeto.

**1. Clone o repositório:**
```bash
git clone [URL_DO_SEU_REPOSITORIO]
cd [NOME_DO_REPOSITORIO]
```

**2. Crie e ative um ambiente virtual (Recomendado)**

```bash
# Cria o ambiente
python -m venv venv

# Ativa o ambiente
# No Windows:
venv\Scripts\activate
# No macOS/Linux:
source venv/bin/activate
```

**3. Instale as dependências:**
```bash
    pip install -r requirements.txt
```

### ▶️ Como Executar o Bot

Este projeto depende de um arquivo keras_model.h5. Se você não possui este arquivo ou deseja treinar um modelo customizado com suas próprias imagens, siga os passos:

- 1. Acesse o banco de imagens: Um conjunto de imagens para treino está disponível no link abaixo. Você pode usar estas imagens ou adicionar as suas.
- https://drive.google.com/drive/folders/19WMO8Hl801PpnSzTPmAhLd5ZSxQxruP-?usp=sharing.

- 2. Use o Teachable Machine: Esta ferramenta online e gratuita do Google permite treinar um modelo de classificação de imagens de forma visual e intuitiva.
- Acesse o https://teachablemachine.withgoogle.com/train/image.
- Crie as classes (Pedra, Papel, Tesoura, etc.) e faça o upload das imagens de treino para cada uma.
- Após o treino, exporte o modelo no formato Tensorflow > Keras. Isso irá gerar os arquivos keras_model.h5 e labels.txt para você usar no projeto.


### ▶️ Como Executar o Bot

Para iniciar o bot, você precisa do token de acesso fornecido pelo Telegram.

- Obtenha seu Token: Fale com o @BotFather no Telegram para criar um novo bot e receber seu token de acesso.
- Execute o script: No seu terminal, navegue até a pasta do projeto e rode o script bot_telegramv2.py, passando o seu token como um argumento na linha de comando. Substitua SEU_TOKEN_AQUI pelo seu token real.

- Script original (v1). Uma versão mais simples do bot que classifica a imagem original sem remover o fundo, podendo resultar em menor acurácia.
```bash
    python bot_telegram.py SEU_TOKEN_AQUI
```
- Script principal (v2) e recomendado. Contém a lógica mais avançada, incluindo um pré-processamento que remove o fundo da imagem antes da classificação, garantindo maior precisão.
```bash
    python bot_telegramv2.py SEU_TOKEN_AQUI
```

- Pronto! O terminal exibirá os logs de inicialização. A partir desse momento, o bot estará online e pronto para receber imagens no Telegram. Para parar a execução, pressione CTRL+C no terminal.


### 🛠️ Tecnologias Utilizadas

- Python: Linguagem principal do projeto.

- TensorFlow / Keras: Para a construção e utilização do modelo de classificação de imagens.

- python-telegram-bot: Biblioteca para a integração com a API do Telegram.

- Pillow (PIL): Para manipulação e processamento de imagens.

- rembg: Para a funcionalidade de remoção de fundo das fotos.

- NumPy: Para operações numéricas e manipulação de arrays, essencial para o pré-processamento de imagens para o modelo.

### 👨‍💻 Autor

Este projeto foi desenvolvido com dedicação por André G. Silva.

- GitHub: github.com/andrexgs
- LinkedIn: linkedin.com/in/andregoncalvesdasilva
- Email: instagram.andre12@gmail.com