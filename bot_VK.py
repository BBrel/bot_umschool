import requests
import telebot
from telebot import types
import os
import json

# bot token
bot_token = telebot.TeleBot('')

# users base and admins list
admins = [581843384]
users_base = {}

# buttons
yes_no_buttons = types.InlineKeyboardMarkup()
button_yes = types.InlineKeyboardButton("Да", callback_data='yes')
button_no = types.InlineKeyboardButton("Нет", callback_data='no')
yes_no_buttons.add(button_yes, button_no)

function_buttons = types.InlineKeyboardMarkup()
button_friends = types.InlineKeyboardButton("Получить друзей", callback_data='friends')
button_community = types.InlineKeyboardButton("Участники бесед", callback_data='community')
function_buttons.add(button_friends, button_community)

reg_buttons = types.InlineKeyboardMarkup()
button1 = types.InlineKeyboardButton("Регистрация!", callback_data='registration')
reg_buttons.add(button1)

url_address_numbers = types.InlineKeyboardMarkup()
button_url = types.InlineKeyboardButton("Инструкция",
                                        url='https://docs.google.com/document/d/1qdqsaRUsMwpPrcEjiucdTIWzlrnKmuyoYwNBjlvbEYM/edit?usp=sharing')
url_address_numbers.add(button_url)

url_address_token = types.InlineKeyboardMarkup()
button_url = types.InlineKeyboardButton("Инструкция",
                                        url='https://docs.google.com/document/d/1lnDe8vB5upqib-G0eVRunXSNu1TopMlfMjTKtVyAkm8/edit?usp=sharing')
url_address_token.add(button_url)


def check_token(token):
    if token[:5] != 'vk1.a':
        return False
    if "&expires_in" in token:
        return False
    if "&" in token:
        return False
    else:
        return True


