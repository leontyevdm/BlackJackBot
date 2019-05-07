import telebot
import random
import sqlite3

bot_summary = 0
player_summary = 0
bot_cards = []
player_cards = []
bot_aces = 0
new_deck = []
winner = ''

conn = sqlite3.connect('blackjackdatabase.db', check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""CREATE TABLE distributions
                  (Winner text, Player_points integer, Bot_points integer)
               """)

def build_deck():
    deck = []
    for i in range(4):
        deck.append("двойка")
        deck.append("тройка")
        deck.append("четверка")
        deck.append("пятерка")
        deck.append("шестерка")
        deck.append("семерка")
        deck.append("восьмерка")
        deck.append("девятка")
        deck.append("десятка")
        deck.append("валет")
        deck.append("дама")
        deck.append("король")
        deck.append("туз")
    return deck


def get_int_from_card(string):
    if string == "двойка":
        return 2
    elif string == "тройка":
        return 3
    elif string == "четверка":
        return 4
    elif string == "пятерка":
        return 5
    elif string == "шестерка":
        return 6
    elif string == "семерка":
        return 7
    elif string == "восьмерка":
        return 8
    elif string == "девятка":
        return 9
    elif string == "десятка":
        return 10
    elif string == "валет":
        return 10
    elif string == "дама":
        return 10
    elif string == "король":
        return 10
    elif string == "туз":
        return 11


bot = telebot.TeleBot("865071127:AAH4SbS9G21EHbfHHBF6R-fYm2iNOByABZ4")


@bot.message_handler(commands=['start'])
def start_message(message):
    output_string = 'Готов к игре. Допустимые команды: /new - начать новую раздачу, /more - получить еще одну карту,' \
                    ' /stop - закончить набор карт'
    bot.send_message(message.chat.id, output_string)


@bot.message_handler(commands=['new'])
def start_new_round(message):
    global new_deck, bot_aces
    new_deck = build_deck()
    player_first = random.choice(new_deck)
    new_deck.remove(player_first)
    player_cards.append(player_first)
    player_second = random.choice(new_deck)
    new_deck.remove(player_second)
    player_cards.append(player_second)
    bot_first = random.choice(new_deck)
    new_deck.remove(bot_first)
    bot_cards.append(bot_first)
    if bot_first == 'туз':
        bot_aces += 1
    output_string = ('Ваши карты: ' + player_first + ', ' + player_second + '\n' +
                     'Карта бота: ' + bot_first)
    bot.send_message(message.chat.id, output_string)


@bot.message_handler(commands=['stop'])
def stop(message):
    player_aces = 0
    game_ended = False
    global player_summary, bot_summary, bot_aces, new_deck, bot_cards, player_cards, winner
    for i in player_cards:
        player_summary += get_int_from_card(i)
        if i == 'туз':
            player_aces += 1
    while player_summary > 21 and player_aces > 0:
        player_summary -= 10
        player_aces -= 1
    if player_summary > 21:
        bot.send_message(message.chat.id, 'У вас перебор. Вы проиграли')
    elif player_summary == 21:
        bot.send_message(message.chat.id, 'BlackJack. Вы выиграли')
    else:
        bot_summary = get_int_from_card(bot_cards[0])
        while bot_summary < 17:
            new_bot_card = random.choice(new_deck)
            new_deck.remove(new_bot_card)
            bot_cards.append(new_bot_card)
            output_string = 'Новая карта бота:' + new_bot_card
            bot.send_message(message.chat.id, output_string)
            if new_bot_card == 'туз':
                bot_aces += 1
            bot_summary += get_int_from_card(new_bot_card)
            while bot_summary > 21 and bot_aces > 0:
                bot_summary -= 10
                bot_aces -= 1
            if bot_summary > 21:
                bot.send_message(message.chat.id, 'У бота перебор. Вы выиграли')
                game_ended = True
        if not game_ended:
            output_string = 'у Вас ' + str(player_summary) + '.\n' + 'У бота ' + str(bot_summary) + '.\n'
            if bot_summary < player_summary:
                output_string += 'Вы выиграли.'
                winner = 'Игрок'
                bot.send_message(message.chat.id, output_string)
            elif bot_summary > player_summary:
                output_string += 'Вы проиграли.'
                winner = 'Бот'
                bot.send_message(message.chat.id, output_string)
            else:
                output_string += 'Ничья'
                winner = 'Ничья'
                bot.send_message(message.chat.id, output_string)
    parameters = [(winner, player_summary, bot_summary)]
    cursor.executemany("insert into distributions values (?, ?, ?);", parameters)
    conn.commit()
    new_deck = build_deck()
    bot_summary = 0
    player_summary = 0
    bot_cards = []
    player_cards = []
    bot_aces = 0


@bot.message_handler(commands=['more'])
def more(message):
    global new_deck, bot_summary, bot_cards, player_summary, player_cards, bot_aces, winner
    new_player_card = random.choice(new_deck)
    new_deck.remove(new_player_card)
    player_cards.append(new_player_card)
    bot.send_message(message.chat.id, new_player_card)
    summary = 0
    aces = 0
    for i in player_cards:
        summary += get_int_from_card(i)
        if i == 'туз':
            aces += 1
    while summary > 21 and aces > 0:
        summary -= 10
        aces -= 1
    if summary > 21:
        output_string = 'У Вас ' + str(summary) + '. Перебор.  Вы проиграли'
        bot.send_message(message.chat.id, output_string)
        new_deck = build_deck()
        bot_summary = 0
        player_summary = 0
        bot_cards = []
        player_cards = []
        bot_aces = 0
        parameters = [(winner, player_summary, bot_summary)]
        cursor.executemany("insert into distributions values (?, ?, ?);", parameters)
        conn.commit()
    elif summary == 21:
        output_string = 'У Вас ' + str(summary) + ' Вы выиграли'
        bot.send_message(message.chat.id, output_string)
        new_deck = build_deck()
        bot_summary = 0
        player_summary = 0
        bot_cards = []
        player_cards = []
        bot_aces = 0
        winner = 'Игрок'
        parameters = [(winner, player_summary, bot_summary)]
        cursor.executemany("insert into distributions values (?, ?, ?);", parameters)
        conn.commit()


bot.polling()
