import telebot

# TELEGRAM STUFF
API_KEY = '6970037214:AAHplF29QE9IrSxeGPaFAxVkAHxddpMIOLU'
bot = telebot.TeleBot(API_KEY)

@bot.message_handler(commands=['start'], content_types=['text'])
def start(message):
  bot.send_message(message.chat.id, "This is a test...")

bot.polling()