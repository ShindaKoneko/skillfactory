import requests
from config import TOKEN
from pytelegrambotapi import TeleBot

class APIException(Exception):
    pass

class CurrencyConverter:
    @staticmethod
    def get_price(base, quote, amount):
        api_url = f'https://api.exchangerate-api.com/v4/latest/{base}'
        response = requests.get(api_url)
        data = response.json()

        if 'error' in data:
            raise APIException(f'Ошибка при получении данных: {data["error"]}')

        if quote not in data['rates']:
            raise APIException(f'Неизвестная валюта: {quote}')

        rate = data['rates'][quote]
        result = round(amount * rate, 2)
        return result

bot = TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'help'])
def handle_start_help(message):
    instructions = "Привет! Я бот для конвертации валют. Для использования, отправьте сообщение в формате:\n\n" \
                    "<имя валюты, цену которой вы хотите узнать> <имя валюты, в которой надо узнать цену первой валюты> <количество первой валюты>"
    bot.send_message(message.chat.id, instructions)

@bot.message_handler(commands=['values'])
def handle_values(message):
    values_info = "Доступные валюты: евро (EUR), доллар (USD), рубль (RUB)"
    bot.send_message(message.chat.id, values_info)

@bot.message_handler(func=lambda message: True)
def handle_currency_conversion(message):
    try:
        input_data = message.text.split()
        if len(input_data) != 3:
            raise APIException("Некорректный ввод. Используйте команду /help для получения инструкций.")

        base, quote, amount = input_data
        result = CurrencyConverter.get_price(base, quote, float(amount))
        response = f'{amount} {base} = {result} {quote}'
        bot.send_message(message.chat.id, response)

    except APIException as e:
        bot.send_message(message.chat.id, f'Ошибка: {str(e)}')

if __name__ == "__main__":
    bot.polling(none_stop=True, interval=0)
