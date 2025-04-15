from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CommandHandler
from huggingface_hub import InferenceClient
import logging
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)


client = InferenceClient(model="HuggingFaceH4/zephyr-7b-beta")

def generate_response(prompt, chat_history=None):
    """Генерация ответа с улучшенным промтом на русском"""
    if chat_history is None:
        chat_history = []
    

    system_prompt = """
        Ты - русскоязычный AI-ассистент. Обязательно:
        1. Отвечай предпочтительно на Русском языке(если не попросят иного)
        2. Сохраняй дружелюбный и вежливый тон
        3. Если вопрос не на русском - вежливо попроси перефразировать
        4. Не выдумывай факты, говори честно 'я не знаю' при необходимости
        """.format(date=datetime.now().strftime("%d.%m.%Y")).strip()
    

    messages = [
        {"role": "system", "content": system_prompt},
        *chat_history,
        {"role": "user", "content": prompt}
    ]
    
  
    formatted_prompt = ""
    for msg in messages:
        if msg["role"] == "system":
            formatted_prompt += f"<|system|>\n{msg['content']}</s>\n"
        elif msg["role"] == "user":
            formatted_prompt += f"<|user|>\n{msg['content']}</s>\n"
    formatted_prompt += "<|assistant|>\n"
    
    try:
        response = client.text_generation(
            formatted_prompt,
            max_new_tokens=200,
            do_sample=True,
            temperature=0.7,
            top_k=50,
            repetition_penalty=1.2
        )
        # Очистка ответа
        return response.split("<|assistant|>")[-1].strip()
    except Exception as e:
        logging.error(f"Ошибка HF API: {e}")
        return "Извините, произошла ошибка при обработке запроса"

async def start(update: Update, context):
    """Обработчик команды /start"""
    welcome_text = (
        "Привет! Я ваш русскоязычный ассистент на базе Zephyr-7B.\n"
        "Задайте мне любой вопрос на русском языке."
    )
    await update.message.reply_text(welcome_text)

async def handle_message(update: Update, context):
    """Обработка текстовых сообщений"""
    try:
        user_input = update.message.text
        user_id = update.message.from_user.id
        logging.info(f"User {user_id}: {user_input}")
        

        response = generate_response(user_input)
        
        await update.message.reply_text(response)
    except Exception as e:
        logging.error(f"Ошибка: {e}")
        await update.message.reply_text("Произошла ошибка при обработке сообщения")

def main():
    """Основная функция запуска бота"""
    TOKEN = os.getenv("TELEGRAM_TOKEN")#взят локальный env. нужно наменить
    if not TOKEN:
        logging.error("Не найден TELEGRAM_TOKEN в переменных окружения!")
        return
    
    app = Application.builder().token(TOKEN).build()
    
    # Регистрация обработчиков
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logging.info("Бот запущен и ожидает сообщений...")
    app.run_polling()

if __name__ == "__main__":
    main()