import json
import os
import datetime
import logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from states import Stages
from data import universities
from userData import users_info
from pointsParse import send_info, update_userdata, get_userdata

logging.basicConfig(level=logging.INFO)

load_dotenv()
storage = MemoryStorage()

bot = Bot(token=os.getenv('TOKEN'), parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=storage)

universityNames = list(universities.keys())
admin_id = [int(os.getenv('ADMIN_ID'))]


async def on_startup(_):
    print('Бот запущен')


async def on_shutdown(_):
    print('Бот откинулся')


@dp.message_handler(commands='admin', state='*')
async def admin(message: types.Message, state: FSMContext):
    if message.from_user.id in admin_id:
        args = message.get_args()
        if args.split()[0] == 'say':
            users = await users_info.get_users()
            for user in users:
                try:
                    await bot.send_message(user[0], args[4:])
                except:
                    pass
            await bot.send_message(admin_id[0], 'Все сообщения были отправлены!')
        elif args.split()[0] == 'say_test':
            await bot.send_message(admin_id[0], args[9:])
        elif args.split()[0] == 'say_to':
            await bot.send_message(int(args.split()[1]), ' '.join(args.split()[2:]))


@dp.message_handler(commands='contacts', state='*')
async def contacts(message: types.Message, state: FSMContext):
    await bot.send_message(message.chat.id, '<b>--------------- ☎️ Контакты ☎️ ---------------</b>\n\nРазработчик:\n@dazesss\n\nТелеграм канал о текущем состоянии бота:\nhttps://t.me/urfupointsnews')


@dp.message_handler(commands='donate', state='*')
async def donate(message: types.Message, state: FSMContext):
    await bot.send_message(message.chat.id, '<b>--------------- 💰 Донат 💰 ---------------</b>\n\n<b>5469 1600 1991 3958</b> - сбер\n<b>5536 9140 6615 8761</b> - тинькофф') 


@dp.message_handler(commands='info', state='*')
async def info(message: types.Message, state: FSMContext):
    await bot.send_message(message.chat.id, '<b>--------------- ❕ Информация ❕ ---------------</b>\n\nС помощью данного бота можно посмотреть свою позицию в конкурсном списке, узнать количество бюджетных мест, а также число абитуриентов на конкретную специальность.\n\n❗️Не является официальным решением от УрФУ❗️\n\nПри возникновении каких-либо проблем, вопросов, а также если у вас есть идеи по доработке функционала, пишите сюда: @dazesss\n\n<i>P.S. если вы вдруг хотите поддержать данный проект, то реквизиты сможете найти по команде:</i>\n/donate\n\n😊😊😊')


@dp.message_handler(commands='start', state='*')
async def startuem(message: types.Message, state: FSMContext):
    await bot.send_message(message.chat.id, f'<b>✨Добро пожаловать в URFU Points!✨</b>\n<i>(не является официальным решением от УрФУ)</i>\n\nС его помощью можно посмотреть свою позицию в конкурсном списке, узнать количество бюджетных мест, а также число абитуриентов на конкретную специальность.\n\nПри возникновении каких-либо проблем, вопросов, а также если у вас есть идеи по доработке функционала, пишите сюда: @dazesss\n\n<i>P.S. если вы вдруг хотите поддержать данный проект, то реквизиты сможете найти по команде:</i>\n/donate\n\n😊😊😊')
    await bot.send_message(message.chat.id, 'Телеграм канал о текущем состоянии бота:\nhttps://t.me/urfupointsnews')

    keyboard = create_buttons(['1️⃣ Номер', '2️⃣ Баллы'], 2)

    stage, mess = chose_way()

    await stage.set()
    await update_userdata(message.from_user, state)
    await bot.send_message(message.chat.id, mess, reply_markup=keyboard)


@dp.message_handler(state=Stages.choice)
async def start(message: types.Message, state: FSMContext):
    if message.text.lower() == '1️⃣ номер' or message.text == '1':
        keyboard = create_button('Назад')

        await state.update_data(choseNumber=True)
        await Stages.number.set()
        await update_userdata(message.from_user, state)
        await bot.send_message(message.chat.id, 'Введи свой регистрационный номер', reply_markup=keyboard)
    elif message.text.lower() == '2️⃣ баллы' or message.text == '2':
        keyboard = create_button('Назад')

        await state.update_data(choseNumber=False)
        await Stages.points.set()
        await update_userdata(message.from_user, state)
        await bot.send_message(message.chat.id, 'Введи свою сумму баллов ЕГЭ', reply_markup=keyboard)


