import sqlite3
from newsapi import NewsApiClient
import telebot

flag = False
keyboard = telebot.types.ReplyKeyboardMarkup(True)
keyboard.row('/site', '/help')

conn = sqlite3.connect('database.db', check_same_thread=False)
cursor = conn.cursor()

bot = telebot.TeleBot("1525707127:AAHRkcH0iBcgmBsPnh3IQsxViLO7Js9JaYY")
newsapi = NewsApiClient(api_key='ac1090254ef54229bac8a6a1a300b2a7')


def db_table_val(user_id: int, user_name: str, user_surname: str,
                 username: str):
    global flag
    flag = False
    cursor.execute(
        'INSERT INTO data (user_id, user_name, user_surname, username) '
        'VALUES (?, ?, ?, ?)',
        (user_id, user_name, user_surname, username))
    conn.commit()


@bot.message_handler(commands=['start'])
def start_message(message):
    global flag
    flag = False
    bot.send_message(message.chat.id, 'Приветик! 😁 Пришел узнать последние '
                                      'новости? Напиши мне любую тему'
                                      ')', reply_markup=keyboard)
    having_users = cursor.execute(f"SELECT user_id FROM data").fetchall()
    idd = False
    for i in having_users:
        if message.from_user.id == i[0]:
            idd = True
    if idd:
        pass
    else:
        us_id = message.from_user.id
        us_name = message.from_user.first_name
        us_sname = message.from_user.last_name
        username = message.from_user.username
        db_table_val(user_id=us_id, user_name=us_name,
                     user_surname=us_sname,
                     username=username)


@bot.message_handler(content_types=['sticker'])
def sticker(message):
    global flag
    flag = False
    bot.send_message(message.chat.id, 'А я не умею отправлять стикеры(',
                     reply_markup=keyboard)


@bot.message_handler(content_types=['voice'])
def voice(message):
    global flag
    flag = False
    bot.send_message(message.chat.id, 'Давай текстом, э',
                     reply_markup=keyboard)


@bot.message_handler(commands=['help'])
def help(message):
    global flag
    flag = False
    bot.send_message(message.chat.id, 'Напиши мне любое слово и я найду '
                                      'новость по этой теме. Более того, ты '
                                      'можешь использовать предложенные ниже '
                                      'кнопки!', reply_markup=keyboard)


@bot.message_handler(commands=['site'])
def site(message):
    global flag
    flag = False
    yesno = telebot.types.ReplyKeyboardMarkup(True)
    yesno.row('/Предложить_идею')
    bot.send_message(message.chat.id, 'Ссылка')
    bot.send_message(message.chat.id, 'Хочешь помочь развитию сайта, предложив'
                                      ' свою идею?', reply_markup=yesno)


@bot.message_handler(commands=['Предложить_идею'])
def yes(message):
    bot.send_message(message.chat.id, 'Отлично! Напиши свою идею')
    global flag
    flag = True


@bot.message_handler(content_types=['text'])
def contact(message):
    global flag
    print(message.text)
    if flag:
        user_id = message.from_user.id
        cursor.execute(
            'INSERT INTO contact (user_id, idea) '
            'VALUES (?, ?)', (user_id, message.text))
        conn.commit()
        bot.send_message(message.chat.id, 'Большое спасибо! Я передам '
                                          'информацию разработчикам!',
                         reply_markup=keyboard)
        flag = False
    else:
        try:
            top_headlines = newsapi.get_everything(q=f'{message.text}',
                                                   language='ru')
            title = top_headlines["articles"][0]["title"]
            description = top_headlines["articles"][0]["description"]
            url = top_headlines["articles"][0]["url"]
            time = top_headlines["articles"][0]["publishedAt"]
            bot.send_message(message.chat.id, time[0:10],
                             reply_markup=keyboard)
            bot.send_message(message.chat.id, title, reply_markup=keyboard)
            bot.send_message(message.chat.id, description,
                             reply_markup=keyboard)
            bot.send_message(message.chat.id, url, reply_markup=keyboard)
        except Exception:
            bot.send_message(message.chat.id, 'Я не понимаю',
                             reply_markup=keyboard)


bot.polling(none_stop=True)
