import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

# Токен бота (замени на свой)
API_TOKEN = "YOUR_BOT_TOKEN"

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Определяем класс состояний для анкеты
class Form(StatesGroup):
    name = State()  # Состояние для имени
    age = State()   # Состояние для возраста
    city = State()  # Состояние для города

# Обработчик команды /start
@dp.message(CommandStart())
async def start_form(message: Message, state: FSMContext):
    await message.answer("Привет! Давай заполним анкету. Как тебя зовут?")
    await state.set_state(Form.name)  # Устанавливаем состояние для имени

# Обработчик команды /cancel
@dp.message(Command("cancel"))
async def cancel_form(message: Message, state: FSMContext):
    await state.clear()  # Очищаем состояние
    await message.answer("Анкета сброшена. Начнем заново? Напиши /start")

# Обработчик ввода имени
@dp.message(Form.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)  # Сохраняем имя
    await message.answer("Сколько тебе лет? (Введи число)")
    await state.set_state(Form.age)  # Переходим к следующему состоянию

# Обработчик ввода возраста
@dp.message(Form.age)
async def process_age(message: Message, state: FSMContext):
    if not message.text.isdigit():  # Проверяем, что введено число
        await message.answer("Пожалуйста, введи возраст числом!")
        return
    age = int(message.text)
    if age < 0 or age > 120:  # Простая валидация возраста
        await message.answer("Возраст должен быть от 0 до 120 лет!")
        return
    await state.update_data(age=age)  # Сохраняем возраст
    await message.answer("В каком городе ты живешь?")
    await state.set_state(Form.city)  # Переходим к следующему состоянию

# Обработчик ввода города
@dp.message(Form.city)
async def process_city(message: Message, state: FSMContext):
    await state.update_data(city=message.text)  # Сохраняем город
    data = await state.get_data()  # Получаем все данные
    await message.answer(
        f"Спасибо! Вот твоя анкета:\n"
        f"Имя: {data['name']}\n"
        f"Возраст: {data['age']}\n"
        f"Город: {data['city']}"
    )
    await state.clear()  # Сбрасываем состояние

# Основная функция для запуска бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
