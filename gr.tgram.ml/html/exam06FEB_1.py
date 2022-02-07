from typing import Dict
import os
import json
import time
from fnmatch import fnmatch
import uvicorn
from fastapi import FastAPI  # , Query, APIRouter, Path, BackgroundTasks
from fastapi import Response, Request
from fastapi.templating import Jinja2Templates
from pathlib import Path
import sh
import subprocess


import random
import string
import telebot
from telebot import types
from telebot.types import Message
import glob

# import asyncio
# import asyncssh
import sys
from telebot.async_telebot import AsyncTeleBot
import paramiko

from PIL import Image

templates = Jinja2Templates(directory='/var/www/gr.tgram.ml/html')
DIR = '/var/www/gr.tgram.ml/html'
TGRAM_DIR = DIR + '/tgram'
IMAGE_DIR = DIR + '/Images/'
STORAGE_DIR = DIR + '/Storage'
TOKEN = '1618584232:AAHmGvkcP91w9gsxM9Vhw5_FdlTJlULD6vg'
STICKER = 'CAACAgQAAxkBAAIEnWH2gp_bPNeujOzLrhUebjjVe8daAAIxAAP1mFALPtINSL0JxOAjBA'
STICKER2 = 'CAACAgIAAxkBAANsYd7QrvW61972Gz-ZEghYeF31iDQAAhcLAALuggcN6CvtTeUcCtkjBA'
PIC_1 = ''
PIC_2 = ''
PIC_cont = ''
PIC_style = ''
PHOTOPATH = DIR + '/photos/'
HOSTDIR = '/var/wwww/style/Images'  # '/home/serg/photos/'
FLAG_READY_SERVER = False
HOST_SEND_DIR = '/var/wwww/style/Out/'
IMAGE_STYLE = DIR + '/ImageStyle'

ssh_20GB_2GB_60rub = '195.234.208.168'  # тут будет модель
ssh_nvme_139rub = '45.130.151.35'  # этот, я тут
ssh_gramm_ml_99rub = '185.195.26.149'


try:
    subprocess.Popen(''.join(['sudo rm -r ', PHOTOPATH, '*.*']), shell=True)
except Exception:
    pass

tg = AsyncTeleBot(TOKEN)
app = FastAPI(
    title="Recipe API", openapi_url="/openapi.json"
)

# ####### Титульная страница по запросу GET


@ app.get('/')
async def main(request: Request):
    pass
    return templates.TemplateResponse('index.html', {'request': request})

# ####### Титульная страница по запросу POST


@app.post('/')
async def lower_case(json_data: Dict):
    update = telebot.types.Update.de_json(json_data)
    print(json_data)
    await tg.process_new_updates([update])


# SSH
def ssh_send(param=None) -> None:
    global FLAG_READY_SERVER
    # cmd = '/home/serg/gram/gram/bin/python /var/wwww/style/pic02FEB.py &'
    # cmd = 'gram && sudo /home/serg/gram/gram/bin/python3   /var/wwww/style/pic02FEB.py &'
    # cmd = '/var/wwww/anaconda3/envs/gram/bin/python /var/wwww/style/pic02FEB.py &'
    cmd = 'cd /var/wwww ; /usr/bin/env /home/serg/gram/gram/bin/python3 /var/wwww/style/pic02FEB.py &'
    llist = dict_json_edit(param="get_first")
    # if len(llist)> 1:
    print(f'{param=} \n {llist=}')
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=ssh_20GB_2GB_60rub, username='serg', password='111',
                look_for_keys=True, key_filename='/home/serg/.ssh/id_ed25519.pub', port=22)
