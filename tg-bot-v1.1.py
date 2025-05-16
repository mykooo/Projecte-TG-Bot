
import telebot
import openai
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

TG_API = 'TG_TOKEN_1'
OPENAI_API = 'IA_TOKEN_1'
OPENAI_MODEL = "gpt-4o"

bot = telebot.TeleBot(TG_API)
client = openai.OpenAI(api_key=OPENAI_API)

user_languages = {}

buttons = {
    'en': ['🔝 Top 5 attractions', '🏨 Best areas to stay', '🍽 Cheap places to eat'],
    'es': ['🔝 Las 5 mejores atracciones', '🏨 Mejores zonas para alojarse', '🍽 Lugares baratos para comer']
}

def get_main_keyboard(lang='en'):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for text in buttons[lang]:
        markup.add(KeyboardButton(text))
    return markup

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("🇬🇧 English"), KeyboardButton("🇪🇸 Español"))

    bot.send_message(
        message.chat.id,
        "👋 Welcome! / ¡Bienvenido!\n\nChoose your preferred language:\nElige tu idioma preferido:",
        reply_markup=markup
    )

@bot.message_handler(func=lambda m: m.text in ["🇬🇧 English", "🇪🇸 Español"])
def set_language(message):
    lang = 'en' if "English" in message.text else 'es'
    user_languages[message.chat.id] = lang

    if lang == 'en':
        greeting = "✅ Language set to English.\nAsk me anything about Barcelona!"
    else:
        greeting = "✅ Idioma cambiado a Español.\n¡Pregúntame lo que quieras sobre Barcelona!"

    bot.send_message(message.chat.id, greeting, reply_markup=get_main_keyboard(lang))

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    lang = user_languages.get(chat_id, 'en')  

    if lang == 'en':
        system_prompt = "You are a friendly travel assistant helping tourists in Barcelona. Be informative and concise."
    else:
        system_prompt = "Eres un asistente de viajes amable que ayuda a turistas en Barcelona. Sé informativo y conciso."

    user_input = message.text.strip()

    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            temperature=0.7
        )

        reply = response.choices[0].message.content
        bot.send_message(chat_id, reply, reply_markup=get_main_keyboard(lang))

    except Exception as e:
        bot.send_message(chat_id, "❌ Error while contacting ChatGPT.")
        print("OpenAI error:", e)

print("🤖 Bot funciona correctamente..")

bot.polling(none_stop=True)
