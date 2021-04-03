import os

from flask import Flask, request

import telebot

import datetime
import sqlite3

TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)


@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, 'Hola, ' + message.from_user.first_name)

@bot.message_handler(commands=['polereset'])
def polereset(message):
    user = '<a href="tg://user?id='+ str(message.from_user.id)  +'">inline mention of a user</a>'
    db = sqlite3.connect("data.db")
    cursor = db.cursor()
    datos = cursor.execute("DELETE FROM poles")
    bot.reply_to(message, f'Pole reseteadas! {user}')

@bot.message_handler(commands=['polerank'])
def polereset(message):
    db = sqlite3.connect("data.db")
    cursor = db.cursor()
    datos = cursor.execute("SELECT * FROM poles")
    bot.reply_to(message, f"Pole reseteadas! {user}",parse_mode="Markdown")


@bot.message_handler(func=lambda message: True, content_types=['text'])
def echo_message(message):
    """Pole para AP"""
    weekno = datetime.datetime.today().weekday()
    now = datetime.datetime.now()
    hour = now.hour

    db = sqlite3.connect("data.db")
    cursor = db.cursor()

    #sacamos las fecha de consulta
    fecha_ant = "'" + str(now.year) + '-' + str(now.month) + '-' + str(now.day) + "'"
    fecha_act = datetime.datetime(now.year, now.month, (now.day+1))

    cid = message.chat.id 
    message_text = message.text 
    user_id = message.from_user.id 
    user_name = message.from_user.username or message.from_user.first_name
    mention = "["+str(user_name)+"](tg://user?id="+str(user_id)+")"

    # if weekno < 5 and now.hour>=5:
    if weekno < 7:
        if(message.text.lower()=="pole"):
            user = mention
            #Validamos que no se haya hecho la pole
            datos = cursor.execute("SELECT * FROM poles WHERE pole='pole' AND date >=  '" +str(now.year) + "-" + str(now.month).zfill(2) + "-" + str(now.day).zfill(2) + "'")
            if len(datos.fetchall())==0:
                registros = ('pole',user,3.5,now)
                datos = cursor.execute("INSERT INTO poles(pole,user,points,date) VALUES(?,?,?,?)",registros)
                db.commit()
                bot.reply_to(message,
                    f'Erda bien y tal, {user} ha hecho la pole',parse_mode="Markdown"
                )
        elif (message.text.lower()=="plata"):
            user = mention
            # Validamos que se haya hecho la pole
            datos = cursor.execute("SELECT * FROM poles WHERE pole='pole' AND date >=  '" +str(now.year) + "-" + str(now.month).zfill(2) + "-" + str(now.day).zfill(2) + "'")
            if len(datos.fetchall())>0:
                # Validamos que no se haya hecho una plata
                datos = cursor.execute("SELECT * FROM poles WHERE pole='plata' AND date >=  '" +str(now.year) + "-" + str(now.month).zfill(2) + "-" + str(now.day).zfill(2) + "'")
                if len(datos.fetchall())==0:
                    #Validamos que si este usuario ya hizo alguna position, no puede hacer plata
                    datos = cursor.execute("SELECT * FROM poles WHERE user='"+str(user)+"' AND date >=  '" +str(now.year) + "-" + str(now.month).zfill(2) + "-" + str(now.day).zfill(2) + "'")
                    if len(datos.fetchall())==0:
                        registros = ('plata',user,2,now)
                        datos = cursor.execute("INSERT INTO poles(pole,user,points,date) VALUES(?,?,?,?)",registros)
                        db.commit()
                        bot.reply_to(message,
                            f'muy bien, {user} ha hecho la plata',parse_mode="Markdown"
                        )
        elif (message.text.lower()=="bronce"):
            user = mention
            # Validamos que se haya hecho la plata
            datos = cursor.execute("SELECT * FROM poles WHERE pole='plata' AND date >=  '" +str(now.year) + "-" + str(now.month).zfill(2) + "-" + str(now.day).zfill(2) + "'")
            if len(datos.fetchall())>0:
                # Validamos que no se haya hecho una plata
                datos = cursor.execute("SELECT * FROM poles WHERE pole='bronce' AND date >=  '" +str(now.year) + "-" + str(now.month).zfill(2) + "-" + str(now.day).zfill(2) + "'")
                if len(datos.fetchall())==0:
                    #Validamos que si este usuario ya hizo alguna position, no puede hacer plata
                    datos = cursor.execute("SELECT * FROM poles WHERE user='"+str(user)+"' AND date >=  '" +str(now.year) + "-" + str(now.month).zfill(2) + "-" + str(now.day).zfill(2) + "'")
                    if len(datos.fetchall())==0:
                        registros = ('bronce',user,0.5,now)
                        datos = cursor.execute("INSERT INTO poles(pole,user,points,date) VALUES(?,?,?,?)",registros)
                        db.commit()
                        bot.reply_to(message,
                            f'Algo es algo, {user} ha conseguido el bronce',parse_mode="Markdown"
                        )
        elif (message.text.lower()=="fail"):
            user = mention
            registros = ('fail',user,0,now)
            datos = cursor.execute("INSERT INTO poles(pole,user,points,date) VALUES(?,?,?,?)",registros)
            db.commit()
            bot.reply_to(message,
                f'Al menos lo intento, {user} ha conseguido un Fail',parse_mode="Markdown"
            )
    elif (message.text.lower()=="poleprueba" or message.text.lower()=="plataprueba" or message.text.lower()=="bronceprueba" or message.text.lower()=="fail"):
        user = mention
        bot.reply_to(message,
            f'Deja de molestarme {user} que estas no son horas de estar haciendo {message.text.lower()}',parse_mode="Markdown"
        )


@server.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200


@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://pilaricaap.herokuapp.com/' + TOKEN)
    return "!", 200


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))