# ssh.connect(hostname = '185.195.26.149', username = 'serg', look_for_keys = True, port = 22 )
# ssh.connect(hostname = '185.195.26.149', username = 'serg', password = '111', port = 22 )
    ftp_client = ssh.open_sftp()
    ftp_client.chdir(HOSTDIR)
    if param == 'get_pic':
        print('param')
        for i, fl in enumerate(ftp_client.listdir(HOST_SEND_DIR)):
            ftp_client.get(HOST_SEND_DIR + fl,  TGRAM_DIR + '/' + fl)
        cmd_del = ''.join(['sudo rm -r ', HOST_SEND_DIR, '*.*'])
        ssh.exec_command(cmd_del)
    if len(llist) > 1:
        pic_style, pic_cont = llist
        print(f'{param=}')
        print(f'{llist=}')
        if param == 'send_pic':
            print(f'{pic_style=} \n {pic_style.replace(STORAGE_DIR, HOSTDIR)=} \n {pic_cont=} \n {pic_cont.replace(STORAGE_DIR, HOSTDIR)=}  ')
            ftp_client.put(pic_style, pic_style.replace(STORAGE_DIR, HOSTDIR))
            time.sleep(3)
            ftp_client.put(pic_cont, pic_cont.replace(STORAGE_DIR, HOSTDIR))
            # stdin, stdout, stderr = ssh.exec_command(cmd)
            ssh.exec_command(cmd)
            print('SSH command START')
            # gds = stdout.readlines()
            # print(*gds)
            FLAG_READY_SERVER = False
            dict_json_edit(param="delete_first")
    print(f'{ftp_client.getcwd()=} ')
    ftp_client.close()
    print('ssh END')


# DICT
def dict_concat(dict_jsn, dict_i):
    if (len(dict_jsn) == 1) and (dict_jsn["-1"] == ["first", "second"]):
        ll = [dict_i]
    else:
        del dict_jsn["-1"]
        ll = [dict_jsn, dict_i]
    rez = {-1: ["first", "second"]}
    m = n = 0
    for ff in ll:
        ff = {int(k): v for k, v in ff.items()}
        for i, nn in enumerate(ff):
            rez[i+m] = ff[nn]
        m = n+1
    return rez


def dict_json(folder=IMAGE_DIR):
    name = []
    dict_i = {}
    if len(os.listdir(folder)) > 1:
        file_list = [f for f in os.listdir(folder) if fnmatch(f, '*_style_*')]
        file_list.sort(key=lambda x: os.path.getmtime(folder + x))
        print('file-list= ', *file_list)

        if len(file_list) > 0:
            for i, mm in enumerate(file_list):
                name = []
                name.append(folder + file_list[i])
                print(f'{name[0]= }')
                if os.path.exists(folder + file_list[i].replace("style_", "")):
                    # (folder + file_list[0].split("_")[0] + '.' + file_list[0].split(".")[-1])
                    name.append(folder + file_list[i].replace("style_", ""))
                    print(f'{name[1]= }')
                dict_i[i] = name
                # PIC_cont= '/var/www/gr.tgram.ml/html/Images/133420623__1618584232_k2y62Hx762_.jpg'
               # PIC_style= '/var/www/gr.tgram.ml/html/Images/133420623__1618584232_k2y62Hx762_style_.jpg'
    # в списке name все файлы, которые пришли пособытию сторожа
    # загрузим json со старым списком
    with open(DIR + '/json_image.json') as f:
        dict_image = json.load(f)
    # сейчас dict_i содержит имена новых картинок, а dict_image содержит список
    # старых картинок
    # объединим оба словаря
    dict_image = dict_concat(dict_image, dict_i)
    #  теперь в словаре добавлена новая пара картинок
    # теперь надо картинки перенести из Images в STORAGE_DIR и поменять имена файлов в словаре
    for key in dict_image:
        if key != int("-1"):
            for i, nn in enumerate(dict_image[key]):
                if os.path.exists(nn):
                    os.rename(nn, nn.replace(IMAGE_DIR, STORAGE_DIR+'/'))
                    dict_image[key][i] = nn.replace(IMAGE_DIR, STORAGE_DIR+'/')
    # теперь все картинки в STORAGE_DIR и имена файлов и ловарь соответствуют
    #  сохраняем словарь
    with open(DIR + '/json_image.json', "w") as outfile:
        json.dump(dict_image, outfile, indent=4, sort_keys=True)
    print(f'{FLAG_READY_SERVER=} ')
    if FLAG_READY_SERVER:
        ssh_send('send_pic')  # as_main()

    # os.rename(name[0], (name[0]).replace(IMAGE_DIR, STORAGE_DIR + '/' + str(index) + '_CN_'))
    # os.rename(name[1], (name[1]).replace(IMAGE_DIR, STORAGE_DIR + '/' + str(index) + '_ST_'))


