from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

API_TOKEN = '7347340152:AAGPVAOjW_VnWFDWKxFZGKuE4tQ5YMiD8Zg'

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Обновленное меню команд
menu_commands = [
    ('/start', 'Начать взаимодействие с ботом'),
    ('/leave_review', 'Оставить отзыв'),
    ('/report_problem', 'Сообщить о проблеме')
]

# Создаем боковую кнопку меню
menu_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
for command, description in menu_commands:
    menu_keyboard.add(KeyboardButton(f"{command} - {description}"))

cancel_button = KeyboardButton('Отмена')
cancel_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(cancel_button)

confirm_button = KeyboardButton('Подтвердить')
cancel_button = KeyboardButton('Отмена')
confirm_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(confirm_button, cancel_button)

class ReviewState(StatesGroup):
    review = State()
    confirm_review = State()
    confirm_problem = State()

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    # Отправляем приветственное сообщение и список команд
    await message.reply(
        """Это бот позволяет отправлять отзывы и сообщать о возникших проблемах при использовании проекта lazylearn.academy.
\n*Доступные команды:*\n/start - Начать взаимодействие с ботом\n/leave_review - Оставить отзыв\n/report_problem - Сообщить о проблеме""",
        parse_mode="Markdown",
        reply_markup=menu_keyboard
    )

@dp.message_handler(commands=['leave_review'])
async def leave_review(message: types.Message):
    await ReviewState.review.set()
    await message.reply("Пожалуйста, оставьте свой отзыв:", reply_markup=cancel_keyboard)

@dp.message_handler(commands=['report_problem'])
async def report_problem(message: types.Message):
    await ReviewState.review.set()
    await message.reply("Пожалуйста, опишите возникшую проблему:", reply_markup=cancel_keyboard)

@dp.message_handler(state=ReviewState.review)
async def get_review(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['review'] = message.text
    if message.text.startswith('/leave_review'):
        await ReviewState.next()
        await message.reply("Вы хотите отправить следующий отзыв:", reply_markup=confirm_keyboard)
    else:
        await ReviewState.confirm_problem.set()
        await message.reply("Вы хотите отправить следующее описание проблемы:", reply_markup=confirm_keyboard)

@dp.message_handler(lambda message: message.text == 'Подтвердить', state=ReviewState.confirm_review)
async def confirm_review(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        review = data['review']
    print(review)  # выводим отзыв на экран
    await message.reply("Ваш отзыв был отправлен успешно!", reply_markup=menu_keyboard)
    await state.finish()

@dp.message_handler(lambda message: message.text == 'Подтвердить', state=ReviewState.confirm_problem)
async def confirm_problem(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        review = data['review']
    print(review)  # выводим описание проблемы на экран
    await message.reply("Ваше описание проблемы было отправлено успешно!", reply_markup=menu_keyboard)
    await state.finish()

@dp.message_handler(lambda message: message.text == 'Отмена', state='*')
async def cancel_action(message: types.Message, state: FSMContext):
    await message.reply("Действие отменено.", reply_markup=menu_keyboard)
    await state.finish()

@dp.message_handler()
async def echo(message: types.Message):
    await message.answer(message.text, reply_markup=menu_keyboard)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)