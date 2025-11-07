import os
import discord
import sqlite3
import random
import datetime
import requests
import time
import aiohttp
import ast
import typing
from typing import Optional,List, Tuple,TYPE_CHECKING,Literal
from keep_alive import keep_alive
from discord.ext import commands
from discord import app_commands,ui,ButtonStyle,File
from discord.ui import View, Button
from pokemon import *
from trainers import *
from field import *
from plugins import *
from movelist import *
from attack import *
from typematchup import *
from movelist import *
from hiddenpower import *
from dotenv import load_dotenv
load_dotenv()
token=os.getenv("TOKEN")
ITEMS_PER_PAGE = 15