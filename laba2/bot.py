import datetime
import re

from aiogram import Bot, types, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage


bot = Bot(token='5873543232:AAEGfPaiuxVmejyK5hVoshvOfiwyO4hkJe0')
dp = Dispatcher(bot=bot, storage=MemoryStorage())

hello = """
Привет! я бот для записи на приём к врачу.
/help - список команд бота.
"""
helpp = """/appointment - запись на приём.
/list - список ваших записей.
/delete - удалить запись на приём
"""
info = """
Адрес больницы:
Время работы:
Нельзя записать
"""
doctors = """
Выберите врача:
Доктор Степанов, эндокринолог, кабинет 223
Доктор Иванов, кардиолог, кабинет 237
Доктор Петров, терапевт, кабинет 311
Доктор Кузнецов, гастроэнтеролог, кабинет 466
Доктор Зубарев, нефролог, кабинет 359
"""
appointments = []
name = ''
doctor = ''
time = ''
date = ''


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply(text=hello)


@dp.message_handler(commands=['help'])
async def start(message: types.Message):
    await message.reply(text=helpp)


@dp.message_handler(commands=['info'])
async def start(message: types.Message):
    await message.reply(text=info)


@dp.message_handler(commands=['delete'])
async def start(message: types.Message):
    await message.reply("Для продолжения напишите ваше ФИО:")

    await dp.current_state(user=message.from_user.id).set_state('date_appointment')


@dp.message_handler(commands=['appointment'])
async def start(message: types.Message):
    await message.reply("Для продолжения напишите ваше ФИО:")

    # Добавляем состояние пользователя "ждем имя"
    await dp.current_state(user=message.from_user.id).set_state('wait_name')


@dp.message_handler(commands=['list'])
async def list_appointments(message: types.Message):
    await message.reply("Для продолжения напишите ваше ФИО:")

    await dp.current_state(user=message.from_user.id).set_state('list_continue')


@dp.message_handler(state='list_continue')
async def list_appointments(message: types.Message, state):
    global name
    name = message.text
    text = "Записи:\n"
    try:
        with open(f"{name}.txt", 'r') as f:
            lines = f.readlines()
            for line in lines:
                text += str(line) + '\n'
                await message.reply(text)
    except IOError:
        await message.reply(text)

    await state.finish()


@dp.message_handler(state='date_appointment')
async def date_appointment(message: types.Message):
    global name
    name = message.text
    await message.reply("Введите дату приёма:")

    await dp.current_state(user=message.from_user.id).set_state('time_appointment')


@dp.message_handler(state='time_appointment')
async def time_appointment(message: types.Message):
    global date
    date = datetime.datetime.strptime(message.text, '%d.%m.%Y').date()

    await message.reply("Введите время приёма:")

    await dp.current_state(user=message.from_user.id).set_state('check_file')


@dp.message_handler(state='check_file')
async def check_file(message: types.Message, state):
    global name, time, date
    time = datetime.datetime.strptime(message.text, '%H:%M')
    stroka = f"время: {time.strftime('%H:%M')}, дата: {date.strftime('%d.%m.%Y')}"
    pattern = re.compile(re.escape(stroka))
    try:
        with open(f"{name}.txt", 'r') as f:
            lines = f.readlines()
        with open(f"{name}.txt", 'w') as f:
            for line in lines:
                result = pattern.search(line)
                if result is None:
                    f.write(line)
        await message.reply('Запись удалена')
    except IOError:
        await message.reply("У вас нет записей")
        await state.finish()

    await state.finish()


@dp.message_handler(state='wait_name')
async def process_name(message: types.Message):
    global name
    name = message.text
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(types.KeyboardButton('Доктор Степанов, эндокринолог, кабинет 223'))
    kb.add(types.KeyboardButton('Доктор Иванов, кардиолог, кабинет 237'))
    kb.add(types.KeyboardButton('Доктор Петров, терапевт, кабинет 311'))
    kb.add(types.KeyboardButton('Доктор Кузнецов, гастроэнтеролог, кабинет 466'))
    kb.add(types.KeyboardButton('Доктор Зубарев, нефролог, кабинет 359'))
    await message.reply(text=doctors, reply_markup=kb)

    # Добавляем состояние пользователя "ждем выбор врача"
    await dp.current_state(user=message.from_user.id).set_state('wait_doctor')


@dp.message_handler(state='wait_doctor')
async def process_doctor(message: types.Message):
    global doctor
    doctor = message.text
    await message.answer(f"Хорошо, вы выбрали врача {doctor}. На какую дату хотите записаться?")

    # Добавляем состояние пользователя "ждем дату приема"
    await dp.current_state(user=message.from_user.id).set_state('wait_date')


@dp.message_handler(state='wait_date')
async def process_date(message: types.Message):
    global date
    date = datetime.datetime.strptime(message.text, '%d.%m.%Y').date()
    await message.answer(f"Отлично, вы выбрали {date.strftime('%d.%m.%Y')}. На какое время?")

    # Добавляем состояние пользователя "ждем время приема"
    await dp.current_state(user=message.from_user.id).set_state('wait_time')


@dp.message_handler(state='wait_time')
async def process_time(message: types.Message, state):
    global name, time, doctor, date
    time = datetime.datetime.strptime(message.text, '%H:%M')
    appointment = f"время: {time.strftime('%H:%M')}, дата: {date.strftime('%d.%m.%Y')}, доктор: {doctor}"
    with open(f'{name}.txt', 'a+') as f:
        f.write(appointment + '\n')
    appointments.append(appointment)
    text = f"Вы успешно записались на приём. Запись: {appointment}"

    await message.reply(text)

    # Сбрасываем состояние пользователя
    await state.finish()


def run():
    executor.start_polling(dp, skip_updates=True)