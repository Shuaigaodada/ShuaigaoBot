import interactions
from components import *
from event import *
from commands import *

with open("token.txt") as f:
    token = f.read()

bot = interactions.Client(token=token)



bot.start()
