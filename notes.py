import asyncio
import sqlite3
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

# Токен бота (замени на свой)
API_TOKEN = "YOUR_BOT_TOKEN"

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Инициализация базы данных
def init_db():
    conn = sqlite3.connect("notes.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS notes (
        user_id INTEGER,
        note_text TEXT,
        note_id INTEGER PRIMARY KEY AUTOINCREMENT
    )''')
    conn.commit()
    conn.close()

# Вызываем инициализацию базы данных
init_db()


@dp.message(CommandStart())
async def command_start(message: Message):
    await message.answer("Привет! Я - твой бот для создания заметок. Вот мои команды:\n /create - Создать заметку \n /notes - Список заметок \n /delete - Удалить заметку") 


# Обработчик команды /add_note
@dp.message(Command("create"))
async def add_note(message: Message):
    user_id = message.from_user.id
    note_text = message.text.replace("/add_note ", "").strip()
    if not note_text:
        await message.answer("Пожалуйста, введи текст заметки после команды /add_note!")
        return
    conn = sqlite3.connect("notes.db")
    c = conn.cursor()
    c.execute("INSERT INTO notes (user_id, note_text) VALUES (?, ?)", (user_id, note_text))
    conn.commit()
    note_id = c.lastrowid
    conn.close()
    await message.answer(f"Заметка добавлена с ID {note_id}!")

# Обработчик команды /my_notes
@dp.message(Command("notes"))
async def show_notes(message: Message):
    user_id = message.from_user.id
    conn = sqlite3.connect("notes.db")
    c = conn.cursor()
    c.execute("SELECT note_id, note_text FROM notes WHERE user_id = ?", (user_id,))
    notes = c.fetchall()
    conn.close()
    if not notes:
        await message.answer("У тебя нет заметок!")
        return
    response = "Твои заметки:\n"
    for note_id, note_text in notes:
        response += f"ID {note_id}: {note_text}\n"
    await message.answer(response)

# Обработчик команды /delete_note
@dp.message(Command("delete"))
async def delete_note(message: Message):
    try:
        note_id = int(message.text.replace("/delete_note ", "").strip())
    except ValueError:
        await message.answer("Пожалуйста, укажи ID заметки числом после команды /delete_note!")
        return
    user_id = message.from_user.id
    conn = sqlite3.connect("notes.db")
    c = conn.cursor()
    c.execute("DELETE FROM notes WHERE note_id = ? AND user_id = ?", (note_id, user_id))
    if c.rowcount == 0:
        await message.answer("Заметка не найдена или не принадлежит тебе!")
    else:
        await message.answer(f"Заметка с ID {note_id} удалена!")
    conn.commit()
    conn.close()

# Основная функция для запуска бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