@dp.message_handler(state=Stages.number)
async def get_number(message: types.Message, state: FSMContext):
    if message.text.lower() == 'назад':
        keyboard = create_buttons(['1️⃣ Номер', '2️⃣ Баллы'], 2)

        stage, mess = chose_way()

        await stage.set()
        await update_userdata(message.from_user, state)
        await bot.send_message(message.chat.id, mess, reply_markup=keyboard)
    else:
        await state.update_data(user_data=message.text)

        keyboard = create_list(universityNames)

        await Stages.university.set()
        await update_userdata(message.from_user, state)
        await bot.send_message(message.chat.id, 'Выбери институт, который тебя интересует', reply_markup=keyboard)


@dp.message_handler(state=Stages.points)
async def get_points(message: types.Message, state: FSMContext):
    if message.text.lower() == 'назад':
        keyboard = create_buttons(['1️⃣ Номер', '2️⃣ Баллы'], 2)

        stage, mess = chose_way()

        await stage.set()
        await update_userdata(message.from_user, state)
        await bot.send_message(message.chat.id, mess, reply_markup=keyboard)
    else:
        try:
            await state.update_data(user_data=int(message.text))

            keyboard = create_list(universityNames)

            await Stages.university.set()
            await update_userdata(message.from_user, state)
            await bot.send_message(message.chat.id, 'Выбери институт, который тебя интересует', reply_markup=keyboard)
        except:
            pass


@dp.message_handler(state=Stages.university)
async def get_university(message: types.Message, state: FSMContext):
    if message.text.lower() == 'назад':
        data = await state.get_data()
        if data.get('choseNumber'):
            keyboard = create_button('Назад')

            await Stages.number.set()
            await update_userdata(message.from_user, state)
            await bot.send_message(message.chat.id, 'Введи свой регистрационный номер', reply_markup=keyboard)
        else:
            keyboard = create_button('Назад')

            await Stages.points.set()
            await update_userdata(message.from_user, state)
            await bot.send_message(message.chat.id, 'Введи свою сумму баллов ЕГЭ', reply_markup=keyboard)     
    elif message.text in universityNames:
        directions = universities[message.text]['directions']
        keyboard = create_list(directions)

        await state.update_data(university=message.text)
        await Stages.direction.set()
        await update_userdata(message.from_user, state)
        await bot.send_message(message.chat.id, 'Выбери направление обучения', reply_markup=keyboard)


@dp.message_handler(state=Stages.direction)
async def get_direction(message: types.Message, state: FSMContext):
    if message.text.lower() == 'назад':
        keyboard = create_list(universityNames)

        await Stages.university.set()
        await update_userdata(message.from_user, state)
        await bot.send_message(message.chat.id, 'Выбери институт, который тебя интересует', reply_markup=keyboard)
    else:
        data = await state.get_data()
        university = data.get('university')
        if message.text in universities[university]['directions']:
            loading = await bot.send_message(message.chat.id, 'Обработка данных...')

            await state.update_data(direction=message.text)
            await Stages.retry.set()
            
            direct = message.text

            keyboard = create_buttons(['Назад', 'Начать заново', 'Обновить информацию'], 2)  

            ident = universities[university]['ident']
            userData = data.get('user_data')
            choseNumber = data.get('choseNumber')

            info = send_info(ident, userData, direct, choseNumber)

            await update_userdata(message.from_user, state)

            if message.from_user.username is not None:
                print(message.from_user.id, message.from_user.username, f'({str(info["position"])}/{str(info["budgetPlaces"])})', direct, '|' + str(userData) + '|', datetime.datetime.now().strftime(f"%d.%m %H:%M"))
            else:
                print(message.from_user.id, message.from_user.first_name, f'({str(info["position"])}/{str(info["budgetPlaces"])})', direct, '|' + str(userData) + '|', datetime.datetime.now().strftime(f"%d.%m %H:%M"))


            if info['potential']:
                mess = f'\n\n<b>(потенциальная позиция в финальном рейтинге на данный момент: {info["potentialPosition"]})</b>\n\n<i>P.S. потенциальная позиция высчитывается лишь примерно, и показывает худший вариант расположения в списке (среди людей с таким же количеством баллов вы будете последним)</i>'
            else:
                mess = ''


            await loading.delete()
            await bot.send_message(message.chat.id, f'<b>{direct}</b>\n\nБюджетные места:  <b>{info["budgetPlaces"]}</b>\nКоличество абитуриентов:  <b>{info["abiturients"]}</b>\nТвоё место в списке:  <b>{info["position"]}</b>' + mess, reply_markup=keyboard)