def dict_json_edit(param=None):
    # загрузим json со старым списком
    with open(DIR + '/json_image.json') as f:
        dict_image = json.load(f)
    dict_image = {int(k): v for k, v in dict_image.items()}
    print(f'{dict_image=}')
    if len(dict_image) > 1:
        print(f'222 {dict_image=}')
        print(f'{param=}')
        print(f'{type(param)=}')
        if param == 'delete_first':
            index = sorted([i for i in dict_image.keys()])[
                1]  # min(dict_image, key=dict_image.get)
            file_del = dict_image.pop(index, "empty")
            print(f'{index=}')
            print(f'{dict_image= }')
            if file_del == "empty":
                dict_image = {"-1": ["first", "second"]}
            else:
                try:
                    subprocess.Popen(''.join(['sudo rm -r ', file_del[0]]), shell=True)
                    subprocess.Popen(''.join(['sudo rm -r ', file_del[1]]), shell=True)
                except Exception:
                    pass
                # os.remove(file_del[0])
                print("delete pic")
            with open(DIR + '/json_image.json', "w") as outfile:
                json.dump(dict_image, outfile, indent=4, sort_keys=True)

        if param == 'get_first':
            index = sorted([i for i in dict_image.keys()])[
                1]  # min(dict_image, key=dict_image.get)
            print(f'{dict_image[index]=}')
            return dict_image[index]
    else:
        with open(DIR + '/json_image.json', "w") as outfile:
            json.dump(dict_image, outfile, indent=4, sort_keys=True)
        return []
    #  сохраняем словарь


# Rename
def rename_PIC(pic_1, pic_style, user_id, chat_id):
    global PIC_1
    global PIC_2
    global PIC_cont
    global PIC_style
    # рандомная часть имени файла
    rand_text = [random.choice(string.ascii_lowercase + string.digits) if i !=
                 5 else random.choice(string.ascii_uppercase) for i in range(10)]

    rand_text = ''.join(rand_text)
    pic_1_ext = pic_1.split('.')[-1]
    pic_2 = pic_1.split('.')[:-1]
    pic_style_ext = pic_style.split('.')[-1]
    pic_2style = pic_style.split('.')[:-1]
    PIC_cont = IMAGE_DIR + str(chat_id) + '__' + \
        str(user_id) + '_' + rand_text + '_.' + pic_1_ext
    PIC_style = IMAGE_DIR + \
        str(chat_id) + '__' + str(user_id) + '_' + \
        rand_text + '_style_.' + pic_style_ext
    PIC_1 = pic_1
    PIC_2 = pic_style
    print(f'{pic_1= }  ')
    print(f'{pic_style= }  ')
    print(f'{PIC_1= }  ')
    print(f'{PIC_2= }  ')
    print(f'{PIC_cont= }  ')
    print(f'{PIC_style= }  ')
    # в эту функцию картинки PIC_1 и PIC_2 пришли с именами pic_1 и pic_2
    # для них были созданы новые имена с Chat_ID и User_ID и уникальной строкой
    # картинки находятся в папке PHOTOPATH /photos
    # их надо перенести в IMAGES и сформировать словарь dict_json_edit
    # Я ГДЕ-ТО ЗАПУТАЛСЯ, ПОЭТОМУ ПОМЕНЯЛ МЕСТАМИ cont и style
    os.rename(pic_1, PIC_style)
    os.rename(pic_style, PIC_cont)
    # arg = ''.join(['sudo rm -r ' , PHOTOPATH , '*.*'])
    # print(arg)
    try:
        subprocess.Popen(''.join(['sudo rm -r ', PHOTOPATH, '*.*']), shell=True)
    except Exception:
        pass


    dict_json()