try:
    @bot_token.message_handler(commands=['start'])
    def start(message):
        bot_token.send_message(message.chat.id, "Привет ✌\n\nЭтот бот предназначен для того, чтобы ты мог несколько "
                                                "облегчить себе работу и узнать список всех пользователей, "
                                                "которые находятся у тебя в друзьях или состоят в твоей беседе-комьюнити "
                                                "в ВКонтакте!\n\nДля начала работы тебе необходимо пройти регистрацию, "
                                                "нажимай кнопку ниже и следуй дальнейшим указаниям)",
                               reply_markup=reg_buttons)


    @bot_token.callback_query_handler(func=lambda callback: callback.data == 'registration')
    def registration_token(call):
        users_base[call.message.chat.id] = []
        msg = bot_token.send_message(call.message.chat.id,
                                     'Ну, приступим! 💫\n\nСейчас тебе необходимо отправить мне токен твоей странички '
                                     'ВК\n\n🔴 <b>Обязательно прочитай инструкцию! 👇</b>',
                                     reply_markup=url_address_token, parse_mode='html')

        bot_token.register_next_step_handler(msg, registration_numbers)


    def registration_numbers(message):
        if check_token(message.text):
            users_base[message.chat.id].append(message.text)
            msg = bot_token.send_message(message.chat.id, '✅ Токен выглядит правильным и сохранен для дальнейшего '
                                                          'использования!\n\nТеперь отправь мне номера бесед через '
                                                          'запятую\n\n🔴 <b>Инструкция по определению номера беседы '
                                                          '👇</b>', reply_markup=url_address_numbers,
                                         parse_mode='html')
            bot_token.register_next_step_handler(msg, registration_check)
        else:
            bot_token.send_message(message.chat.id,
                                   '<b>Введен некорректный токен</b>\nПрочитай инструкцию и начни регистрироваться заново\n\n'
                                   'Для регистрации нажми на /start', reply_markup=url_address_token, parse_mode='html')


    def registration_check(message):
        users_base[message.chat.id].append(message.text.split(','))
        bot_token.send_message(message.chat.id,
                               "Проверь введенные беседы)\n\n" + get_chat_name(users_base[message.chat.id][1],
                                                                               message.chat.id) +
                               "\nВыбраны верные комьюнити?", reply_markup=yes_no_buttons)


    @bot_token.callback_query_handler(func=lambda callback: callback.data == 'yes')
    def registration_end(call):
        bot_token.send_message(call.message.chat.id, f'Ты успешно прошёл регистрацию! 🧡'
                                                     f'Введённые данные:\n\n'
                                                     f'Токен: {users_base[call.message.chat.id][0]}\n\n'
                                                     f'Номера бесед: {users_base[call.message.chat.id][1]}\n\n'
                                                     f'Если где-то была допущена ошибка, перезапусти бота командой /start\n\n'
                                                     f'Если появятся вопросы по работе с ботом - /help')

        bot_token.send_message(call.message.chat.id, f'Выбери нужную тебе команду', reply_markup=function_buttons)


    @bot_token.callback_query_handler(func=lambda callback: callback.data == 'no')
    def registration_false(call):
        bot_token.send_message(call.message.chat.id, 'Повтори регистрацию введя команду /start')


    def get_friends_vk_api(user_id):
        response = requests.get('https://api.vk.com/method/friends.get',
                                params={
                                    'access_token': users_base[user_id][0],
                                    'v': 5.131
                                })

        return response.json()['response']['items']


    def get_community_users_vk_api(user_id):
        result = []
        com_name = users_base[user_id][1]
        for number in com_name:
            response = requests.get('https://api.vk.com/method/messages.getChat',
                                    params={
                                        'access_token': users_base[user_id][0],
                                        'v': 5.131,
                                        'chat_id': str(number)
                                    })

            result.extend(response.json()['response']['users'])
        return result


    def get_chat_name(com_name, user_id):
        result = ''
        for number in com_name:
            response = requests.get('https://api.vk.com/method/messages.getChat',
                                    params={
                                        'access_token': users_base[user_id][0],
                                        'v': 5.131,
                                        'chat_id': str(number)
                                    })

            result += response.json()['response']['title'] + '\n'
        return result


    @bot_token.callback_query_handler(func=lambda callback: callback.data == 'community')
    def get_cummunity_users(call):
        bot_token.send_message(581843384, f"Привет ✌\n<b>@{call.message.chat.username}</b> использовал бота ",
                               parse_mode='html')

        bot_token.send_message(call.message.chat.id,
                               "Бот уже во всю готовит список твоих учеников, стоит только немного подождать ✨")
        try:
            result = get_community_users_vk_api(call.message.chat.id)

            with open(call.message.chat.username + '.txt', 'w+') as file:
                for i in result:
                    file.writelines('https://vk.com/id' + str(i) + '\n')

            with open(call.message.chat.username + '.txt', 'r') as file:
                bot_token.send_document(call.message.chat.id, file)
            os.remove(call.message.chat.username + '.txt')
            bot_token.send_message(call.message.chat.id,
                                   f"Список был получен! Сумма всех участников комьюнити: {len(result)}\n\n"
                                   f"Выбери действие:", reply_markup=function_buttons)

        except:
            bot_token.send_message(call.message.chat.id, "В боте произошла проблема. Повтори снова. /start")
            pass


    @bot_token.callback_query_handler(func=lambda callback: callback.data == 'friends')
    def get_friends_bot(call):
        bot_token.send_message(581843384, f"Привет ✌\n<b>@{call.message.chat.username}</b> использовал бота ",
                               parse_mode='html')

        bot_token.send_message(call.message.chat.id,
                               "Бот уже во всю готовит список твоих учеников, стоит только немного подождать ✨")

        try:
            result = get_friends_vk_api(call.message.chat.id)

            with open(call.message.chat.username + '.txt', 'w+') as file:
                for i in result:
                    file.writelines('https://vk.com/id' + str(i) + '\n')

            with open(call.message.chat.username + '.txt', 'r') as file:
                bot_token.send_document(call.message.chat.id, file)
            os.remove(call.message.chat.username + '.txt')

            bot_token.send_message(call.message.chat.id, f"Список был получен! Всего друзей: {len(result)}\n\n"
                                                         f"Выбери действие:", reply_markup=function_buttons)
        except:
            bot_token.send_message(call.message.chat.id, "В боте произошла проблема. Повтори снова. /start")
            pass


    @bot_token.message_handler(commands=['help'])
    def help(message):
        bot_token.send_message(message.chat.id, f'<b>Раздел помощи: </b>\n\n'
                                                f'<b>/help</b> - список всех команд бота\n'
                                                f'<b>/info</b> - получение информации, хранящейся в боте\n'
                                                f'<b>/func</b> - возможные функции бота\n'
                                                f'<b>/start</b> - регистрация в боте с самого начала\n\n'
                                                f'<b>/help_me</b> - при возникновении технических вопросов можешь '
                                                f'написать запрос формата: /help_me *Вопрос* ', parse_mode='html')


    @bot_token.message_handler(commands=['help_me'])
    def help_me(message):
        bot_token.send_message(581843384,
                               'Запрос от @' + message.chat.username + ' ' + str(message.chat.id) + '\n' + message.text[message.text.find(' '):])
        bot_token.send_message(message.chat.id, f'Твой запрос был отправлен!')


    @bot_token.message_handler(commands=['info'])
    def info(message):
        if message.chat.id in users_base:
            bot_token.send_message(message.chat.id, f'Информация в боте: 🧡\n\n'
                                                    f'Токен: {users_base[message.chat.id][0]}\n\n'
                                                    f'Номера бесед: {users_base[message.chat.id][1]}\n\n'
                                                    f'Если где-то была допущена ошибка, перезапусти бота командой /start')

            bot_token.send_message(message.chat.id, f'Выбери нужную тебе команду', reply_markup=function_buttons)
        else:
            bot_token.send_message(message.chat.id, f'Ты еще не зарегистрирован!', reply_markup=reg_buttons)


    @bot_token.message_handler(commands=['func'])
    def func(message):
        if message.chat.id in users_base:
            bot_token.send_message(message.chat.id, f'Выбери нужную тебе команду', reply_markup=function_buttons)
        else:
            bot_token.send_message(message.chat.id, f'Ты еще не зарегистрирован!', reply_markup=reg_buttons)