@dp.message_handler(state=Stages.retry)
async def retry(message: types.Message, state: FSMContext):
    if message.text.lower() == 'начать заново':
        keyboard = create_buttons(['1️⃣ Номер', '2️⃣ Баллы'], 2)

        stage, mess = chose_way()

        await stage.set()
        await update_userdata(message.from_user, state)
        await bot.send_message(message.chat.id, mess, reply_markup=keyboard)
    elif message.text.lower() == 'назад':
        data = await state.get_data()
        directions = universities[data.get('university')]['directions']
        keyboard = create_list(directions)

        await Stages.direction.set()
        await update_userdata(message.from_user, state)
        await bot.send_message(message.chat.id, 'Выбери направление обучения', reply_markup=keyboard)
    elif message.text.lower() == 'обновить информацию':
        loading = await bot.send_message(message.chat.id, 'Обработка данных...')

        data = await state.get_data()
        university = data.get("university")
        direct = data.get('direction')

        keyboard = create_buttons(['Назад', 'Начать заново', 'Обновить информацию'], 2)  

        ident = universities[university]['ident']
        userData = data.get('user_data')
        choseNumber = data.get('choseNumber')

        info = send_info(ident, userData, direct, choseNumber)

        await update_userdata(message.from_user, state)

        if message.from_user.username is not None:
            print(message.from_user.id, message.from_user.username, f'({str(info["position"])}/{str(info["budgetPlaces"])})', direct, '|' + str(userData) + '|', datetime.datetime.now().strftime(f"%d.%m %H:%M"))
        else:
            print(message.from_user.id, message.from_user.first_name, f'({str(info["position"])}/{str(info["budgetPlaces"])})', direct, '|' + str(userData) + '|', datetime.datetime.now().strftime(f"%d.%m %H:%M"))


        if info['potential']:
            mess = f'\n\n<b>(потенциальная позиция в финальном рейтинге на данный момент: {info["potentialPosition"]})</b>\n\n<i>P.S. потенциальная позиция высчитывается лишь примерно, и показывает худший вариант расположения в списке (среди людей с таким же количеством баллов вы будете последним)</i>'
        else:
            mess = ''


        await loading.delete()
        await bot.send_message(message.chat.id, f'<b>{direct}</b>\n\nБюджетные места:  <b>{info["budgetPlaces"]}</b>\nКоличество абитуриентов:  <b>{info["abiturients"]}</b>\nТвоё место в списке:  <b>{info["position"]}</b>' + mess, reply_markup=keyboard)


@dp.message_handler()
async def calm(message: types.Message, state: FSMContext):
    inf = await get_userdata(message.from_user)
    state_name = inf[0]
    data = json.loads(inf[1])
    await restore_data(message, state, state_name, data)
        

async def restore_data(message, state, state_name, data):
    match state_name:
        case 'choice':
            await Stages.choice.set()
            await start(message, state)
        case 'number':
            await state.set_data(data)
            await Stages.number.set()
            await get_number(message, state)
        case 'points':
            await state.set_data(data)
            await Stages.points.set()
            await get_points(message, state)
        case 'university':
            await state.set_data(data)
            await Stages.university.set()
            await get_university(message, state)
        case 'direction':
            await state.set_data(data)
            await Stages.direction.set()
            await get_direction(message, state)
        case 'retry':
            await state.set_data(data)
            await Stages.retry.set()
            await retry(message, state)
        case _:
            await startuem(message, state)


def chose_way():
    return Stages.choice, f'<b>Ты можешь:</b>\n\n1️⃣  Узнать свою точную позицию при помощи регистрационного номера, который можно посмотреть в личном кабинете абитуриента УрФУ\n\n2️⃣  Узнать приблизительную позицию по сумме баллов ЕГЭ <b><i>(при получении информации на основе баллов отображается худший возможный вариант расположения в списке)</i></b>'


def create_button(text):
    button = types.KeyboardButton(text)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    keyboard.add(button)

    return keyboard


def create_buttons(btns, width):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=width)
    keyboard.add(*btns)

    return keyboard


def create_list(button_list):
    backButton = types.KeyboardButton('Назад')
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    keyboard.add(backButton).add(*button_list)

    return keyboard
    

if __name__ == '__main__':
    try:
        executor.start_polling(dp, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown)
    except:
        print('бот откинулся')