# RESIZE
def resize_image(image_path,
                 user_id,
                 ext,
                 fixed_width=180):
    img = Image.open(image_path)
    width, height = img.size
    # output_image_path.replace(PHOTOPATH+)
    print(f'The original image size is {width} x {height} \n {image_path= } ')

    # получаем процентное соотношение
    # старой и новой ширины
    width_percent = (fixed_width / float(img.size[0]))
    # на основе предыдущего значения
    # вычисляем новую высоту
    height_size = int((float(img.size[1]) * float(width_percent)))
    # меняем размер на полученные значения
    new_image = img.resize((fixed_width, height_size))
    width, height = new_image.size
    print('The resized image size is {wide} wide x {height} '
          'high'.format(wide=width, height=height))
    # new_image.show()
    if image_path[len(PHOTOPATH):len(PHOTOPATH) + 2] == '1-':
        output_name = '1-' + user_id + '.' + ext
    if image_path[len(PHOTOPATH):len(PHOTOPATH) + 2] == '2-':
        output_name = '2-' + user_id + '.' + ext
    new_image.save(output_name)


# @bot.message_handler(commands=['Style'])
# def button(message):
#     markup = types.InlineKeyboardMarkup(row_width=2)
#     item_style_1 = types.InlineKeyboardButton('Попробуйте этот стиль', callback_data='Style_1')
#     item_style_2 = types.InlineKeyboardButton('Попробуйте этот стиль', callback_data='Style_2')
#     item_style_3 = types.InlineKeyboardButton('Попробуйте этот стиль', callback_data='Style_3')
#     item_style_4 = types.InlineKeyboardButton('Попробуйте этот стиль', callback_data='Style_4')
#     item_style_8 = types.InlineKeyboardButton('Попробуйте этот стиль', callback_data='Style_8')
#     item_style_9_0 = types.InlineKeyboardButton('Попробуйте этот стиль', callback_data='Style_9_0')
#     item_style_9 = types.InlineKeyboardButton('Попробуйте этот стиль', callback_data='Style_9')
#     item_style_11 = types.InlineKeyboardButton('Попробуйте этот стиль', callback_data='Style_11')
#     item_style_12 = types.InlineKeyboardButton('Попробуйте этот стиль', callback_data='Style_12')
#     # item2 = types.InlineKeyboardButton('Пока', callback_data='goodbye')
#     markup.add(item_style_1, item_style_2, item_style_3, item_style_4, item_style_8, item_style_9_0, item_style_9, item_style_11, item_style_12 )

#     bot.send_message(message.chat.id, 'Хотите выбрать стиль из набора?', reply_markup=markup)

# @bot.callback_query_handler(func=lambda call:True)
# def callback(call):
#     if call.message:
#         if call.data == 'question_1':
#             bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text= 'Дела отлично!')
#         elif call.data == 'goodbye':
#             bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text= 'Пока друг')


# BUTTONS Help  Start Button
@tg.message_handler(commands=['help', 'start', 'button', 'style'])
async def send_welcome(message: Message):
    print(message)
    if message.html_text == '/style':
        print('style')
        markup = types.ReplyKeyboardMarkup(
            resize_keyboard=True, one_time_keyboard=True)
        items_yes_style = types.KeyboardButton('Давайте')
        items_no_style = types.KeyboardButton('Нет, есть свой стиль')

        markup.add(items_yes_style, items_no_style)
        # await tg.edit_message_text(chat_id=message.chat.id, message_id=message.id, text="_")
        await tg.send_message(message.chat.id, 'Хотите выбрать из готовых стилей?...', reply_markup=markup)

        # markup_style = types.InlineKeyboardMarkup(row_width=2)
        # items_yes_style = types.InlineKeyboardButton(text="Давайте", callback_data='yes_style')
        # items_no_style = types.InlineKeyboardButton(text="Нет, есть свой стиль", callback_data='no_style')

        # markup.add(items_yes_style, items_no_style)
        # await tg.send_message(message.chat.id, "Хотите выбрать из готовых стилей?", reply_markup=markup_style)

    if message.html_text == '/button':
        markup = types.InlineKeyboardMarkup(row_width=2)
        items_yes = types.InlineKeyboardButton(text="YES", callback_data='yes')
        items_no = types.InlineKeyboardButton(text="NO", callback_data='no')

        markup.add(items_yes, items_no)
        await tg.send_message(message.chat.id, "Хотите узнать свой ник или ID?", reply_markup=markup)
    if message.html_text == '/start':
        await tg.reply_to(message, """\
Привет, я - бот.
Попробуй отправить мне смайлик!\
Или напиши мне любое слово, а угадаю твой возраст!
""")
    # print(message.html_text)
    if message.html_text == '/help':
        await tg.reply_to(message, """В этом есть два варианта переноса стиля одного изображения на другое:
- Вы можете нажать на кнопу Style из меню, выбрать стиль и потом загрузить своё изображение
- Второй вариант - нажмите на значок скрепки и загрузите два изображения. Затем выберите которое из них будет Style""")

