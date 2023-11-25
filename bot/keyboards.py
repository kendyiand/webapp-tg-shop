import telebot
from telebot import types

none = types.ReplyKeyboardRemove()

admin_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
add_item_start = types.KeyboardButton("Добавить товар")
choose_item_start = types.KeyboardButton("Посмотреть список нынешних")
admin_keyboard.add(add_item_start, choose_item_start)


add_item_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
add_item_yes = types.KeyboardButton("Да")
add_item_no = types.KeyboardButton("Нет")
add_item_keyboard.add(add_item_yes, add_item_no)

add_item_end_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
add_item_end = types.KeyboardButton("Ок")
add_item_end_keyboard.add(add_item_end)
