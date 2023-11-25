import os
import psycopg2
import telebot
import requests
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

from keyboards import *
from db import *

TOKEN = "6592742075:AAGi9yXLgObGKd2is4yySlHb94GkJ5ljQn0"
bot = telebot.TeleBot(token=TOKEN)

db_init()


@bot.message_handler(commands=["start"])
def menu_message(message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    username = message.from_user.username

    create_user(user_id, first_name, last_name, username)

    user_role = get_user_role(user_id)

    if user_role == "admin":
        bot.send_message(message.chat.id, "Выберите опцию.", reply_markup=admin_keyboard)
        bot.register_next_step_handler(message, choose_option)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton('Open WebApp', web_app=WebAppInfo(url='https://kendyiand.github.io/')))
        bot.send_message(message.chat.id, 'Выберите опцию', reply_markup=markup)


def choose_option(message):
    if message.text == 'Добавить товар':
        ask_for_name(message)
    if message.text == 'Посмотреть список нынешних':
        bot.send_message(message.chat.id, 'Список добавленных товаров.', reply_markup=none)
        show_product_list(message)


def ask_for_name(message):
    msg = bot.send_message(message.chat.id, 'Введите название товара', reply_markup=none)
    bot.register_next_step_handler_by_chat_id(msg.chat.id, ask_for_picture)


def ask_for_picture(message):
    name = message.text
    if len(name) <= 30:
        msg = bot.send_message(message.chat.id, 'Отправьте фотографию товара.')
        bot.register_next_step_handler_by_chat_id(msg.chat.id, ask_for_price, name)
    else:
        msg = bot.send_message(message.chat.id, 'Название может содержать не более 30 символов. '
                                                f'\nКоличество введенных символов - {len(name)}')
        bot.register_next_step_handler_by_chat_id(msg.chat.id, ask_for_picture)


def ask_for_price(message, name):
    if message.photo:
        try:
            file_id = message.photo[2].file_id
        except IndexError:
            try:
                file_id = message.photo[1].file_id
            except IndexError:
                try:
                    file_id = message.photo[0].file_id
                except IndexError:
                    msg = bot.send_message(message.chat.id, 'Пожалуйста, отправьте одно изображение.')
                    bot.register_next_step_handler_by_chat_id(msg.chat.id, ask_for_price, name)
                    return

        msg = bot.send_message(message.chat.id, 'Укажите цену товара в Br')
        bot.register_next_step_handler_by_chat_id(msg.chat.id, ask_for_count, name, file_id)

    else:
        msg = bot.send_message(message.chat.id, 'Пожалуйста, отправьте фотографию товара.')
        bot.register_next_step_handler_by_chat_id(msg.chat.id, ask_for_price, name)


def ask_for_count(message, name, file_id):
    count_text = message.text
    try:
        count = float(count_text.replace(',', '.'))
        msg = bot.send_message(message.chat.id, 'Введите количество товаров.')
        bot.register_next_step_handler_by_chat_id(msg.chat.id, ask_for_sku, name, count, file_id)
    except ValueError:
        msg = bot.send_message(message.chat.id, 'Пожалуйста, введите численное значение количества товаров.')
        bot.register_next_step_handler_by_chat_id(msg.chat.id, ask_for_count, name, file_id)


def ask_for_sku(message, name, price, file_id):
    count_text = message.text
    if count_text.isdigit():
        count = int(count_text)
        msg = bot.send_message(message.chat.id, 'Введите артикул товара (максимум 9 символов), например: 110075, '
                                                'NKBSMUS9W, GP-T-F-XL')
        bot.register_next_step_handler_by_chat_id(msg.chat.id, getresults, name, price, count, file_id)
    else:
        msg = bot.send_message(message.chat.id, 'Пожалуйста, введите численное значение количества.')
        bot.register_next_step_handler_by_chat_id(msg.chat.id, ask_for_sku, name, price, file_id)


