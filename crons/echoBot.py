import pymongo
import vk
import os
import requests
import random

global mongo, bot
VK_CHAT_K = 2000000000

def main():
	global mongo, bot

	mongo = connectToMongoDB("python", "bot_oo")
	bot = connectToVK()
	
	declareBotCommands()
	
	pollServerInfo = bot.messages.getLongPollServer()
	r = connectToPollVK(pollServerInfo)
	print(r.json())
	
	while (r != None):
		pollServerInfo['ts'] = r.json()['ts']
		print(r.json())

		for m in r.json()['updates']:
			if (m[0] != 4):
				break

#			try:
			message_trimmed = trimm(m[6])
			for command in bc:
				for commandName in command[0]:
					if (commandName in message_trimmed):
						print(command[1](m))
#							raise IndexError
#			except IndexError:
#				pass

		r = connectToPollVK(pollServerInfo)

# MongoDB
def connectToMongoDB(dbName, collectionName):
	mongo_uri = os.environ['OPENSHIFT_MONGODB_DB_URL']
	mongo_client = pymongo.MongoClient(mongo_uri)
	db = mongo_client[dbName]
	mcoll = db[collectionName]
	return mcoll

# VK
def connectToVK():
	return vk.API(access_token="e38f10e4ea7f650911484b4e9101d7ea10959d98b2290b57272d9dabdfde8bfd42a8d5e7550ebcaa7dcf0",
			scope="friends,photos,audio,video,docs,pages,status,wall,groups,messages,email,notifications,offline",
			api_version="5.37")

def connectToPollVK(vals):
	return requests.get("http://"+vals['server']+"?act=a_check&key="+vals['key']+"&ts="+str(vals['ts'])+"&wait=10&mode=2")


# Bot-Commands-Funs
def bot_getRasp(m):
	global mongo, bot

	# Новое сообщение
	if (m[0] != 4):
		return

	try:
		message_id = mongo.find_one({"bot_rasp": m[3]})['message_id']
	except TypeError:
		return

	hint_messages = ["Вот", "Лови", "Прошу", "Пожалуйста", "Вот-вот"]
	hint_message = hint_messages[random.randint(0, len(hint_messages)-1)]
	
	chat_id = m[3] - VK_CHAT_K
	if (chat_id > 0):
		bot.messages.send(chat_id = (m[3] - VK_CHAT_K), forward_messages = message_id, message = hint_message)
	else:
		bot.messages.send(user_id = m[3], forward_messages = message_id, message = hint_message)

	return

def bot_setRasp(m):
	global mongo

	if (m[0] != 4):
		return

	try:
		mongo.find_one({"bot_rasp": m[3]})

		mongo.update_one({"bot_rasp": m[3]}, {"$set": {"message_id": m[1]}})
	except TypeError:
		mongo.insert_one({"bot_rasp": m[3], "message_id": m[1]})

	return

def bot_help(m):
	if (m[0] != 4):
		return

	tmp = "-- Оо Оо --"
	tmp += "\n---------\n"

	for c in bc:
		tmp += c[2] + "\n"
		tmp += "Использование: "
		for h in c[0]:
			tmp += "'" + h + "'"
		tmp += "\n---------\n"
	tmp += "\n Бот при парсинге удаляет символы: . (точка), , (запятая) и  (пробел)"
	tmp += "\n-- Oo Oo --"

	chat_id = m[3] - VK_CHAT_K
	if (chat_id > 0):
		bot.messages.send(chat_id = (m[3] - VK_CHAT_K), message = tmp)
	else:
		bot.messages.send(user_id = m[3], message = tmp)
	return


# Bot-Commands-Gen
bc = []

def declareBotCommands():
	declareOneBotCommand(["Оо, помощь", "Оо, справка", "Оо, выведи помощь"], bot_help, "Вывод этой помощи")
	declareOneBotCommand(["Оо, кинь расписание", "Оо, расписание", "оо расп"], bot_getRasp, "Вывод расписания, запомненого ранее")
	declareOneBotCommand(["#Расписание", "Оо, вот расписание"], bot_setRasp, "Запоминание расписания для дальнейшего вывода")


def declareOneBotCommand(names, callback, helpTip):
	names_trimmed = trimm(names)
	bc.append([names_trimmed, callback, helpTip])

def trimm(tr):
	if (type(tr) == str):
		tmp = tr

		tmp = tmp.replace(".", "")
		tmp = tmp.replace(",", "")
		tmp = tmp.replace(" ", "")
		tmp = tmp.lower()

		return tmp
	else:
		tmp = []
		for i in tr:
			tmp.append(trimm(i))
		return tmp


if (__name__ == "__main__"):
	main()