# Главная обработка


@tg.message_handler(content_types=['text', 'photo', 'sticker'])
@tg.edited_message_handler(content_types=['text'])
async def gettext(message: Message):
    global FLAG_READY_SERVER
    # print(f'{message.content_type=}')
    if message.content_type == 'text':
        markup_remove = types.ReplyKeyboardRemove()
        if message.text == "MyID":
            await tg.send_message(message.chat.id, f'Your ID: {message.from_user.id}', reply_markup=markup_remove)
            # await tg.send_message(message.chat.id, f'Your ID: {message.from_user.id}', reply_markup=markup_remove)
        elif message.text == "MyNIC":
            await tg.send_message(message.chat.id, f'Your NIC: {message.from_user.first_name}', reply_markup=markup_remove)

        elif message.text == "Давайте":

            markup_1 = types.InlineKeyboardMarkup(row_width=2)
            item_style_1 = types.InlineKeyboardButton(
                text='Попробуйте этот стиль', callback_data='style_1.jpg')
            markup_1.add(item_style_1)
            await tg.send_photo(message.chat.id, photo=open(IMAGE_STYLE + '/'+'style_1.jpg', 'rb'), caption='Мне нрвится этот ^^^', reply_markup=markup_1)

            markup_2 = types.InlineKeyboardMarkup(row_width=2)
            item_style_2 = types.InlineKeyboardButton(
                text='Попробуйте этот стиль', callback_data='style_2.jpg')
            markup_2.add(item_style_2)
            await tg.send_photo(message.chat.id, photo=open(IMAGE_STYLE + '/'+'style_2.jpg', 'rb'), caption='Мне нрвится этот ^^^', reply_markup=markup_2)

            markup_3 = types.InlineKeyboardMarkup(row_width=2)
            item_style_3 = types.InlineKeyboardButton(
                text='Попробуйте этот стиль', callback_data='style_3.jpg')
            markup_3.add(item_style_3)
            await tg.send_photo(message.chat.id, photo=open(IMAGE_STYLE + '/'+'style_3.jpg', 'rb'), caption='Мне нрвится этот ^^^', reply_markup=markup_3)

            markup_4 = types.InlineKeyboardMarkup(row_width=2)
            item_style_4 = types.InlineKeyboardButton(
                text='Попробуйте этот стиль', callback_data='style_4.jpg')
            markup_4.add(item_style_4)
            await tg.send_photo(message.chat.id, photo=open(IMAGE_STYLE + '/'+'style_4.jpg', 'rb'), caption='Мне нрвится этот ^^^', reply_markup=markup_4)

            markup_8 = types.InlineKeyboardMarkup(row_width=2)
            item_style_8 = types.InlineKeyboardButton(
                text='Попробуйте этот стиль', callback_data='style_8.jpg')
            markup_8.add(item_style_8)
            await tg.send_photo(message.chat.id, photo=open(IMAGE_STYLE + '/'+'style_8.jpg', 'rb'), caption='Мне нрвится этот ^^^', reply_markup=markup_8)

            markup_9_0 = types.InlineKeyboardMarkup(row_width=2)
            item_style_9_0 = types.InlineKeyboardButton(
                text='Попробуйте этот стиль', callback_data='style_9_0.jpg')
            markup_9_0.add(item_style_9_0)
            await tg.send_photo(message.chat.id, photo=open(IMAGE_STYLE + '/'+'style_9_0.jpg', 'rb'), caption='Мне нрвится этот ^^^', reply_markup=markup_9_0)

            markup_9 = types.InlineKeyboardMarkup(row_width=2)
            item_style_9 = types.InlineKeyboardButton(
                text='Попробуйте этот стиль', callback_data='style_9.jpg')
            markup_9.add(item_style_9)
            await tg.send_photo(message.chat.id, photo=open(IMAGE_STYLE + '/'+'style_9.jpg', 'rb'), caption='Мне нрвится этот ^^^', reply_markup=markup_9)

            markup_11 = types.InlineKeyboardMarkup(row_width=2)
            item_style_11 = types.InlineKeyboardButton(
                text='Попробуйте этот стиль', callback_data='style_11.jpg')
            markup_11.add(item_style_11)
            await tg.send_photo(message.chat.id, photo=open(IMAGE_STYLE + '/'+'style_11.jpg', 'rb'), caption='Мне нрвится этот ^^^', reply_markup=markup_11)

            markup_12 = types.InlineKeyboardMarkup(row_width=2)
            item_style_12 = types.InlineKeyboardButton(
                text='Попробуйте этот стиль', callback_data='style_12.jpg')
            markup_12.add(item_style_12)
            await tg.send_photo(message.chat.id, photo=open(IMAGE_STYLE + '/'+'style_12.jpg', 'rb'), caption='Мне нрвится этот ^^^', reply_markup=markup_12)
            # item2 = types.InlineKeyboardButton('Пока', callback_data='goodbye')
            # markup.add(item_style_1, item_style_2, item_style_3, item_style_4, item_style_8, item_style_9_0, item_style_9, item_style_11, item_style_12 )

            # bot.send_message(message.chat.id, 'Хотите выбрать стиль из набора?', reply_markup=markup)
        elif message.text == "Нет, есть свой стиль":
            await tg.send_message(message.chat.id, 'I`m shut up', reply_markup=types.ReplyKeyboardRemove())


        else:
            if fnmatch(message.text, 'Iteration*'):
                await tg.reply_to(message, message.text)
            elif (message.text != 'ASK_ASK_query'):
                await tg.reply_to(message, str(random.randint(0, 85)))
            elif (message.text == "ASK_ASK_query") and (message.chat.username == 'SergTREE'):
                print("HELLOOOOOOOO")
                ssh_send('get_pic')  # await as_main()
                for fl in os.listdir(TGRAM_DIR):
                    chat_id = fl.split('__')[0]
                    print('send tg')
                    await tg.send_photo(chat_id, photo=open(TGRAM_DIR + '/' + fl, 'rb'))
                    try:
                        subprocess.Popen(''.join(['sudo rm -r ', TGRAM_DIR, '/', fl]), shell=True)
                    except Exception:
                        pass
                FLAG_READY_SERVER = True  # запустить функцию отправки картинок
                dict_json()  # ssh_send('send_pic')
    if message.content_type == 'photo':
        file_id = message.photo[-1].file_id
        # print(file_id)
        # gt = json.loads(message)
        # with open('photo.json', 'w') as f:
        #     json.dump(message.json, f)

        file_info = await tg.get_file(file_id)
        file_name, file_ext = file_info.file_path.split('.')
        download_file = await tg.download_file(file_name + '.' + file_ext)
        tmp = str(message.from_user.id) + file_id + '.' + file_ext
        # print(f' {tmp=}')
        src = name_photo(message, tmp)
        # file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(API_TOKEN, file_info.file_path))
        # print(f' {src=}')
        with open(src, 'wb') as f:
            f.write(download_file)
            resize_image(src, str(message.from_user.id), file_ext)
        if src[len(PHOTOPATH):len(PHOTOPATH)+2] == '2-':
            fl_list = [f for f in os.listdir(
                PHOTOPATH) if fnmatch(f, '*_choose_style_*')]
            if len(fl_list) > 0:
                # print(f'{(PHOTOPATH + fl_list[0])=}')
                rename_PIC(
                    (PHOTOPATH + fl_list[0]), PIC_2, message.from_user.id, message.chat.id)
                await tg.send_message(message.chat.id, 'Отлично! Изображение придёт после обработки...', reply_markup=types.ReplyKeyboardRemove())
            else:
                markup = types.InlineKeyboardMarkup(row_width=1)
                markup2 = types.InlineKeyboardMarkup(row_width=1)
                items_1pic = types.InlineKeyboardButton(
                    text="THis Pic Style", callback_data='1')
                markup.add(items_1pic)
                print('send 1')
                print(f'{PIC_1=}')
                print(f'{message=} \n {message.chat.id=} ')
                await tg.send_photo(message.chat.id, photo=open('1-'+str(message.chat.id) + '.' + file_ext, 'rb'), caption='выбор фото с которого будет взят стиль', reply_markup=markup)

                items_2pic = types.InlineKeyboardButton(
                    text="THis Pic Style", callback_data='2')
                markup2.add(items_2pic)
                print('send 2')
                print(f'{PIC_2=}')
                await tg.send_photo(message.chat.id, photo=open('2-'+str(message.chat.id) + '.' + file_ext, 'rb'), caption='выбор фото с которого будет взят стиль', reply_markup=markup2)
            for f in glob.glob('/home/serg/*' + str(message.from_user.id) + '*'):
                try:
                    subprocess.Popen(''.join(['sudo rm -r ', f]), shell=True)
                except Exception:
                    pass
    if message.content_type not in ['text', 'photo']:
        print(message)
        await tg.send_sticker(message.chat.id, STICKER)