def getresults(message, name, price, count, file_id):
    sku = message.text
    if len(sku) <= 9:
        photo_id = file_id
        bot.send_photo(message.chat.id, photo_id)

        msg = bot.send_message(message.chat.id,
                               f"Вы хотите добавить вот такой товар? \n\nНазвание: {name} "
                               f"\nЦена: {price} Br \nКоличество: {count} шт. \nАртикул: {sku}",
                               reply_markup=add_item_keyboard)
        bot.register_next_step_handler_by_chat_id(msg.chat.id, add_item_to_db, name, price, count, sku, file_id)
    else:
        msg = bot.send_message(message.chat.id, 'Артикул должен содержать не более 9 символов. '
                                                'Пожалуйста, введите артикул заново.')
        bot.register_next_step_handler_by_chat_id(msg.chat.id, getresults, name, price, count, file_id)


def add_item_to_db(message, name, price, count, sku, file_id):
    conn = get_connection()
    cursor = conn.cursor()

    if message.text == 'Да':
        cursor.execute("INSERT INTO product (name, price, count, sku, file_id) VALUES (%s, %s, %s, %s, %s)",
                       (name, price, count, sku, file_id))
        conn.commit()

        file_info = bot.get_file(file_id)
        pic = f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}?file_id={file_id}"
        local_file_path = f'../ecom/ecom/static/pictures/{file_id}.png'

        response = requests.get(pic)
        with open(local_file_path, 'wb') as file:
            file.write(response.content)

        bot.send_message(message.chat.id, "Данные успешно добавлены в базу данных.", reply_markup=none)
        menu_message(message)

    elif message.text == 'Нет':
        menu_message(message)

    else:
        bot.send_message(message.chat.id, "Пожалуйста, выберите 'Да' или 'Нет' для продолжения.")


def show_product_list(message):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, name FROM product")

    product_records = cursor.fetchall()

    cursor.close()
    conn.close()

    keyboard = types.InlineKeyboardMarkup()
    back_button = types.InlineKeyboardButton(text='🔙 Назад', callback_data="product-back")

    for id, name in product_records:
        button = types.InlineKeyboardButton(text=name, callback_data=f"product-{id}")
        keyboard.add(button)
    keyboard.add(back_button)

    bot.send_message(message.chat.id, "Выберите один для редактирования.", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith("product-"))
def show_product_info(call):
    bot.answer_callback_query(call.id)
    id = call.data.split("-")[1]

    if id == "back":
        menu_message(call.message)
    else:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT name, price, count, sku, file_id FROM product WHERE id = %s", (id,))
        product_info = cursor.fetchone()

        cursor.close()
        conn.close()

        if product_info:
            name, price, count, sku, file_id = product_info
            response_text = f"Информация о продукте:\n\nНазвание: {name}\nЦена: {price} Br\nКоличество: " \
                            f"{count} шт.\nАртикул: {sku}"

            product_keyboard = types.InlineKeyboardMarkup()
            delete_product = types.InlineKeyboardButton(text='❌ Удалить',
                                                        callback_data=f"options-delete_product-{id}")
            back_to_list = types.InlineKeyboardButton(text='🔙 Назад',
                                                      callback_data="options-back_to_list")
            list_edit = types.InlineKeyboardButton(text='🔀 Редактировать',
                                                   callback_data=f"options-list_edit-{id}")

            product_keyboard.add(back_to_list, list_edit, delete_product)

            bot.send_photo(call.message.chat.id, photo=open(f'../ecom/ecom/static/pictures/{file_id}.png', 'rb'), caption=response_text,
                           reply_markup=product_keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith("options-"))
