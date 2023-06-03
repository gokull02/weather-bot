import json
import requests
import re
from datetime import datetime
import requests
import pandas as pd
questionsUrl = './questionsComma.csv'
df = pd.read_csv(questionsUrl, sep=",",
                 skipinitialspace=True)
# print(df['Question'].str.lower() == "hi")
# import pytz
# cet = pytz.timezone('CET')
# url = "https://api.telegram.org/bot2020338407:AAGonMkXK5auCPbkpusrA3jDaVwlHovqeu0/sendMessage"
last_read_id = -1
url = "https://api.telegram.org/bot6143320760:AAGR0uJas9B4sMS2_4clIi6CMYohswfzdt0"
try_again_text = "-1"


def auto_answer(message):
    # String = decodedResponse['result'][0]['message']['text']
    # if(String[-1] == '?'):

    answer = df.loc[df['Question'].str.lower().replace(
        to_replace='\?', value='', regex=True)
        == message.lower()]

    if not answer.empty:
        answer = answer.iloc[0]['Answer']
        return answer
    else:
        return "Sorry, I could not understand you !!! I am still learning and try to get better in answering."


def start(last_message, chat_id):
    global url
    global last_read_id
    if ("/start" in last_message['message']['text']) and (last_read_id != last_message['update_id']):

        last_read_id = last_message['update_id']
        parameters = {
            "chat_id": chat_id,
            "text": "Hey! How can i help you today.!"
        }
        response = requests.get(url+"/sendMessage", data=parameters)


listOfDates = []
parameters = []
forecasts = []



def forecast(last_message, chat_id):
    
    global url
    global parameters
    global last_read_id
    global listOfDates
    if ("/forecast" in last_message['message']['text']) and (last_read_id != last_message['update_id']):
        forecastparameters = {
                "chat_id": chat_id,
                "text": "Enter the city you want to know the weather of"
            }
        response = requests.get(url+"/sendMessage", data=forecastparameters)
        last_read_id = last_message['update_id']
        while(True):
            q = requests.get(url+"/getUpdates?offset=-1")
            qJson = q.json()
            weatherQuery = qJson['result'][0]['message']['text']
            if str(weatherQuery)!='/forecast':
                break
        forecastUrl = "https://api.openweathermap.org/data/2.5/forecast?q="+weatherQuery+"&appid=d19877b60e33d88d860eff5661a77a05&units=metric"
        res = requests.get(
            forecastUrl)
        weatherDataList = json.loads(res.text)
        listOfForecast = weatherDataList['list']
        for i in range(len(listOfForecast)):
            forecasts.append(listOfForecast[i])
            t1 = datetime.strptime(listOfForecast[i]['dt_txt'],
                                   '%Y-%m-%d %H:%M:%S')

            listOfDates.append("%s-%s-%s" % (t1.day, t1.month, t1.year))
        listOfDates = list(set(listOfDates))
        
        for i in range(len(listOfDates)):
            parameters.append(
                {"text": listOfDates[i], "callback_data": listOfDates[i]})
        # send_buttons(chat_id, parameters, "Predict weather on")
        listDate = []
        listOflistDate = []
        for i in range(1, len(listOfDates)+1):
            listDate.append(
                {"text": listOfDates[i-1], "callback_data": listOfDates[i-1]+",date"})
            if i % 3 == 0 and i != 0:
                listOflistDate.append(listDate)
                listDate = []
        send_buttons(
            chat_id, listOflistDate, "Predict weather on")
        while True:
            response = requests.get(url+"/getUpdates?offset=-1")
            decodedResponse = response.json()
            if ('callback_query' in decodedResponse['result'][0]):
                break



def send_buttons(chat_id, callback_object, text):

    keyboard = json.dumps(
        {'inline_keyboard': callback_object})
    parameters = {
        "chat_id": chat_id,
        "text": text,
        "reply_markup": keyboard
    }

    response = requests.post(url+"/sendMessage", data=parameters)


