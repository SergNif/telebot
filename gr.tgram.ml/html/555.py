from typing import Dict
import os, json, time
from fnmatch import fnmatch
import uvicorn
from fastapi import FastAPI  # , Query, APIRouter, Path, BackgroundTasks
from fastapi import Response, Request
from fastapi.templating import Jinja2Templates
from pathlib import Path
import sh



import random, string
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
HOSTDIR =   '/var/wwww/style/Images'    #'/home/serg/photos/'
FLAG_READY_SERVER = False
HOST_SEND_DIR = '/var/wwww/style/Out/'

ssh_20GB_2GB_60rub = '195.234.208.168'  # тут будет модель
ssh_nvme_139rub = '45.130.151.35'  # этот, я тут
ssh_gramm_ml_99rub = '185.195.26.149'

import subprocess

####### SSHstyle/pic02FEB.py
def ssh_send(param=None) -> None:
    global FLAG_READY_SERVER
    # cmd = '/home/serg/gram/gram/bin/python /var/wwww/style/del_out.py'
    # cmd = 'sudo /var/wwww/anaconda3/envs/gram/bin/python /var/wwww/style/pic02FEB.py &'
    # cmd = 'sudo /home/serg/gram/gram/bin/python3 /var/wwww/style/pic02FEB.py &'
    cmd = 'cd /var/wwww ; /usr/bin/env /home/serg/gram/gram/bin/python3 /var/wwww/style/pic02FEB.py &'
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=ssh_20GB_2GB_60rub, username='serg', password='111',
            look_for_keys=True, key_filename='/home/serg/.ssh/id_ed25519.pub', port=22)
    ftp_client = ssh.open_sftp()
    ftp_client.chdir(HOSTDIR)
    ssh.exec_command(cmd)
    print('SSH command START')
    ftp_client.close()
    print('ssh END')

ssh_send()
# arg = ''.join(['sudo rm -r ' , PHOTOPATH , '*.*'])
# print(arg)
# subprocess.Popen(arg, shell=True) 