# Второй уровень меню


@tg.callback_query_handler(func=lambda call: True)
async def answer(call):
    # print(f'{call.data= } ')
    # if call.data == 'yes_style':
    #     markup_reply_style = types.ReplyKeyboardMarkup(
    #         resize_keyboard=True, one_time_keyboard=True)

    #     # markup = types.InlineKeyboardMarkup(row_width=2)
    #     # , callback_data='Style_1')
    #     item_style_1 = types.KeyboardButton('Cтиль 1')
    #     # , callback_data='Style_2')
    #     item_style_2 = types.KeyboardButton('Cтиль 2')
    #     # , callback_data='Style_3')
    #     item_style_3 = types.KeyboardButton('Cтиль 3')
    #     # , callback_data='Style_4')
    #     item_style_4 = types.KeyboardButton('Cтиль 4')
    #     # , callback_data='Style_8')
    #     item_style_8 = types.KeyboardButton('Cтиль 5')
    #     # , callback_data='Style_9_0')
    #     item_style_9_0 = types.KeyboardButton('Cтиль 6')
    #     # , callback_data='Style_9')
    #     item_style_9 = types.KeyboardButton('Cтиль 7')
    #     # , callback_data='Style_11')
    #     item_style_11 = types.KeyboardButton('Cтиль 8')
    #     # , callback_data='Style_12')
    #     item_style_12 = types.KeyboardButton('Cтиль 9')
    #     # item2 = types.KeyboardButton('Пока', callback_data=')#goodbye')
    #     markup_reply_style.add(item_style_1, item_style_2, item_style_3, item_style_4,
    #                            item_style_8, item_style_9_0, item_style_9, item_style_11, item_style_12)

    #     await tg.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text="_")
    #     await tg.send_message(call.message.chat.id, 'Выбирайте и пробуйте...', reply_markup=markup_reply_style)
    if call.data == 'yes':
        markup_reply = types.ReplyKeyboardMarkup(
            resize_keyboard=True, one_time_keyboard=True)
        items_id = types.KeyboardButton('MyID')
        items_username = types.KeyboardButton('MyNIC')

        markup_reply.add(items_id, items_username)
        await tg.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text="_")
        await tg.send_message(call.message.chat.id, 'Нажмите одну из кнопок...', reply_markup=markup_reply)

    elif call.data == 'no':
        await tg.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text="_")
        await tg.send_message(call.message.chat.id, 'I`m shut up', reply_markup=types.ReplyKeyboardRemove())
    elif call.data == '1':
        rename_PIC(PIC_1, PIC_2, call.message.from_user.id,
                   call.message.chat.id)
        print(f'{call.message.chat.id=}  ')
        await tg.send_message(call.message.chat.id, 'Ok 1 - style, wait...', reply_markup=types.ReplyKeyboardRemove())
    elif call.data == '2':
        rename_PIC(PIC_2, PIC_1, call.message.from_user.id,
                   call.message.chat.id)
        print(f'{call.message.chat.id=}  ')
        await tg.send_message(call.message.chat.id, 'Ok 2 - style, wait...', reply_markup=types.ReplyKeyboardRemove())

    # elif (call.data == 'style_1.jpg') or  (call.data == 'style_2.jpg') or  (call.data == 'style_3.jpg') or  (call.data == 'style_4.jpg') or  (call.data == 'style_8.jpg') or  (call.data == 'style_9_0.jpg') or  (call.data == 'style_9.jpg') or  (call.data == 'style_11.jpg') or  (call.data == 'style_12.jpg'):
    elif call.data in os.listdir(IMAGE_STYLE):

        file_id = call.message.photo[-1].file_id
        # print(file_id)
        # gt = json.loads(message)
        # with open('photo.json', 'w') as f:
        #     json.dump(message.json, f)

        file_info = await tg.get_file(file_id)
        file_name, file_ext = file_info.file_path.split('.')
        download_file = await tg.download_file(file_name + '.' + file_ext)

        print(f'{os.listdir(IMAGE_STYLE)=} \n {call=} ')
        # file_info = await tg.get_file(file_id)
        # file_name, file_ext = call.data.split('.')
        # print(*call)

        # download_file = await tg.download_file(IMAGE_STYLE + '/' + call.data)
        print(f' {call.from_user.id=} \n {file_name=} \n {file_ext=}  ')

        tmp = file_name.replace(
            'photos/', str(call.from_user.id) + '_') + '.' + file_ext
        print(f' {tmp=} ')
        call.message.from_user.id = call.from_user.id
        src = name_photo(call.message, tmp)
        # file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(API_TOKEN, file_info.file_path))
        # print(f' {src=}')
        src = src.replace(str(call.from_user.id), str(
            call.from_user.id) + '_choose_style_')
        with open(src, 'wb') as f:
            f.write(download_file)
            resize_image(src, str(call.message.from_user.id), file_ext)

        await tg.send_message(call.message.chat.id, 'Ok Ждём Вашу картинку...', reply_markup=types.ReplyKeyboardRemove())
    print(f'{call.id=}')
    await tg.answer_callback_query(callback_query_id=call.id, text = 'This is a test', show_alert = True)


