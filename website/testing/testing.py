from . import db
from .models import Search, History, Today
from datetime import date

def deleteDataToday():

    history_all = History.query.all()

    today = date.today().strftime('%d/%m/%Y')
    # for x in history_all:
    #     if x.date ==
    print(today)