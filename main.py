# Модули
## Стандартные / локальные
import os
import sys
import random
import time

## PIPy
import requests
import pymongo
import vk


global mongo, bot, bc
VK_CHAT_K = 2000000000		# Константа для корректной работы с чатом
VK_BOT_ID = 280091202		# ID бота (Оо Оо)

def main():
	global mongo, bot, bc

	mongo = connectToMongoDB("python", "bot_oo")
	bot = connectToVK()
	
	declareBotCommands()
	
	pollServerInfo = bot.messages.getLongPollServer()
	
	while (True):
		r = connectToPollVK(pollServerInfo)

		try:
			if (r.json()['failed'] != None):
				pollServerInfo = bot.messages.getLongPollServer()
				continue
		except (KeyError, ValueError):
			pass

		pollServerInfo['ts'] = r.json()['ts']

		for m in r.json()['updates']:
			# Обработка только новых сообщений:
			if (m[0] != 4):
				continue

			# Сообщение не от бота:
			try:
				if (m[7]['from'] == str(VK_BOT_ID)):
					continue
			except KeyError:
				pass

			if (m[3] == VK_BOT_ID):
				continue


			try:
				message_trimmed = trimm(m[6])
				
				if (type(message_trimmed) is list):
					message_trimmed = message_trimmed[0]

				for command in bc:
					for commandName in command[0]:
						if (commandName in message_trimmed):
							# Выполняем команды в зависимости о тих типа
							if (not (type(command[1]) is list)):
								command[1](m)
							else:
								command[1][0](m, command[1][1])
							raise ZeroDivisionError
			except ZeroDivisionError:
				pass
	return

# MongoDB
def connectToMongoDB(dbName, collectionName):
	"""Подключение к MongoDB"""

	#mongo_uri = os.environ['MONGODB_DB_URL']
	mongo_uri = "mongodb://127.0.0.1:27017"
	mongo_client = pymongo.MongoClient(mongo_uri)
	db = mongo_client[dbName]
	mcoll = db[collectionName]
	return mcoll

# VK
def connectToVK():
	"""Подключение к VK.API"""

	return vk.API(access_token="e38f10e4ea7f650911484b4e9101d7ea10959d98b2290b57272d9dabdfde8bfd42a8d5e7550ebcaa7dcf0",
			scope="friends,photos,audio,video,docs,pages,status,wall,groups,messages,email,notifications,offline",
			api_version="5.37")

def connectToPollVK(vals):
	"""Подключение к Poll серверу ВК"""

	return requests.get("http://"+vals['server']+"?act=a_check&key="+vals['key']+"&ts="+str(vals['ts'])+"&wait=10&mode=2")

def vk_send_message(m, **arg):
	"""Оберта для отправки ВК сообщений"""

	global bot

	chat_id = m[3] - VK_CHAT_K
	if (chat_id > 0):
		bot.messages.send(chat_id = chat_id, **arg)
	else:
		bot.messages.send(user_id = m[3], **arg)
	return


# Bot-Commands-Funs
def bot_getRasp(m):
	global mongo, bot

	try:
		message_id = mongo.find_one({"bot_rasp": m[3]})['message_id']
	except TypeError:
		return "No value in MongoDB"
	
	vk_send_message(m, forward_messages = message_id, message = randomHint(["Вот", "Лови", "Прошу", "Пожалуйста", "Вот-вот"]))
	return

def bot_setRasp(m):
	global mongo

	mongo.update_one({"bot_rasp": m[3]}, {"$set": {"bot_rasp": m[3], "message_id": m[1]}}, True)

	return

def bot_help(m):
	global bot, bc, trimm_syms

	tmp = ""

	for c in bc:
		tmp += "\n\n > " + c[2] + "\n"
		tmp += ">-> Использование: \n>->->"
		for h in c[3]:
			tmp += " '" + h + "'"

	tmp += "Бот при парсинге удаляет символы: "
	for s in trimm_syms:
		tmp += " " + s[0] + " (" + s[1] + ")"

	tmp += "\nРазделителем команд является символ " + splitter

	vk_send_message(m, message = tmp)
	return

def bot_isLive(m):
	global bot
	vk_send_message(m, message = randomHint(["Живой", "Жив и цел", "Норм", "Статус: работаю"]))
	return

def bot_say(m):
	global bot
	vk_send_message(m, message = trimm(m[6])[1])
	return

def bot_saySmile(m, args = {'msg': ':-)'}):
	global bot
	vk_send_message(m, message = args['msg'])
	return


# Bot-Commands-Gen
bc = []

def declareBotCommands():
	"""Объявление всех команд бота"""

	# [лист текстов, на которые нужно реагировать], функция, текст помощи
	declareOneBotCommand(["Оо, помощь", "Оо, справка", "Оо, выведи помощь"], bot_help, "Вывод этой помощи")
	declareOneBotCommand(["Оо, кинь расписание", "Оо, расп"], bot_getRasp, "Вывод расписания, запомненого ранее")
	declareOneBotCommand(["#Расписание", "Оо, вот расписание"], bot_setRasp, "Запоминание расписания для дальнейшего вывода")
	declareOneBotCommand(["Оо, ты жив?", "Оо, жив", "Оо, статус"], bot_isLive, "Показывает статус бота")
	declareOneBotCommand(["Оо, скажи", "Оо, произнеси", "Oo, say"], bot_say, "Сказать фразу, [0: фраза]")

	declareOneBotCommand(["Оо, дай пят", "Оо, пять"], [bot_saySmile, {"msg": "&#9995;"}], "Дать пять")
	declareOneBotCommand(["Оо, помолись", "Оо, молитва"], [bot_saySmile, {"msg": "&#128591;"}], "Бот помолится")
	return


def declareOneBotCommand(names, callback, helpTip):
	"""Объявление одной команды бота"""

	global bc

	names_trimmed = trimm(names)
	bc.append([names_trimmed, callback, helpTip, names])

	return

# Other commands
trimm_syms = [[".", "точка"],
			[",", "запятая"],
			[" ", "пробел"],
			["?", "знак вопроса"],
			["-", "минус"]]

splitter = "|"

def trimm(tr):
	"""Исключение недопустимых символов"""

	if (type(tr) == str):
		if (splitter in tr):
			return [trimm(tr.split(splitter)[0])] + tr.split(splitter)[1:]

		tmp = tr

		for t in trimm_syms:
			tmp = tmp.replace(t[0], "")
		tmp = tmp.lower()

		return tmp
	else:
		tmp = []
		for i in tr:
			tmp.append(trimm(i))
		return tmp

def randomHint(msgs):
	"""Выбор случайного элемента из списка строк"""

	return msgs[random.randint(0, len(msgs)-1)]



if (__name__ == "__main__"):
	main()
