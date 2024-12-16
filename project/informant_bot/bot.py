
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.types import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func, and_
from datetime import date
from dotenv import load_dotenv
import os
import redis.asyncio as aioredis
from urllib.parse import quote

# Import SQLAlchemy models
from models.models import User, UserAddresses, Address, Street, Blackout, UserNotify

# Initialize logging
logging.basicConfig(level=logging.INFO)
# Define ANSI escape sequences for colors
GREEN = "\033[92m"
RESET = "\033[0m"

# Load config
load_dotenv('config.env')
# Setup config
API_TOKEN = os.getenv('TG_API_TOKEN')
redis_host = os.getenv('REDIS_HOST')
redis_port = int(os.getenv('REDIS_PORT'))
redis_db = int(os.getenv('REDIS_DB'))
redis_password = os.getenv('REDIS_PASSWORD')
DATABASE_URL = os.getenv('DATABASE_URI_ASINC')

# Initialize Redis storage
storage = RedisStorage2(
    host=redis_host,
    port=redis_port,
    db=redis_db,
    password=redis_password
)

# Setup Telegram API
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)

# Database setup
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
# Register DB builtin function
is_within_range = func.is_within_range


# States for FSM
class Form(StatesGroup):
    address = State()


redis_settings = {
    'host': os.getenv('REDIS_HOST'),
    'port': int(os.getenv('REDIS_PORT')),
    'db': int(os.getenv('REDIS_DB')),
    'password': os.getenv('REDIS_PASSWORD')
}

# Construct the Redis URL
# redis://[:password]@host:port/db
password_part = quote(redis_settings['password']) if redis_settings['password'] else ""
redis_url = f"redis://:{password_part}@{redis_settings['host']}:{redis_settings['port']}/{redis_settings['db']}"

r = aioredis.from_url(redis_url)


# Helper function to get or create a user
async def get_or_create_user(session, user_tg_id, user_name):
    result = await session.execute(select(User).filter_by(user_tg_id=user_tg_id))
    user = result.scalar_one_or_none()
    if not user:
        user = User(user_tg_id=user_tg_id, user_name=user_name)
        session.add(user)
        await session.commit()
        await session.refresh(user)
    return user


# Start command handler
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.answer("Welcome! Используйте команду /add или меню для добавления адресов.")


# Help command handler
@dp.message_handler(commands=['help'])
async def send_help(message: types.Message):
    await send_welcome(message)


# Add address command handler
@dp.message_handler(commands=['add'])
async def add_address(message: types.Message):
    await Form.address.set()
    await message.answer("📝 Введите адрес в формате 'Улица,номер':")


# Handle address input
@dp.message_handler(state=Form.address)
async def process_address(message: types.Message, state: FSMContext):
    async with async_session() as session:
        try:
            user = await get_or_create_user(session, message.from_user.id, message.from_user.username)
            address_input = message.text.split(',')
            if len(address_input) != 2:
                await message.answer("❌ Формат не верен. Используйте 'street,number'.")
                return

            street, number = address_input
            existing_addresses_count = await session.execute(
                select(func.count()).select_from(UserAddresses).filter_by(user_id=user.id))
            existing_addresses_count = existing_addresses_count.scalar()
            if existing_addresses_count >= 5:
                await message.answer("⛔️ Можно добавить не более 5 адресов.")
                return

            new_address = UserAddresses(street=street, number=number, user_id=user.id)
            session.add(new_address)
            await session.commit()
            await message.answer(f"✅ Адрес добавлен: {street}, {number}")
            await find_blackouts(user.id)
        except SQLAlchemyError as e:
            await message.answer(f"❌ Ошибка: {e}")
        finally:
            await state.finish()


# List addresses command handler
@dp.message_handler(commands=['list'])
async def list_addresses(message: types.Message):
    async with async_session() as session:
        try:
            user = await get_or_create_user(session, message.from_user.id, message.from_user.username)
            addresses = await session.execute(select(UserAddresses).filter_by(user_id=user.id))
            addresses = addresses.scalars().all()
            if not addresses:
                await message.answer("📭 У вас нет сохраненных адресов.")
                return

            address_list = "\n".join([f"{addr.street}, {addr.number}" for addr in addresses])
            await message.answer(f"📋 *Ваши адреса:*\n{address_list}", parse_mode=ParseMode.MARKDOWN)
        except SQLAlchemyError as e:
            await message.answer(f"❌ Ошибка: {e}")


