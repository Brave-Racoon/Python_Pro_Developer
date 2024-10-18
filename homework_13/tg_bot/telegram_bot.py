import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext

# API endpoint
API_ENDPOINT = "http://localhost:8080/predict"

# Replace with your own valid Telegram bot token!
TELEGRAM_BOT_TOKEN = "TOKEN"


async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Привет! Отправь мне сообщение на русском и я проанализирую его токсичность!')


async def analyze_toxicity(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    response = requests.get(API_ENDPOINT, params={'text': text})

    if response.status_code == 200:
        data = response.json()
        sentiment_label = data['sentiment_label']
        sentiment_score = data['sentiment_score']

        reply_text = f"Sentiment Label: {sentiment_label}\nSentiment Score: {sentiment_score}"
    else:
        reply_text = "Уппс, что-то я не справился..."

    await update.message.reply_text(reply_text)


def main() -> None:
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, analyze_toxicity))

    application.run_polling()


if __name__ == '__main__':
    main()
