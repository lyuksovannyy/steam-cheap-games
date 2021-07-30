import requests
import colorama

import re
import os
import time
import random
import json

from colorama import Fore, Style

colorama.init()

detalied_actions = True # print more information
detailed_errors = True # print more info about errors, must be on "print_error"
print_error = True # print errors

currency = "ru" # recommended currency for that is Russian Ruble or Argentina Peso, by that you can buy games for lower price
secondcurrency = 5 # https://stackoverflow.com/a/65653682 
currency_mark = "pуб."
pages = 5 # how many pages will parsed
page_from = 0 # starting from page
games_limit = 0 # how many games you need to parse | 0 - until pages end.
sleep_time = 1.3 # time to next card info get

using_proxies = True
# SCRIPT START #

def ApplyProxy():
	proxylist = requests.get('https://api.proxyscrape.com?request=getproxies&proxytype=socks5&timeout=1000')
	proxylist = proxylist.text
	proxies = str(proxylist).split('\n')
	try:
		proxy = str(proxies[random.randint(0, len(proxies))])
	except:
		proxy = str(proxies[0])
	useproxy = str('socks5://'+str(proxy).replace('\r',''))
	proxy = dict(http=useproxy, https=useproxy)
	return proxy

def ProxyRequest(url, num):
	pp = 0
	todisableproxy = 0
	for g_ in range(999):
		proxy = ApplyProxy()
		try:
			if pp == 0:
				request = requests.get(url, proxies = proxy)
			else:
				request = requests.get(url)
			if request.text == "null":
				if print_error is True:
					print(Fore.RED+"STEAM ERROR@"+num+": A lot of requests, retrying with another proxies"+Fore.RESET)
					pp = 0
				pass
			else:
				return request
				break
		except Exception as e:
			if "Max retries exceeded with url" in str(e):
				todisableproxy += 1
				if todisableproxy == 10:
					pp = 1
					if print_error is True:
						print(Style.BRIGHT+Fore.BLACK+' ~ '+Style.DIM+Fore.RED+'Trying request without proxy'+Style.RESET_ALL)
			elif detailed_errors is True and print_error is True:
				print(Style.BRIGHT+Fore.BLACK+' ~ '+Style.DIM+Fore.RED+str(e)+Style.RESET_ALL)
				pp = 0
			pass

def LoopRequest(url, num):
	for q_ in range(999):
		try:
			request = requests.get(url)
			if request.text == "null":
				if print_error is True:
					print(Fore.RED+"STEAM ERROR@"+num+": A lot of requests, retrying with another proxies"+Fore.RESET)
				pass
			else:
				return request
				break
		except Exception as e:
			if detailed_errors is True and print_error is True:
				print(Style.BRIGHT+Fore.BLACK+' ~ '+Style.DIM+Fore.RED+str(e)+Style.RESET_ALL)
			pass

games = []

os.system('cls')

print(Fore.BLUE+"PARSING GAME DATAS."+Fore.RESET)

# GETTING LIST OF GAMES #
for i_ in range(pages):

	page_from += 1

	url = "https://store.steampowered.com/search/?sort_by=Price_ASC&cc=" + str(currency) + "&ignore_preferences=1&force_infinite=1&category1=998%2C994&category2=29%2C22&specials=1&page=" + str(page_from)

	if detalied_actions is True:
		print(Style.BRIGHT+Fore.BLACK+" ~ === Page "+str(page_from)+" === ~ "+Style.RESET_ALL)

	request = requests.get(url)
	
	if '<meta property="og:title" content="Steam Community :: Error">' in request.text:
		if print_error is True:
			print(Fore.RED+"STEAM ERROR@1: A lot of requests, retrying with proxies"+Fore.RESET)
		if using_proxies is True:
			ProxyRequest(url, '1')
		else:
			time.sleep(65)
			LoopRequest(url, '1')


	splitt = str(request.text).split('data-ds-itemkey="App_')
	splitt.pop(0)

	for get in splitt:
		try:
			id = int(re.search('(.*)" data-ds-tagids=', get).group(1))
			name = str(re.search('<span class="title">(.*)</span>', get).group(1))
			price = str(re.search('</strike></span><br>(.*)                    </div>', get).group(1))
			if not "\t" in name:
				if int(games_limit) == len(games) and not int(games_limit) == 0:
					break
				else:
					games += [{"name": str(name), 'id': id, "price": str(price), "cards": []}]
					if detalied_actions is True:
						print(Style.BRIGHT+Fore.BLACK+" ~ Added "+Style.DIM+Fore.YELLOW+name+Style.RESET_ALL)
		except:
			pass


print(Fore.BLUE+"PARSED " + str(len(games)) + " GAMES.\nSAVING CARDS DATA."+Fore.RESET)