def weather(last_message, chat_id):
    global url
    global last_read_id
    global try_again_text
    res = requests.get(
        'https://api.openweathermap.org/data/2.5/weather?q=idukki&appid=d19877b60e33d88d860eff5661a77a05&units=metric')
    weatherData = json.loads(res.text)

    if ("/weather" in last_message['message']['text']) and (last_read_id != last_message['update_id']):

        last_read_id = last_message['update_id']
        parameters = {
            "chat_id": chat_id,
            "text": "Enter the city you want to know the weather of"
        }
        response = requests.get(url+"/sendMessage", data=parameters)
        # waiting for reply
        last_read_id = last_message['update_id']
        while True:
            q = requests.get(url+"/getUpdates?offset=-1")
            qJson = q.json()
            if('/weather' not in qJson['result'][0]['message']['text']):
                weatherQuery = qJson['result'][0]['message']['text']
                res = requests.get(
                    'https://api.openweathermap.org/data/2.5/weather?q='+str(weatherQuery) + '&appid=d19877b60e33d88d860eff5661a77a05&units=metric')
                weatherData = json.loads(res.text)
                last_read_id = last_message['update_id']
                if (weatherData['cod'] == 200):

                    parameters = {
                        "chat_id": chat_id,
                        "photo": "https://openweathermap.org/img/wn/"+weatherData['weather'][0]['icon']+"@2x.png"
                    }
                    response = requests.get(
                        url+"/sendPhoto", data=parameters)

                    sr = int(weatherData['sys']['sunrise'])
                    ss = int(weatherData['sys']['sunset'])
                    sunrise = datetime.fromtimestamp(
                        sr).strftime('%H:%M:%S')
                    sunset = datetime.fromtimestamp(
                        ss).strftime('%H:%M:%S')
                    parameters = {
                        "chat_id": chat_id,
                        "text": "🏙 City name: "+weatherQuery+"\n🔥 Temperature: "+str(weatherData['main']['temp'])+"°C\n💡 Feels like: "+str(weatherData['main']['feels_like'])+"\n🤯 Pressure: "+str(weatherData['main']['pressure'])+"\n💧 Humidity: "+str(weatherData['main']['humidity'])+"\n🌫 Visibility: "+str(weatherData['visibility'])+"m\n🌬 Wind Speed: "+str(weatherData['wind']['speed'])+"\n💨 Wind degree: "+str(weatherData['wind']['deg'])+"\n☁️ Clouds: "+str(weatherData['clouds']['all'])+"\n⛅️ Sunrise: "+sunrise+"\n🌘 Sunset: "+sunset
                    }
                    response = requests.get(
                        url+"/sendMessage", data=parameters)

                    try_again_text = "-1"
                    while True:
                        q = requests.get(url+"/getUpdates?offset=-1")
                        qJson = q.json()
                        loopWeatherQuery = qJson['result'][0]['message']['text']
                        if weatherQuery!=loopWeatherQuery:
                            break
                    break
                elif(weatherData['cod'] == 401):
                    if try_again_text != str(weatherQuery):
                        parameters = {
                            "chat_id": chat_id,
                            "text": "No city found try another city"
                        }
                        response = requests.get(
                            url+"/sendMessage", data=parameters)
                        try_again_text = str(weatherQuery)
                else:
                    print("Some problem in bot")


