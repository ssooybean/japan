from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types

def user_menu_btns ():
  builder = InlineKeyboardBuilder()

  builder.add( types.InlineKeyboardButton(
    text="Ввести координаты", callback_data="get_predict"
  ))

  builder.adjust(1)
  return builder