# Delete address command handler
@dp.message_handler(commands=['del'])
async def delete_address(message: types.Message):
    async with async_session() as session:
        try:
            user = await get_or_create_user(session, message.from_user.id, message.from_user.username)
            addresses = await session.execute(select(UserAddresses).filter_by(user_id=user.id))
            addresses = addresses.scalars().all()
            if not addresses:
                await message.answer("📭 У вас нет сохраненных адресов.")
                return

            keyboard = InlineKeyboardMarkup()
            for addr in addresses:
                keyboard.add(InlineKeyboardButton(f"{addr.street}, {addr.number}", callback_data=f"delete_{addr.id}"))

            await message.answer("🗑️ *Выберете адрес, который хотите удалить:*", reply_markup=keyboard,
                                 parse_mode=ParseMode.MARKDOWN)
        except SQLAlchemyError as e:
            await message.answer(f"❌ Ошибка: {e}")


# Handle address deletion
@dp.callback_query_handler(lambda c: c.data.startswith('delete_'))
async def process_delete_address(callback_query: types.CallbackQuery):
    address_id = int(callback_query.data.split('_')[1])
    async with async_session() as session:
        try:
            address = await session.get(UserAddresses, address_id)
            if address:
                await session.delete(address)
                await session.commit()
                await callback_query.message.answer(f"✅ Адрес удален: {address.street}, {address.number}")
            else:
                await callback_query.message.answer("❌ Адрес не найден.")
            await bot.answer_callback_query(callback_query.id)    
        except SQLAlchemyError as e:
            await callback_query.message.answer(f"❌ Ошибка: {e}")


# Function to check for blackouts
async def check_for_blackouts(user_id):
    async with async_session() as session:
        blackouts_list = []

        user_addresses = await session.execute(
            select(UserAddresses, User.user_tg_id)
            .join(UserAddresses.user)
            .filter(UserAddresses.user_id == user_id)
        )
        user_addresses = user_addresses.all()

        for user_address, user_tg_id in user_addresses:
            street_name = user_address.street
            addresses = await session.execute(
                select(Address)
                .join(Address.street)
                .filter(
                    and_(
                        Street.street == street_name,
                        is_within_range(Address.number_from, Address.number_to, user_address.number),
                    )
                )
            )
            addresses = addresses.scalars().all()

            for address in addresses:
                blackouts = await session.execute(
                    select(Blackout).filter(
                        Blackout.address_id == address.id,
                        Blackout.blackout_day >= date.today()
                    )
                )
                blackouts = blackouts.scalars().all()

                for blackout in blackouts:
                    existing_notify = await session.execute(
                        select(UserNotify).filter_by(user_id=user_id, off_id=blackout.id)
                    )
                    existing_notify = existing_notify.scalar_one_or_none()

                    if not existing_notify:
                        blackouts_list.append({
                            'user_tg_id': user_tg_id,
                            'street': address.street.street,
                            'number_from': address.number_from,
                            'number_to': address.number_to,
                            'blackout_day': blackout.blackout_day,
                        })
                        new_notify = UserNotify(user_id=user_id, off_id=blackout.id)
                        session.add(new_notify)

        await session.commit()  # Commit after processing all

    return blackouts_list


async def find_blackouts(user_id=None):
    async with async_session() as session:
        try:
            if user_id:
                # Check blackouts for particular user
                users = [await session.get(User, user_id)]
            else:
                # Check blackouts for all users
                users = await session.execute(select(User))
                users = users.scalars().all()

            for user in users:
                blackouts_list = await check_for_blackouts(user.id)
                if blackouts_list:
                    # Prepare message for the user
                    messages = []
                    for blackout in blackouts_list:
                        messages.append(
                            f"🚧 {blackout['street']}, {blackout['number_from']}{' - ' + blackout['number_to'] if blackout['number_to'] else ''} Дата: {blackout['blackout_day']}")

                    # Join all blackouts to a Telegram message and send
                    full_message = "🚨🚨🚨 *Найдено плановое отключение:*\n" + "\n".join(messages)
                    await bot.send_message(
                        chat_id=blackout['user_tg_id'],
                        text=full_message,
                        parse_mode=ParseMode.MARKDOWN
                    )
        except SQLAlchemyError as e:
            logging.error(f"❌ Ошибка: {e}")


# Redis Pub/Sub
async def listen_redis():
    pubsub = r.pubsub()
    await pubsub.subscribe('ch_parser')

    try:
        async for message in pubsub.listen():
            if message['type'] == 'message':
                await handle_message(message['data'])
    except asyncio.CancelledError:
        pass
    finally:
        await pubsub.unsubscribe('ch_parser')
        await pubsub.aclose()


async def handle_message(data):
    # Process the incoming message
    logging.info(f"{GREEN}Received message: {data.decode('utf-8')}{RESET}")
    # await bot.send_message(chat_id='ID', text=data.decode('utf-8'))  # For test send msg to me
    await find_blackouts()


async def on_startup(dp):
    # Start listening to Redis in the background
    dp['redis_task'] = asyncio.create_task(listen_redis())


async def on_shutdown(dp):
    # Cancel the Redis task on shutdown
    dp['redis_task'].cancel()
    await dp['redis_task']
    await r.aclose()


# Start the bot
if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown, skip_updates=True)