except:
    pass

# admin commands
@bot_token.message_handler(commands=['answer'])
def answer(message):
    if message.chat.id in admins or message.chat.username in admins:
        user_sent = message.text.split()[1]
        bot_token.send_message(user_sent, message.text[message.text.find(' '):])
        bot_token.send_message(message.chat.id, 'Ответ отправлен')
    else:
        bot_token.send_message(message.chat.id, 'You have no access')

@bot_token.message_handler(commands=['download'])
def download(message):
    if message.chat.id in admins or message.chat.username in admins:
        capitals_json = json.dumps(users_base)

        with open("users.json", "w") as my_file:
            my_file.write(capitals_json)

        with open("users.json", 'r') as file:
            bot_token.send_document(message.chat.id, file)
    else:
        bot_token.send_message(message.chat.id, 'You have no access')


@bot_token.message_handler(commands=['sent'])
def sent(message):
    if message.chat.id in admins or message.chat.username in admins:
        for user in users_base:
            bot_token.send_message(user, message.text[message.text.find(' '):])
        bot_token.send_message(message.chat.id, 'Рассылка была выполнена')
    else:
        bot_token.send_message(message.chat.id, 'You have no access')


@bot_token.message_handler(commands=['stat'])
def stat(message):
    if message.chat.id in admins or message.chat.username in admins:
        bot_token.send_message(message.chat.id, 'Статистика бота:'
                                          f'\n{len(users_base)} - количество зарегистрированных пользователей')
    else:
        bot_token.send_message(message.chat.id, 'You have no access')


@bot_token.message_handler(commands=['give_admin'])
def give_admin(message):
    if message.chat.id in admins or message.chat.username in admins:
        admins.append(message.text[message.text.find(' '):][1:])
        bot_token.send_message(message.chat.id, 'админка выдана')
    else:
        bot_token.send_message(message.chat.id, 'You have no access')


@bot_token.message_handler(commands=['help_admin'])
def help_admin(message):
    if message.chat.id in admins or message.chat.username in admins:
        bot_token.send_message(message.chat.id, 'Команды админки:\n\n'
                                                '/give_admin - дать админку пользователю\n'
                                                '/stat - статистика\n'
                                                '/sent - рассылка сообщений\n'
                                                '/download - скачивание пользователей\n'
                                                '/answer - ответ на запрос\n')
    else:
        bot_token.send_message(message.chat.id, 'You have no access')


bot_token.polling(none_stop=True)
