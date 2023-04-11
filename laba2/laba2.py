import datetime

from aiogram import Bot, types, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage


class Appointment:
    def __init__(self, patient, doctor, data, vremya):
        self.patient = patient
        self.doctor = doctor
        self.data = data
        self.vremya = vremya

    def __str__(self):
        return f" - время: {self.vremya}, дата: {self.data.strftime('%d/%m/%Y')}, доктор: {self.doctor}"


bot = Bot(token='5873543232:AAEGfPaiuxVmejyK5hVoshvOfiwyO4hkJe0')
dp = Dispatcher(bot=bot, storage=MemoryStorage())

hello = """
Привет! я бот для записи на приём к врачу.
/appointment - запись на приём.
/list - список ваших записей.
"""
doctors = """
Выберите врача:
Доктор Степанов, эндокринолог
Доктор Иванов, кардиолог
Доктор Петров, терапевт
Доктор Кузнецов, гастроэнтеролог
Доктор Зубарев, нефролог
"""
appointments = []
name = ''
doctor = ''
time = ''
date = ''


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply(text=hello)


@dp.message_handler(commands=['appointment'])
async def start(message: types.Message):
    await message.reply("Для продолжения напишите ваше ФИО:")

    # Добавляем состояние пользователя "ждем имя"
    await dp.current_state(user=message.from_user.id).set_state('wait_name')


@dp.message_handler(commands=['list'])
async def list_appointments(message: types.Message):
    global name
    if len(appointments) > 0:
        text = "Записи:\n"
        for appointment in appointments:
            text += str(appointment) + '\n'
    else:
        text = "Нет записей."
    await message.reply(text)


@dp.message_handler(state='wait_name')
async def process_name(message: types.Message):
    global name
    name = message.text
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(types.KeyboardButton('Доктор Степанов, эндокринолог'))
    kb.add(types.KeyboardButton('Доктор Иванов, кардиолог'))
    kb.add(types.KeyboardButton('Доктор Петров, терапевт'))
    kb.add(types.KeyboardButton('Доктор Кузнецов, гастроэнтеролог'))
    kb.add(types.KeyboardButton('Доктор Зубарев, нефролог'))
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
    time = message.text
    appointment = name + str(Appointment(name, doctor, date, time))
    appointments.append(appointment)
    text = f"Вы успешно записались на приём. Запись: {appointment}"

    await message.reply(text)

    # Сбрасываем состояние пользователя
    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)