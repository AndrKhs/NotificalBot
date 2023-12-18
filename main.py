import datetime
import sqlite3
import telebot
from telebot import types
import time

conn = sqlite3.connect('Inform.db', check_same_thread=False)

bot_token = "6449838676:AAEdfKmzDSGp-fP5t4w8BfI6_TJ7hItHzaU"

bot = telebot.TeleBot(bot_token)


@bot.message_handler(commands=['start'])
@bot.message_handler(content_types=['text', 'document', 'audio'])
def logic(message):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS users(
                userID TEXT PRIMARY KEY,
                messages TEXT,  
                conditions TEXT,
                nowEventID TEXT);''')
    conn.commit()
    cur.execute('''CREATE TABLE IF NOT EXISTS events(
                eventID INTEGER PRIMARY KEY AUTOINCREMENT,
                userID TEXT,
                event TEXT,
                description TEXT,
                date timestamp);''')
    conn.commit()

    userid = str(message.chat.id)
    command = "SELECT * FROM users WHERE userID == '" + str(userid) + "'"
    cur.execute(command)
    c = cur.fetchone()

    if c == None or (message.text == "/start" and str(c[0]) == userid):
        try:
            command = "INSERT INTO users VALUES ('" + str(userid) + "', '" + str(message.text) + "', 'start', NULL)"
            cur.execute(command)
            conn.commit()
        except:
            pass
        button1 = types.KeyboardButton("Создать событие")
        button2 = types.KeyboardButton("Ближайшие события")
        button3 = types.KeyboardButton("Удалить событие")
        markup.add(button1)
        markup.add(button2)
        markup.add(button3)
        get_text_messages(message, "Выберите действие", markup)

    elif message.text in ["Назад", "Готово"] and str(c[0]) == userid:
        command = "UPDATE users set messages ='/start', conditions = 'start' where userID =  " + str(userid) + ""
        cur.execute(command)
        conn.commit()
        button1 = types.KeyboardButton("Создать событие")
        button2 = types.KeyboardButton("Ближайшие события")
        button3 = types.KeyboardButton("Удалить событие")
        markup.add(button1)
        markup.add(button2)
        markup.add(button3)
        get_text_messages(message, "Выберите действие", markup)

    # Создание события

    elif message.text == "Создать событие" and str(c[0]) == userid:
        try:
            command = "UPDATE users set messages ='Create', conditions = 'СозCоб' where userID = " + str(userid) + ""
            cur.execute(command)
            conn.commit()
            buttonBack = types.KeyboardButton("Назад")
            # command = "SELECT * FROM events "
            # for i in cur.execute(command):
            #     markup.add(str(i[0]))
            # conn.commit()
            markup.add(buttonBack)
            get_text_messages(message, "Напишите: название события", markup)
        except:
            buttonBack = types.KeyboardButton("Назад")
            markup.add(buttonBack)
            get_text_messages(message, "Что то пошло не так, попробуйте снова и проверте веденные данные", markup)

    elif str(c[2]) == "СозCоб" and str(c[0]) == userid:
        try:
            command = "SELECT * FROM users where userID = " + str(userid) + ""
            cur.execute(command)
            conn.commit()
            command = 'INSERT INTO events(userID, event, description, date) VALUES( "' + str(userid) + '", "' + \
                      str(message.text) + '" , "-", "' + str(datetime.datetime.now()) + '")'
            cur.execute(command)

            conn.commit()
            command = "UPDATE users set conditions = 'НазСоб' where userID =  " + str(userid) + ""
            cur.execute(command)
            conn.commit()
            buttonBack = types.KeyboardButton("Назад")
            markup.add(buttonBack)
            get_text_messages(message, "Напишите: описание события", markup)
        except:
            buttonBack = types.KeyboardButton("Назад")
            markup.add(buttonBack)

    elif str(c[2]) == "НазСоб" and str(c[0]) == userid:
        try:
            command = "SELECT * FROM users where userID = " + str(userid) + ""
            cur.execute(command)
            conn.commit()
            command = "UPDATE users set conditions = 'ОпиСоб' where userID =  " + str(userid) + ""
            cur.execute(command)
            conn.commit()
            eventId = ""
            try:
                command = "SELECT * FROM events where userID = " + str(userid) + " ORDER BY eventID DESC LIMIT 1"
                eventId = str(cur.execute(command).fetchone()[0])  # SELECT * FROM table ORDER BY column DESC LIMIT 1;
            except:
                print('not pass')
                pass
            try:
                command = "UPDATE events set description = '" + str(message.text) + "' where eventID =  '" + eventId + \
                          "'"
                cur.execute(command)
            except:
                print('not pass2')
                pass
            cur.execute(command)
            conn.commit()
            buttonBack = types.KeyboardButton("Назад")
            markup.add(buttonBack)
            get_text_messages(message, "Напишите: дату события в формате (ДД.ММ.ГГГГ)", markup)
        except:
            buttonBack = types.KeyboardButton("Назад")
            markup.add(buttonBack)

    elif str(c[2]) == "ОпиСоб" and str(c[0]) == userid:
        try:
            command = "SELECT * FROM users where userID = " + str(userid) + ""
            cur.execute(command)
            conn.commit()
            user_date = message.text.split(".")
            cur_time = datetime.date.today()
            if len(user_date) == 3 \
                    and int(user_date[0]) <= 31 \
                    and int(user_date[1]) <= 12 \
                    and int(user_date[2]) >= int(datetime.date.today().strftime("%Y")) \
                    and (datetime.date(day=int(user_date[0]), month=int(user_date[1]),
                                       year=int(user_date[2])) >= cur_time):
                command = "UPDATE users set conditions = 'ДатСоб' where userID =  " + str(userid) + ""
                cur.execute(command)
                conn.commit()
                command = "SELECT * FROM events where userID = " + str(userid) + " ORDER BY eventID DESC LIMIT 1"
                event = cur.execute(command).fetchone()
                eventId = str(event[0])
                command = "UPDATE events set date = '" + str(message.text) + "' where eventID =  '" + eventId + \
                          "'"
                cur.execute(command)
                conn.commit()
                buttonBack = types.KeyboardButton("Готово")
                markup.add(buttonBack)
                msg = "Событие записано\nID события: " + str(event[0]) + "\nНазвание: " + event[2] + "\nОписание: " + \
                      event[3] + "\nДата: " + str(message.text)
                get_text_messages(message, msg, markup)
            else:
                command = "UPDATE users set conditions = 'ОпиСоб' where userID =  " + str(userid) + ""
                cur.execute(command)
                buttonBack = types.KeyboardButton("Назад")
                markup.add(buttonBack)
                msg = "Неверный формат даты, напишите заного"
                get_text_messages(message, msg, markup)

        except:
            print("sds")
            buttonBack = types.KeyboardButton("Назад")
            markup.add(buttonBack)

    # Ближайшее собыите

    elif message.text == "Ближайшие события" and str(c[0]) == userid:
        try:
            command = "UPDATE users set messages ='" + str(
                message.text) + "', conditions = 'БлиСоб' where userID = " + str(userid) + ""
            cur.execute(command)
            conn.commit()
            buttonBack = types.KeyboardButton("Назад")
            cur_time = datetime.date.today().strftime("%d.%m.%Y")
            time_b = (datetime.date.today() + datetime.timedelta(5)).strftime("%d.%m.%Y")
            command = "SELECT * FROM events WHERE date BETWEEN '" + cur_time + "' AND '" + time_b + "' AND userID=" + str(
                userid)
            for i in cur.execute(command):
                markup.add(str(i[2]) + ". Дата: " + str(i[4]) + " ID: " + str(i[0]))
            conn.commit()
            markup.add(buttonBack)
            get_text_messages(message, "Выберите событие", markup)
        except:
            buttonBack = types.KeyboardButton("Назад")
            markup.add(buttonBack)

    elif str(c[2]) == "БлиСоб" and str(c[0]) == userid:
        try:
            print("sasas")
            command = "UPDATE users set messages ='" + str(
                message.text) + "', conditions = 'ОсмСоб' where userID = " + str(userid) + ""
            cur.execute(command)
            conn.commit()
            eventID = message.text.split(" ID: ")[1]
            print(eventID)
            command = "SELECT * FROM events where eventID = " + str(eventID)
            event = cur.execute(command).fetchone()
            conn.commit()
            print(event[2])
            buttonBack = types.KeyboardButton("Готово")
            markup.add(buttonBack)
            msg = "Название: " + event[2] + "\nОписание: " + event[3] + "\nДата: " + event[4]
            get_text_messages(message, msg, markup)
        except:
            buttonBack = types.KeyboardButton("Назад")
            markup.add(buttonBack)

    # Удаление события

    elif message.text == "Удалить событие" and str(c[0]) == userid:
        try:
            command = "UPDATE users set messages ='" + str(message.text) \
                      + "', conditions = 'УдаСоб' where userID = " + str(userid) + ""
            cur.execute(command)
            conn.commit()
            buttonBack = types.KeyboardButton("Назад")
            command = "SELECT * FROM events WHERE userID=" + userid
            for i in cur.execute(command):
                markup.add(str(i[2]) + ". Дата: " + str(i[4]) + " ID: " + str(i[0]))
            conn.commit()
            markup.add(buttonBack)
            get_text_messages(message, "Выберите событие", markup)
        except:
            buttonBack = types.KeyboardButton("Назад")
            markup.add(buttonBack)

    elif str(c[2]) == "УдаСоб" and str(c[0]) == userid:
        try:
            command = "UPDATE users set messages ='" + str(message.text) \
                      + "', conditions = 'ОсмСоб' where userID = " + str(userid) + ""
            cur.execute(command)
            conn.commit()
            eventID = message.text.split(" ID: ")[1]
            command = "DELETE FROM events WHERE eventID=" + eventID
            cur.execute(command)
            conn.commit()
            buttonBack = types.KeyboardButton("Готово")
            markup.add(buttonBack)
            msg = "Сообщение удалено"
            get_text_messages(message, msg, markup)
        except:
            buttonBack = types.KeyboardButton("Назад")
            markup.add(buttonBack)


def get_text_messages(message, mes, markup):
    bot.send_message(message.chat.id, mes, reply_markup=markup)


if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True, interval=0)
        except Exception as e:
            time.sleep(3)
            print(e)