def product_options(call):
    option = call.data.split("-")[1]

    if option == "back_to_list":
        show_product_list(call.message)
        bot.answer_callback_query(call.id)

    if option == "delete_product":
        id = call.data.split("-")[2]

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT file_id FROM product WHERE id = %s", (id,))
        file_id = cursor.fetchone()[0]

        file_path = os.path.join("pictures", f"{file_id}.png")
        if os.path.exists(file_path):
            os.remove(file_path)

        cursor.execute("DELETE FROM product WHERE id = %s", (id,))
        conn.commit()
        bot.send_message(call.message.chat.id, f"Товар успешно удален.")
        menu_message(call.message)

        bot.answer_callback_query(call.id)

        cursor.close()
        conn.close()

    if option == "list_edit":
        id = call.data.split("-")[2]

        edit_keyboard = types.InlineKeyboardMarkup()

        row1 = [types.InlineKeyboardButton("Название", callback_data=f"edit-name-{id}"),
                types.InlineKeyboardButton("Фото", callback_data=f"edit-photo-{id}"),
                types.InlineKeyboardButton("Цена", callback_data=f"edit-price-{id}")]

        row2 = [types.InlineKeyboardButton("Количество", callback_data=f"edit-count-{id}"),
                types.InlineKeyboardButton("Артикул", callback_data=f"edit-sku-{id}"),
                types.InlineKeyboardButton("🔙 Назад", callback_data=f"edit-{id}")]

        edit_keyboard.add(*row1)
        edit_keyboard.add(*row2)

        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=edit_keyboard)
        bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("edit-"))
def edit_options(call):
    option = call.data.split("-")[1]

    if len(call.data.split("-")) < 3:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        show_product_info(call)
        bot.answer_callback_query(call.id)

    if option == "name":
        id = call.data.split("-")[2]
        bot.send_message(call.message.chat.id, 'Введите новое название товара.')
        bot.register_next_step_handler(call.message, edit_name, id)
        bot.answer_callback_query(call.id)

    if option == "photo":
        id = call.data.split("-")[2]
        bot.send_message(call.message.chat.id, 'Отправьте новую фотографию товара.')
        bot.register_next_step_handler(call.message, edit_photo, id)
        bot.answer_callback_query(call.id)

    if option == "price":
        id = call.data.split("-")[2]
        bot.send_message(call.message.chat.id, "Отправьте новую цену")
        bot.register_next_step_handler(call.message, edit_price, id)
        bot.answer_callback_query(call.id)

    if option == "count":
        id = call.data.split("-")[2]
        bot.send_message(call.message.chat.id, "Отправьте новое количество.")
        bot.register_next_step_handler(call.message, edit_count, id)
        bot.answer_callback_query(call.id)

    if option == "sku":
        id = call.data.split("-")[2]
        bot.send_message(call.message.chat.id, "Отправьте новый артикул.")
        bot.register_next_step_handler(call.message, edit_sku, id)
        bot.answer_callback_query(call.id)


def edit_name(message, id):
    new_name = message.text

    conn = get_connection()
    if len(new_name) <= 30:
        cursor = conn.cursor()

        cursor.execute("UPDATE product SET name = %s WHERE id = %s", (new_name, id))

        conn.commit()

        ok_keyboard = types.InlineKeyboardMarkup()
        ok = types.InlineKeyboardButton("Ок", callback_data=f"product-{id}")
        ok_keyboard.add(ok)

        bot.send_message(message.chat.id, f"Название товара успешно обновлено на - {new_name}", reply_markup=ok_keyboard)

    else:
        msg = bot.send_message(message.chat.id, 'Название может содержать не более 30 символов. '
                                                f'\nКоличество введенных символов - {len(new_name)}')
        bot.register_next_step_handler_by_chat_id(msg.chat.id, edit_name, id)


