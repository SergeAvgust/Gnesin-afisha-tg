from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from threading import Thread

import datetime

Months = {
    1 : "января",
    2 : "февраля",
    3 : "марта",
    4 : "апреля",
    5 : "мая",
    6 : "июня",
    7 : "июля",
    8 : "августа",
    9 : "сентября",
    10 : "октября",
    11 : "ноября",
    12 : "декабря",
}
Weekdays = {
    0 : "Понедельник",
    1 : "Вторник",
    2 : "Среда",
    3 : "Четверг",
    4 : "Пятница",
    5 : "Суббота",
    6 : "Воскресенье",
}

class Scrapper(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.full_afisha = self.scrape_afisha()
        self.data_recieved_at = datetime.date.today()
        self.visitors = 0

    def run(self):
        while True:
            # every hour check if date has changed since last refresh, 
            # if True - refresh cached concerts data
            # i.e. refresh data every day around 00:00 - 01:00
            sleep(3600)
            if datetime.date.today() != self.data_recieved_at:
                self.full_afisha = self.scrape_afisha()
                with open('statistics.txt', 'a') as f:
                    f.write(' '.join( str(s) for s in [datetime.date.today(), '===', self.visitors, '\n']))
                self.visitors = 0


    def get_week(self, offset='0'):
        week = datetime.datetime.today().isocalendar()[1]
        week = week+int(offset)-52 if week+int(offset) > 52 else week+int(offset)
        if week in self.full_afisha:
            return self.full_afisha[week]
        return [(0,'Не поверишь, но я не знаю о концертах на этой неделе! Может быть, в Гнесинке выходные?')]

    def get_day(self, date='0'):
        today = datetime.date.today()
        if date == 'td':
            date = datetime.datetime.strftime(today, '%d.%m')
        elif date == 'tm':
            date = datetime.datetime.strftime(today+datetime.timedelta(days=1), '%d.%m')
        if date == '0':
            return 'Нужно ввести дату в формате ДД.ММ , где ДД.ММ для, к примеру, третьего сентября - 03.09'
        date = date.split('.')
        if len(date) != 2:
            return 'Нужно ввести дату в формате ДД.ММ , где ДД.ММ для, к примеру, третьего сентября - 03.09'
        try:
            int(date[0])
            int(date[1])
        except ValueError:
            return 'Нужно ввести дату в формате ДД.ММ , где ДД.ММ для, к примеру, третьего сентября - 03.09'

        today = datetime.date.today()
        try:
            datef = datetime.date(today.year+1 if int(date[1]) < today.month else today.year, int(date[1]), int(date[0]))
        except ValueError:
            return 'Ты уверен, что это настоящая дата?'
        if datef < today:
            return 'Я не храню данные о прошедших концертах! Попробуй другую дату)'
        if not datef.isocalendar()[1] in self.full_afisha:
            return 'В день, который ты выбрал, кажется, нет концертов. Или ты планируешь больше, чем на месяц вперед - я так не умею)'
        for day in self.full_afisha[datef.isocalendar()[1]]:
            if day[0] == datef:
                return day[1]
        else:
            return 'Кажется, в этот день нет концертов. Попробуй другую дату)'


    def getafisha(self, requested_date = ""):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get('https://halls.gnesin-academy.ru/афиша?date='+requested_date)
        
        # Read js from separate file
        with open('collector.js', 'r') as f:
            js = f.read()
        data = driver.execute_script(js)
        driver.close()
        return data

    def stringify(self, data, today=datetime.date.today()):
        results = {}
        for day in data:
            # check if day is current or upcoming, set up key in results dict
            currdate = datetime.datetime.strptime(day['date'], '%Y-%m-%d').date()
            if currdate < today:
                continue
            weeknum = currdate.isocalendar()[1]
            if not weeknum in results:
                results[weeknum] = []
            
            day_arr = []
            M = Months[currdate.month]
            W = Weekdays[currdate.weekday()]
            day_arr.append(W + ', ' + str(currdate.day) + ' ' + M)
            for event in day['events']:
                day_arr.append('<a href="'+event['link']+'">'+event['name']+'</a>')
                day_arr.append(event['time'])
                day_arr.append(event['place']+'\n')
            results[weeknum].append((currdate, '\n'.join(day_arr)))

        return results

    def scrape_afisha(self):
        today = datetime.date.today()
        curr_afs = self.getafisha(str(datetime.datetime.strftime(today, '%Y-%m')))
        nextmonth = datetime.date(today.year + 1, 1, 1) if today.month == 12 else datetime.date(today.year, today.month + 1, 1)
        next_afs = self.getafisha(str(datetime.datetime.strftime(nextmonth, '%Y-%m')))
        return self.stringify(curr_afs+next_afs, today)


