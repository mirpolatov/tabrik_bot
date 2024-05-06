import asyncio
import os

from datetime import datetime

import pytz
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils import executor
from pytz import timezone
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
# from apscheduler.schedulers.asyncio import AsyncIOScheduler

from button import main_rp, order_keyboart

API_TOKEN = "7045481924:AAG56pDeg9_gCOzoO-2CxT6KqnQgMsU0X9c"

bot = Bot(API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

storage = MemoryStorage()
dp.storage = storage
DATABASE_URL = 'sqlite:///video.db'

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class Video(Base):
    __tablename__ = 'video'

    id = Column(Integer, Sequence('video_id_seq'), primary_key=True)
    file_id = Column(String(255))
    file_path = Column(String(255))
    full_name = Column(String)
    data = Column(DateTime)


Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


class Forms(StatesGroup):
    video = State()
    full_name = State()
    date = State()


@dp.message_handler(commands=['start'])
async def start_order(message: types.Message):
    if message.from_user.id == 1327286056:
        await message.answer('hello', reply_markup=main_rp)


@dp.message_handler(lambda message: message.text == "Video qo'shish")
async def start_food_registration(message: types.Message):
    await message.answer("Iltimos,ovqat rasmini kiriting.")
    await Forms.video.set()


# Qismni qabul qilish handler
@dp.message_handler(state=Forms.video, content_types=types.ContentTypes.VIDEO)
async def process_video(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['file_id'] = message.video.file_id
        data['file_path'] = f'videos/{message.video.file_id}.mp4'
        data['user_id'] = message.from_user.id

    await Forms.next()
    await message.answer('Video qismi kiriting:')


# Qismni qabul qilish handler
@dp.message_handler(state=Forms.full_name)
async def process_qism(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['full_name'] = message.text

    await Forms.next()
    await message.answer('Video tafsilotlarini kiriting:')


@dp.message_handler(state=Forms.date)
async def process_description(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['date'] = message.text

        datetime_str = message.text
        # Convert the datetime string to a datetime object
        datetime_obj = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
        # Set the 'date' key to the datetime object
        data['date'] = datetime_obj

    # Fayl saqlash
    os.makedirs(os.path.dirname(data['file_path']), exist_ok=True)
    await bot.download_file_by_id(data['file_id'], data['file_path'])

    # StatesGroupni yakunlash
    await state.finish()

    await message.answer('Video qabul qilindi va ma\'lumotlar saqlandi.')


async def hamma_ovqatlar(message: types.Message):
    db = Session()
    food_items = db.query(Video).all()
    db.close()

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

    for food_item in food_items:
        button_text = f"Videolar: {food_item.full_name}"
        keyboard.add(types.KeyboardButton(text=button_text))

    keyboard.add(types.KeyboardButton(text="Back"))

    await bot.send_message(chat_id=message.chat.id, text="Mavjud userlar:", reply_markup=keyboard)


@dp.message_handler(
    lambda message: any(food_item.full_name in message.text for food_item in Session().query(Video).all()))
async def show_food_details(message: types.Message):
    db = Session()
    selected_food_name = next(
        (food_item.full_name for food_item in db.query(Video).all() if food_item.full_name in message.text), None)
    if message.from_user.id == 5772722670:
        if selected_food_name:
            try:
                selected_food_item = db.query(Video).filter(Video.full_name == selected_food_name).first()
                with open(selected_food_item.file_path, 'rb') as video_file:

                    details_text = f": {selected_food_item.full_name}\n"
                    await bot.send_video(chat_id=message.chat.id, video=video_file, caption=details_text,
                                         reply_markup=order_keyboart())

            finally:
                db.close()


session = Session()


@dp.message_handler(lambda message: message.text == "Video ko'rish")
async def start_food_registration(message: types.Message):
    await hamma_ovqatlar(message)


@dp.message_handler(commands=['send_videos'])
async def send_videos(message: types.Message):
    with open(video.file_path, 'rb') as video_file:
        await bot.send_video(chat_id=-1001201500057, video=video_file,
                             caption='#HappyBirthday @Sohibjon_Xolboboyev_777')
        await message.answer('video guruhga jo''natildi')
    os.remove(video.file_path)
    session.delete(video)
    await message.answer('Video o\'chirildi')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
