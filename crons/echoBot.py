import pymongo
import vk
import os
import requests
import random

global mongo, bot, bc
VK_CHAT_K = 2000000000
VK_BOT_ID = 280091202

def main():
	global mongo, bot, bc

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
				continue

			try:
				if (m[7]['from'] == str(VK_BOT_ID)):
					continue
			except KeyError:
				print("from list in message not found")

			if (m[3] == VK_BOT_ID):
				continue

			try:
				message_trimmed = trimm(m[6])
				for command in bc:
					for commandName in command[0]:
						if (commandName in message_trimmed):
							print(command[1](m))
							raise ZeroDivisionError
			except ZeroDivisionError:
				print("Exited in command-run")

		r = connectToPollVK(pollServerInfo)
	return

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

	try:
		message_id = mongo.find_one({"bot_rasp": m[3]})['message_id']
	except TypeError:
		return "No value in MongoDB"

	hint_messages = ["Вот", "Лови", "Прошу", "Пожалуйста", "Вот-вот"]
	hint_message = hint_messages[random.randint(0, len(hint_messages)-1)]
	
	chat_id = m[3] - VK_CHAT_K
	if (chat_id > 0):
		bot.messages.send(chat_id = chat_id, forward_messages = message_id, message = hint_message)
	else:
		bot.messages.send(user_id = m[3], forward_messages = message_id, message = hint_message)

	return "getRasp"

def bot_setRasp(m):
	global mongo

	a = mongo.update_one({"bot_rasp": m[3]}, {"$set": {"bot_rasp": m[3], "message_id": m[1]}}, True)

	return a

def bot_help(m):
	global bot, bc

	tmp = "-- Оо Оо --"
	tmp += "\n---------\n"

	for c in bc:
		tmp += c[2] + "\n"
		tmp += "Использование: "
		for h in c[3]:
			tmp += "'" + h + "' "
		tmp += "\n---------\n"
	tmp += "\n Бот при парсинге удаляет символы: . (точка), , (запятая) и  (пробел)"
	tmp += "\n-- Oo Oo --"

	chat_id = m[3] - VK_CHAT_K
	if (chat_id > 0):
		bot.messages.send(chat_id = chat_id, message = tmp)
	else:
		bot.messages.send(user_id = m[3], message = tmp)
	return m


# Bot-Commands-Gen
bc = []

def declareBotCommands():
	declareOneBotCommand(["Оо, помощь", "Оо, справка", "Оо, выведи помощь"], bot_help, "Вывод этой помощи")
	declareOneBotCommand(["Оо, кинь расписание", "Оо, расписание", "оо расп"], bot_getRasp, "Вывод расписания, запомненого ранее")
	declareOneBotCommand(["#Расписание", "Оо, вот расписание"], bot_setRasp, "Запоминание расписания для дальнейшего вывода")

	return


def declareOneBotCommand(names, callback, helpTip):
	global bc

	names_trimmed = trimm(names)
	bc.append([names_trimmed, callback, helpTip, names])

	return

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
