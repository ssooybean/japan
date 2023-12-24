from aiogram import types, F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Bot

from keyboards import user_menu_btns

import joblib
import pandas as pd
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer


# Создаем "базу данных" пользователей
user_dict: dict[int, dict[str, float]] = {}


router = Router()

# Cоздаем класс, наследуемый от StatesGroup, для группы состояний нашей FSM
class FSMFillForm(StatesGroup):
    # Создаем экземпляры класса State, последовательно
    # перечисляя возможные состояния, в которых будет находиться
    # бот в разные моменты взаимодейтсвия с пользователем
    longitude = State()        # Состояние ожидания ввода долготы
    latitude = State()         # Состояние ожидания ввода широты


@router.message(CommandStart(), StateFilter(default_state))
async def start_handler(msg: Message):
    user_dict[msg.from_user.id] ={}

    await msg.answer(f'''<b>Здравствуйте, {msg.from_user.full_name}!</b>\nВы можете получить предсказание с магнитудой ближайшего землетрясения в районе Японии''', reply_markup=user_menu_btns().as_markup())


@router.callback_query(F.data == "get_predict", StateFilter(default_state))
async def start_predict(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(f"Пожалуйста введите долготу")
    await state.set_state(FSMFillForm.longitude)
    

@router.message(StateFilter(FSMFillForm.longitude))
async def process_name_sent(message: Message, state: FSMContext):
    user_id = message.from_user.id
    longitude = float(message.text)

    # Получаем текущий словарь пользователя или создаем новый, если его нет
    user_data = user_dict.get(user_id, {})

    # Обновляем или добавляем значение долготы
    user_data['longitude'] = longitude

    # Обновляем словарь пользователя
    user_dict[user_id] = user_data

    await state.update_data(longitude=float(message.text))
    await message.answer(text='Спасибо!\n\nА теперь введите широту')
    # Устанавливаем состояние ожидания ввода широты
    await state.set_state(FSMFillForm.latitude)

@router.message(StateFilter(FSMFillForm.latitude))
async def process_name_sent(message: Message, state: FSMContext):
    user_id = message.from_user.id
    latitude = float(message.text)

    # Получаем текущий словарь пользователя или создаем новый, если его нет
    user_data = user_dict.get(user_id, {})

    # Обновляем или добавляем значение широты
    user_data['latitude'] = latitude

    # Обновляем словарь пользователя
    user_dict[user_id] = user_data

    await state.update_data(latitude=float(message.text))

    prediction = predict_magnitude(user_data.get('longitude'), user_data.get('latitude'))

    await message.answer(text=f'Предсказание магнитуды ближайшего землетрясения в заданных координатах: {prediction}')
    # Очищаем машину состояний
    await state.clear()

@router.message()
async def open_catalog(msg: Message):
    await msg.answer("Извините, я не понимаю...\n")


from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
import joblib

def predict_magnitude(longitude, latitude):
    # Загрузка модели
    rf_model = joblib.load('random_forest_regressor_model.joblib')
    preprocessor = joblib.load('column_transformer_preprocessor.joblib')

    # Остальные признаки, которые необходимо передать модели
    # В этом примере timestamp, locationSource, и status
    # Замените их на реальные значения, которые вы хотите использовать
    timestamp = 0
    locationSource = "us"
    status = "reviewed"

    # Создание массива с признаками для предсказания
    features = [[timestamp, longitude, latitude, locationSource, status]]

    # Предобработка данных 
    features_preprocessed = preprocessor.transform(pd.DataFrame(features, columns=['timestamp', 'longitude', 'latitude', 'locationSource', 'status']))

    # Получение предсказания
    prediction = rf_model.predict(features_preprocessed)

    return prediction