def edit_photo(message, id):
    if message.photo:
        try:
            file_id = message.photo[2].file_id
        except IndexError:
            try:
                file_id = message.photo[1].file_id
            except IndexError:
                try:
                    file_id = message.photo[0].file_id
                except IndexError:
                    msg = bot.send_message(message.chat.id, 'Пожалуйста, отправьте одно изображение.')
                    bot.register_next_step_handler_by_chat_id(msg.chat.id, edit_photo, id)
                    return

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT file_id FROM product WHERE id = %s", (id,))
        old_file_id = cursor.fetchone()[0]

        old_file_path = os.path.join("pictures", f"{old_file_id}.png")
        if os.path.exists(old_file_path):
            os.remove(old_file_path)

        file_info = bot.get_file(file_id)
        pic = f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}?file_id={file_id}"
        local_file_path = f'../ecom/ecom/static/pictures/{file_id}.png'

        response = requests.get(pic)
        with open(local_file_path, 'wb') as file:
            file.write(response.content)

        cursor.execute("UPDATE product SET file_id = %s WHERE id = %s", (file_id, id))

        conn.commit()
        cursor.close()
        conn.close()

        ok_keyboard = types.InlineKeyboardMarkup()
        ok = types.InlineKeyboardButton("Ок", callback_data=f"product-{id}")
        ok_keyboard.add(ok)

        bot.send_message(message.chat.id, f"Фотография товара успешно обновлена.", reply_markup=ok_keyboard)

    else:
        msg = bot.send_message(message.chat.id, 'Пожалуйста, отправьте фотографию товара.')
        bot.register_next_step_handler_by_chat_id(msg.chat.id, edit_photo, id)


def edit_price(message, id):
    new_price_text = message.text
    try:
        new_price = float(new_price_text.replace(',', '.'))
        conn = get_connection()
        cursor = conn.cursor()

        ok_keyboard = types.InlineKeyboardMarkup()
        ok = types.InlineKeyboardButton("Ок", callback_data=f"product-{id}")
        ok_keyboard.add(ok)

        cursor.execute("UPDATE product SET price = %s WHERE id = %s", (new_price, id))
        conn.commit()

        cursor.close()
        conn.close()

        bot.send_message(message.chat.id, f"Цена товара успешно обновлена на {new_price} Br", reply_markup=ok_keyboard)
    except ValueError:
        msg = bot.send_message(message.chat.id, 'Пожалуйста, введите численное значение цены.')
        bot.register_next_step_handler_by_chat_id(msg.chat.id, edit_price, id)


def edit_count(message, id):
    new_count_text = message.text
    try:
        new_count = int(new_count_text)
        conn = get_connection()
        cursor = conn.cursor()

        ok_keyboard = types.InlineKeyboardMarkup()
        ok = types.InlineKeyboardButton("Ок", callback_data=f"product-{id}")
        ok_keyboard.add(ok)

        cursor.execute("UPDATE product SET count = %s WHERE id = %s", (new_count, id))
        conn.commit()

        cursor.close()
        conn.close()

        bot.send_message(message.chat.id, f"Количество товаров успешно обновлено на {new_count} шт.", reply_markup=ok_keyboard)
    except ValueError:
        msg = bot.send_message(message.chat.id, 'Пожалуйста, введите численное значение количества товаров.')
        bot.register_next_step_handler_by_chat_id(msg.chat.id, edit_count, id)


def edit_sku(message, id):
    new_sku = message.text

    if len(new_sku) <= 9:
        conn = get_connection()
        cursor = conn.cursor()

        ok_keyboard = types.InlineKeyboardMarkup()
        ok = types.InlineKeyboardButton("Ок", callback_data=f"product-{id}")
        ok_keyboard.add(ok)

        cursor.execute("UPDATE product SET sku = %s WHERE id = %s", (new_sku, id))
        conn.commit()

        cursor.close()
        conn.close()

        bot.send_message(message.chat.id, f"Артикул товара успешно обновлен на {new_sku}.", reply_markup=ok_keyboard)
    else:
        msg = bot.send_message(message.chat.id, 'Артикул не может быть длиннее 9 символов. Пожалуйста, введите новый артикул.')
        bot.register_next_step_handler_by_chat_id(msg.chat.id, edit_sku, id)


bot.polling(none_stop=True)
