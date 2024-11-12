from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
import random

api = ""

bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

health_tips = [
    "Пейте больше воды каждый день.",
    "Регулярно занимайтесь физическими упражнениями.",
    "Старайтесь спать не менее 7-8 часов каждую ночь.",
    "Питайтесь разнообразно и включайте в рацион свежие фрукты и овощи.",
    "Регулярно делайте перерывы во время работы для отдыха глаз и тела."
]


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.add(types.KeyboardButton("Рассчитать"), types.KeyboardButton("Информация"))

inline_keyboard = types.InlineKeyboardMarkup()
inline_keyboard.add(
    types.InlineKeyboardButton("Рассчитать норму калорий", callback_data="calories"),
    types.InlineKeyboardButton("Формулы расчета", callback_data="formulas")
)


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.reply(
        "Привет! Я бот, помогающий твоему здоровью. Нажмите на 'Рассчитать' "
        "для запуска калькулятора калорий или 'Информация', чтобы узнать обо мне.",
        reply_markup=keyboard
    )


@dp.message_handler(lambda message: message.text == "Информация")
async def about_command(message: types.Message):
    about_text = (
        "Я бот, созданный, чтобы помогать вам заботиться о здоровье. \n"
        "Я могу давать советы, напоминать о важности отдыха и физической активности. "
        "Надеюсь быть полезным!"
    )
    await message.reply(about_text)


@dp.message_handler(lambda message: message.text == "Рассчитать")
async def main_menu(message: types.Message):
    await message.reply("Выберите опцию:", reply_markup=inline_keyboard)


@dp.callback_query_handler(lambda call: call.data == "formulas")
async def get_formulas(call: types.CallbackQuery):
    formula_text = (
        "Формула Миффлина-Сан Жеора для мужчин:\n"
        "Калории = 10 * вес + 6.25 * рост - 5 * возраст + 5\n\n"
        "Формула для женщин:\n"
        "Калории = 10 * вес + 6.25 * рост - 5 * возраст - 161"
    )
    await call.message.answer(formula_text)


@dp.callback_query_handler(lambda call: call.data == "calories")
async def set_age(call: types.CallbackQuery):
    await UserState.age.set()
    await call.message.answer("Введите свой возраст:")


@dp.message_handler(state=UserState.age)
async def set_growth(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.reply("Пожалуйста, введите возраст числом.")
        return
    await state.update_data(age=int(message.text))
    await UserState.growth.set()
    await message.answer("Введите свой рост (в сантиметрах):")


@dp.message_handler(state=UserState.growth)
async def set_weight(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.reply("Пожалуйста, введите рост числом.")
        return
    await state.update_data(growth=int(message.text))
    await UserState.weight.set()
    await message.answer("Введите свой вес (в килограммах):")


@dp.message_handler(state=UserState.weight)
async def send_calories(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.reply("Пожалуйста, введите вес числом.")
        return
    await state.update_data(weight=int(message.text))
    data = await state.get_data()
    age = data['age']
    growth = data['growth']
    weight = data['weight']

    calories = 10 * weight + 6.25 * growth - 5 * age + 5
    await message.answer(f"Ваша норма калорий: {calories:.2f} ккал в день.")
    await state.finish()


@dp.message_handler(commands=["help"])
async def help_command(message: types.Message):
    help_text = (
        "Я помогу тебе заботиться о здоровье!\n"
        "Доступные команды:\n"
        "/start - начать общение с ботом\n"
        "/help - получить список команд\n"
        "/tips - получить случайный совет по здоровью\n"
        "Рассчитать - начать расчет калорий\n"
        "Информация - узнать больше обо мне"
    )
    await message.reply(help_text)


@dp.message_handler(commands=["tips"])
async def tips_command(message: types.Message):
    tip = random.choice(health_tips)
    await message.reply(tip)


@dp.message_handler(content_types=types.ContentType.TEXT)
async def echo_message(message: types.Message):
    await message.reply(message.text)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