question = '-1-1-2-4214'
last_read_id=-1
time=False
while True:
    
    # url = "https://api.telegram.org/bot6143320760:AAGR0uJas9B4sMS2_4clIi6CMYohswfzdt0/getUpdates?offset=-1"
    # url = "https://api.telegram.org/bot6143320760:AAGR0uJas9B4sMS2_4clIi6CMYohswfzdt0/getUpdates?offset=-1"

    response = requests.get(url+"/getUpdates?offset=-1")
    decodedResponse = response.json()
    
    timeRanges = []
    currentMessage='-121'
    if ('callback_query' in decodedResponse['result'][0]):
        last_message = decodedResponse['result'][0]
        last_read_id=last_message['update_id']
        data_from_callback = last_message['callback_query']['data']
        chat_id = last_message['callback_query']['message']['chat']['id']

        if time==True:  
            txt = data_from_callback
            x = re.split(',', txt)
            t1 = datetime.strptime(x[1],
                                   '%Y-%m-%d %H:%M:%S')
            
            for forecast in forecasts:
                if str(t1) in forecast['dt_txt']:
                    parameters = {
                        "chat_id": chat_id,
                        "photo": "https://openweathermap.org/img/wn/"+forecast['weather'][0]['icon']+"@2x.png"
                    }
                    response = requests.get(
                        url+"/sendPhoto", data=parameters)

                    # sr = int(forecast['sys']['sunrise'])
                    # ss = int(forecast['sys']['sunset'])
                    # sunrise = datetime.fromtimestamp(
                    #     sr).strftime('%H:%M:%S')
                    # sunset = datetime.fromtimestamp(
                    #     ss).strftime('%H:%M:%S')
                    parameters = {
                        "chat_id": chat_id,
                        "text": "🔥 Temperature: "+str(forecast['main']['temp'])+"°C\n💡 Feels like: "+str(forecast['main']['feels_like'])+"\n🤯 Pressure: "+str(forecast['main']['pressure'])+"\n💧 Humidity: "+str(forecast['main']['humidity'])+"\n🌫 Visibility: "+str(forecast['visibility'])+"m\n🌬 Wind Speed: "+str(forecast['wind']['speed'])+"\n💨 Wind degree: "+str(forecast['wind']['deg'])+"\n☁️ Clouds: "+str(forecast['clouds']['all'])
                    }
                    response = requests.get(
                        url+"/sendMessage", data=parameters)
                    time=False
        txt = data_from_callback
        x2 = re.split(',', txt)
        last_read_id=-1
        if 'date' == x2[1] and last_read_id != last_message['update_id']: 
            last_read_id=last_message['update_id']
            dateRanges=[]
            for forecast in forecasts:
                t1 = datetime.strptime(forecast['dt_txt'],
                                    '%Y-%m-%d %H:%M:%S')
                txt = data_from_callback
                x3 = re.split(',', txt)
                if "%s-%s-%s" % (t1.day, t1.month, t1.year) == x3[0]:
                    timeRanges.append("%s:%s:%s" % (t1.hour, t1.minute, t1.second))
                    dateRanges.append("%s-%s-%s" % (t1.year, t1.month, t1.day))
            listDate = []
            listOflistDate = []
            for i in range(1, len(timeRanges)+1):
                listDate.append(
                    {"text": timeRanges[i-1], "callback_data":"time,"+dateRanges[i-1]+" "+timeRanges[i-1]})
                if i % 2 == 0 and i != 0:
                    listOflistDate.append(listDate)
                    listDate = []
            send_buttons(
                chat_id, listOflistDate, "Select the time")
            while True:
                response = requests.get(url+"/getUpdates?offset=-1")
                decodedResponse = response.json()
                last_message = decodedResponse['result'][0]
                if("time" in last_message['callback_query']['data'] ):
                    time=True
                    break
    else:

        if(len(decodedResponse['result']) != 0):
            last_message = decodedResponse['result'][0]
            chat_id = last_message['message']['chat']['id']
            String = decodedResponse['result'][0]['message']['text']
            s1 = slice(1)
            if(String[s1] == '/'):
                if('/start' in decodedResponse['result'][0]['message']['text']):
                    start(last_message, chat_id=chat_id)
                if('/forecast' in decodedResponse['result'][0]['message']['text']):
                    # # {'update_id': 227072810, 'message': {'message_id': 1181, 'from': {'id': 1887432410, 'is_bot': False, 'first_name': 'Gokul', 'language_code': 'en'}, 'chat': {'id': 1887432410, 'first_name': 'Gokul', 'type': 'private'}, 'date': 1677782830, 'text': '/forecast', 'entities': [{'offset': 0, 'length': 9, 'type': 'bot_command'}]}}      
                    print(last_message)
                    forecast(last_message, chat_id=chat_id)
                if('/weather' in decodedResponse['result'][0]['message']['text']):
                    # takeQuery()
                    weather(last_message, chat_id=chat_id)
            else:
                if question != decodedResponse['result'][0]['message']['text']:

                    msg = auto_answer(
                        decodedResponse['result'][0]['message']['text'])

                    parameters = {
                        "chat_id": chat_id,
                        "text": msg
                    }
                    response = requests.get(
                        url+"/sendMessage", data=parameters)
                    question = decodedResponse['result'][0]['message']['text']

# url = 'https://raw.githubusercontent.com/vikasjha001/telegram/main/qna_chitchat_professional.tsv'
# HACAq0EwiDrOfYaBkZNqeshIM46bCexa
# {'ok': True, 'result': [{'update_id': 227072419, 'callback_query': {'id': '8106460477530363864', 'from':
# {'id': 1887432410, 'is_bot':# False, 'first_name': 'Gokul', 'language_code': 'en'},
# 'message': {'message_id': 516, 'from': {'id': 6143320760, 'is_bot': True, 'first_name':# 'weatherwizard', 'username': 'wind_whisperer_bot'},
# 'chat': {'id': 1887432410, 'first_name': 'Gokul', 'type': 'private'}, 'date': 1677519218,
# 'text': 'Predict weather on', 'reply_markup': {'inline_keyboard':[[{'text': '28', 'callback_data': 'vide3o'}, {'text': '29', 'callback_data':
# 'playlist'}]]}}, 'chat_instance': '6416464067071861225', 'data': 'vide3o'}}]}