# GETTING CARDS FROM GAMES #
for gameid in games:

	time.sleep(sleep_time) # to smally avoid steam requests limitations

	url = "https://steamcommunity.com/market/search?category_753_Game%5B0%5D=tag_app_" + str(gameid['id']) + "&category_753_cardborder%5B0%5D=tag_cardborder_0&&cc=" + str(currency) + "category_753_item_class%5B0%5D=tag_item_class_2&appid=753"

	if detalied_actions is True:
		print(Style.BRIGHT+Fore.BLACK+" ~ === Cards from "+gameid['name']+" === ~ "+Style.RESET_ALL)

	request = requests.get(url)

	if '<meta property="og:title" content="Steam Community :: Error">' in request.text:
		if print_error is True:
			print(Fore.RED+"STEAM ERROR@2: A lot of requests, retrying with proxies"+Fore.RESET)
		if using_proxies is True:
			ProxyRequest(url, '2')
		else:
			time.sleep(65)
			LoopRequest(url, '2')

	splitt = str(request.text).split('https://steamcommunity.com/market/listings/753/')
	splitt.pop(0)

	noproxy = 0
	for data in splitt:

		cardurl = str(re.search('(.*)" id="resultlink_', data).group(1))

		url = 'https://steamcommunity.com/market/priceoverview/?currency='+ str(secondcurrency) +'&appid=753&market_hash_name=' + str(cardurl)
		request = requests.get(url)

		if request.text == 'null':
			if print_error is True:
				print(Fore.RED+"STEAM ERROR@3: A lot of requests"+Fore.RESET)
			if using_proxies is True:
				ProxyRequest(url, '3')
			else:
				time.sleep(65)
				LoopRequest(url, '3')

		carddata = json.loads(request.text)

		cardname = str(re.search('style="color: #;">(.*)</span>', data).group(1))
		
		try:
			price = carddata['median_price']
		except Exception as e:
			if detailed_errors is True and print_error is True:
				print(Style.BRIGHT+Fore.BLACK+' ~ '+Style.DIM+Fore.RED+str(e)+Style.RESET_ALL)
			price = 0
		try:
			quicksell = carddata['lowest_price']
		except Exception as e:
			if detailed_errors is True and print_error is True:
				print(Style.BRIGHT+Fore.BLACK+' ~ '+Style.DIM+Fore.RED+str(e)+Style.RESET_ALL)
			quicksell = 0
		
		gameid["cards"] += [{"name": str(cardname), "price": str(price), "quicksell": str(quicksell)}]
		if detalied_actions is True:
			print(Style.BRIGHT+Fore.BLACK+" ~ Added "+Style.DIM+Fore.YELLOW+cardname+Style.RESET_ALL)

print(Fore.BLUE+"FILTERING GAMES."+Fore.RESET)
# FILTERING GAMES WITH CHEAP CARDS #

text = ''
for game in games:

	game_price = str(game['price']).replace(currency_mark, '').replace(',','.')
	cprice = float(0)
	clprice = float(0)
	times = 0

	for card in game['cards']:

		times += 1

		one = str(card['price']).replace(currency_mark, '')
		one = str(one).replace(',','.')
		two = str(card['quicksell']).replace(currency_mark, '')
		two = str(two).replace(',','.')

		cprice = float(cprice) + float(one)
		clprice = float(clprice) + float(two)

	times = len(game['cards']) / 2
	times = int(round(times+0.1))
	acprice = cprice / len(game['cards'])
	aclprice = clprice / len(game['cards'])

	cprice = float(acprice) * float(times)
	clprice = float(aclprice) * float(times)

	if float(game_price) < cprice or float(game_price) < clprice:
		text += 'Good game: '+game['name']+' | '+str(game['id'])+'\nPrice: '+game['price']+'\nCard will drop: '+str(times)+' times'+'\nCards approximate cost: '+str(cprice)+'/'+str(acprice)+' '+currency_mark+'\nCards approximate cost(quicksell): '+str(clprice)+'/'+str(aclprice)+' '+currency_mark+'\n\n'
		print(Fore.RED+'Good game: '+game['name']+' | '+str(game['id'])+'\nPrice: '+game['price']+'\nCard will drop: '+str(times)+'\nCards approximate cost: '+str(cprice)+'/'+str(acprice)+' '+currency_mark+'\nCards approximate cost(quicksell): '+str(clprice)+'/'+str(aclprice)+' '+currency_mark+"\n\n"+Fore.RESET)
	else:
		text += 'Bad game: '+game['name']+' | '+str(game['id'])+'\nPrice: '+game['price']+'\nCard will drop: '+str(times)+' times'+'\nCards approximate cost: '+str(cprice)+'/'+str(acprice)+' '+currency_mark+'\nCards approximate cost(quicksell): '+str(clprice)+'/'+str(aclprice)+' '+currency_mark+'\n\n'
		print(Fore.RED+'Bad game: '+game['name']+' | '+str(game['id'])+'\nPrice: '+game['price']+'\nCard will drop: '+str(times)+'\nCards approximate cost: '+str(cprice)+'/'+str(acprice)+' '+currency_mark+'\nCards approximate cost(quicksell): '+str(clprice)+'/'+str(aclprice)+' '+currency_mark+"\n\n"+Fore.RESET)

open('last parsed games.txt', 'w', encoding = "utf-8").write(text)