# создание имен картинок  PIC_1  PIC_2
def name_photo(message, name):
    global PIC_1
    global PIC_2
    # определение текущей рабочей директории
    print(f'{name=}')
    rez = sorted(os.listdir(PHOTOPATH))
    ln = len(str(message.from_user.id))
    fil = 0
    print(f'{rez=}')
    for n, item in enumerate(rez):
        print(f'{type(item)=} \n {item=} \n{str(message.from_user.id)=} \n {len(str(message.from_user.id))=} ')
        print(f'{item[2:ln+2]=}')
        if item[:ln+2] == '1-' + str(message.from_user.id):
            fil += 1
            PIC_2 = PHOTOPATH + "2-" + name.split('/')[-1]  # item[2:]
            print(f'{PIC_2=}')
            return PIC_2
    if fil == 0:
        PIC_1 = PHOTOPATH + '1-' + name.split('/')[-1]
        print(f'{PIC_2=} \n {PIC_1=}')

        return PIC_1


if __name__ == "__main__":
    uvicorn.run("exam06FEB:app", host="0.0.0.0", workers=3,  port=443, log_level="debug",  reload=True,  ssl_keyfile="/etc/letsencrypt/live/gr.tgram.ml/privkey.pem",
                ssl_certfile="/etc/letsencrypt/live/gr.tgram.ml/fullchain.pem")  # , reload_dirs = ["/var/www/gr.tgram.ml/html/$
