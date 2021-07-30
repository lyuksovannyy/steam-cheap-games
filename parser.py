import requests
import colorama

import re
import os
import time
import random
import json

from colorama import Fore, Style

colorama.init()

detalied_actions = True 		# print more information
print_error = True 				# print errors
detailed_errors = False 		# print more info about errors, must be on "print_error"

log_actions = True				# will write all actions in file (doesn't log filtered games)
								
currency = "ru" 				# recommended currency for that is Russian Ruble or Argentina Peso, by that you can buy games for lower price
secondcurrency = 5 				# https://stackoverflow.com/a/65653682 
currency_mark = "pуб."			
pages = 3 						# how many pages will parsed
page_from = 0 					# starting from page
games_limit = 150 				# how many games you need to parse | 0 - until pages end.
sleep_time = 0.3 				# time to next card info get
								
using_proxies = True			
only_proxies = False 			# use this of you have good proxies or process will so slowly, for example ipvanish proxies (so good)
IpVanish_using = False			
# IPVanish creds #				
if IpVanish_using is True: 		# creds in https://account.ipvanish.com/index.php?t=SOCKS5%20Proxy
	ipvanish_hosts = ['syd.socks.ipvanish.com','gig.socks.ipvanish.com','tor.socks.ipvanish.com','par.socks.ipvanish.com','fra.socks.ipvanish.com','lin.socks.ipvanish.com','nrt.socks.ipvanish.com','ams.socks.ipvanish.com','waw.socks.ipvanish.com','lis.socks.ipvanish.com','sin.socks.ipvanish.com','mad.socks.ipvanish.com','sto.socks.ipvanish.com','lon.socks.ipvanish.com','iad.socks.ipvanish.com','atl.socks.ipvanish.com','bos.socks.ipvanish.com','clt.socks.ipvanish.com','chi.socks.ipvanish.com','dal.socks.ipvanish.com','den.socks.ipvanish.com','lax.socks.ipvanish.com','mia.socks.ipvanish.com','msy.socks.ipvanish.com','nyc.socks.ipvanish.com','phx.socks.ipvanish.com','sea.socks.ipvanish.com']
	ipvanish_port = int('port')
	ipvanish_username = "username"
	ipvanish_pass = "password"


# SCRIPT START #

def LogFile(content):
	if log_actions is True:
		try:
			read = open('logFile.txt', 'r', encoding = "utf-8").read()
		except:
			read = ""
		open('logFile.txt', 'w', encoding = "utf-8").write(read+content)

def ApplyProxy():
	if savedproxies == []:
		if IpVanish_using is True: 		# ipvanish proxies (private proxies)
			for host in ipvanish_hosts:
				savedproxies.append(ipvanish_username+':'+ipvanish_pass+'@'+host+':'+str(ipvanish_port))
		else: 							# public proxies
			proxy_service = "https://proxylist.geonode.com/api/proxy-list?limit=200&page=1&sort_by=speed&sort_type=asc&protocols=socks5"
			proxylist = requests.get(proxy_service)
			proxies = json.loads(proxylist.text)
			for proxy in proxies['data']:
				savedproxies.append(proxy['ip']+':'+proxy['port'])
	proxy = str(savedproxies[0])
	savedproxies.pop(0)
	useproxy = str('socks5://'+str(proxy))
	proxy = dict(http=useproxy, https=useproxy)
	return proxy

def LoopRequest(url, num, err_str):
	if using_proxies is False:
		for q_ in range(999):
			try:
				request = requests.get(url)
				if err_str in request.text:
					if print_error is True:
						print(Fore.RED+"STEAM ERROR@"+num+": A lot of requests, retrying in 1 minute"+Fore.RESET)
					LogFile("STEAM ERROR@"+num+": A lot of requests, retrying in 1 minute"+'\n\n')
					time.sleep(60)
					pass
				else:
					return request
					break
			except Exception as e:
				if detailed_errors is True and print_error is True:
					print(Style.BRIGHT+Fore.BLACK+' ~ '+Style.DIM+Fore.RED+str(e)+Style.RESET_ALL)
				LogFile(' ~ '+str(e)+'\n\n')
				pass
	elif using_proxies is True:
		pp = 0
		todisableproxy = 0
		for g_ in range(999):
			proxy = ApplyProxy()
			try:
				if pp == 0:
					request = requests.get(url, proxies = proxy, timeout = 5)
				else:
					request = requests.get(url)
				if err_str in request.text:
					if print_error is True:
						print(Fore.RED+"STEAM ERROR@"+num+": A lot of requests, retrying with another proxies"+Fore.RESET)
					LogFile("STEAM ERROR@"+num+": A lot of requests, retrying with another proxies"+'\n\n')
					pp = 0
					pass
				else:
					return request
					break
			except Exception as e:
				if "Max retries exceeded with url" in str(e):
					if not only_proxies is True:
						todisableproxy += 1
						if todisableproxy == 10:
							pp = 1
							if print_error is True:
								print(Style.BRIGHT+Fore.BLACK+' ~ '+Style.DIM+Fore.RED+'Trying request without proxy'+Style.RESET_ALL)
							LogFile(" ~ Trying request without proxy"+'\n\n')
				elif detailed_errors is True and print_error is True:
					print(Style.BRIGHT+Fore.BLACK+' ~ '+Style.DIM+Fore.RED+str(e)+Style.RESET_ALL)
				LogFile(' ~ '+str(e)+'\n\n')
				pp = 0
				pass

games = []
savedproxies = []

os.system('cls')

print(Fore.BLUE+"PARSING GAME DATAS."+Fore.RESET)
LogFile("PARSING GAME DATAS.\n\n")

# GETTING LIST OF GAMES #
for i_ in range(pages):

	page_from += 1
	os.system('title Checking '+str(page_from)+' page')
	url = "https://store.steampowered.com/search/?sort_by=Price_ASC&cc=" + str(currency) + "&ignore_preferences=1&force_infinite=1&category1=998%2C994&category2=29%2C22&specials=1&page=" + str(page_from)

	if detalied_actions is True:
		print(Style.BRIGHT+Fore.BLACK+" ~ === Page "+str(page_from)+" === ~ "+Style.RESET_ALL)
	LogFile(" ~ === Page "+str(page_from)+" === ~ \n\n")

	request = LoopRequest(url, '1', '<meta property="og:title" content="Steam Community :: Error">')
	
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
					LogFile(" ~ Added "+name+'\n\n')
		except:
			pass


print(Fore.BLUE+"PARSED " + str(len(games)) + " GAMES.\nSAVING CARDS DATA."+Fore.RESET)
LogFile("PARSED " + str(len(games)) + " GAMES.\nSAVING CARDS DATA.\n\n")

# GETTING CARDS FROM GAMES #
count = 0
for gameid in games:

	count += 1
	os.system('title Checking game: '+gameid['name'])
	time.sleep(sleep_time) # to smally avoid steam requests limitations

	url = "https://steamcommunity.com/market/search?category_753_Game%5B0%5D=tag_app_" + str(gameid['id']) + "&category_753_cardborder%5B0%5D=tag_cardborder_0&&cc=" + str(currency) + "category_753_item_class%5B0%5D=tag_item_class_2&appid=753"

	if detalied_actions is True:
		print(Style.BRIGHT+Fore.BLACK+" ~ === Cards from "+Style.DIM+Fore.YELLOW+gameid['name']+Style.BRIGHT+Fore.BLACK+" === ~ "+Style.RESET_ALL)
	LogFile(" ~ === Cards from "+gameid['name']+" ("+str(count)+") === ~ \n\n")

	request = LoopRequest(url, '2', '<meta property="og:title" content="Steam Community :: Error">')

	splitt = str(request.text).split('https://steamcommunity.com/market/listings/753/')
	splitt.pop(0)

	noproxy = 0
	for data in splitt:

		cardurl = str(re.search('(.*)" id="resultlink_', data).group(1))

		url = 'https://steamcommunity.com/market/priceoverview/?currency='+ str(secondcurrency) +'&appid=753&market_hash_name=' + str(cardurl)
		request = LoopRequest(url, '3', 'null')

		carddata = json.loads(request.text)

		cardname = str(re.search('style="color: #;">(.*)</span>', data).group(1))
		
		try:
			price = carddata['median_price']
		except Exception as e:
			if detailed_errors is True and print_error is True:
				print(Style.BRIGHT+Fore.BLACK+' ~ '+Style.DIM+Fore.RED+str(e)+Style.RESET_ALL)
			LogFile(' ~ '+str(e)+'\n\n')
			price = 0
		try:
			quicksell = carddata['lowest_price']
		except Exception as e:
			if detailed_errors is True and print_error is True:
				print(Style.BRIGHT+Fore.BLACK+' ~ '+Style.DIM+Fore.RED+str(e)+Style.RESET_ALL)
			LogFile(' ~ '+str(e)+'\n\n')
			quicksell = 0
		
		gameid["cards"] += [{"name": str(cardname), "price": str(price), "quicksell": str(quicksell)}]
		if detalied_actions is True:
			print(Style.BRIGHT+Fore.BLACK+" ~ Added "+Style.DIM+Fore.YELLOW+cardname+Style.RESET_ALL)
		LogFile(" ~ Added "+cardname+'\n\n')

print(Fore.BLUE+"FILTERING GAMES."+Fore.RESET)
LogFile("FILTERING GAMES.\n\n")
# FILTERING GAMES WITH CHEAP CARDS #
text = ''
count = 0
for game in games:

	count += 1
	os.system('title Filtering '+str(page_from)+' game')

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
	try:
		times = len(game['cards']) / 2
		times = times + 0.3
		times = round(times)
	except:
		times = 'null'
	try:
		acprice = cprice / len(game['cards'])
		aclprice = clprice / len(game['cards'])
	except:
		acprice = 'null'
		aclprice = 'null'

	cprice = float(acprice) * float(times)
	clprice = float(aclprice) * float(times)

	if float(game_price) < cprice or float(game_price) < clprice:
		text += 'Good game: '+game['name']+' | '+str(game['id'])+'\nPrice: '+game['price']+'\nCard will drop: '+str(times)+' times'+'\nCards approximate cost: '+str(cprice)+'/'+str(acprice)+' '+currency_mark+'\nCards approximate cost(quicksell): '+str(clprice)+'/'+str(aclprice)+' '+currency_mark+'\n\n'
		print(Fore.RED+'Good game: '+game['name']+' | '+str(game['id'])+'\nPrice: '+game['price']+'\nCard will drop: '+str(times)+'\nCards approximate cost: '+str(cprice)+'/'+str(acprice)+' '+currency_mark+'\nCards approximate cost(quicksell): '+str(clprice)+'/'+str(aclprice)+' '+currency_mark+"\n\n"+Fore.RESET)
	else:
		text += 'Bad game: '+game['name']+' | '+str(game['id'])+'\nPrice: '+game['price']+'\nCard will drop: '+str(times)+' times'+'\nCards approximate cost: '+str(cprice)+'/'+str(acprice)+' '+currency_mark+'\nCards approximate cost(quicksell): '+str(clprice)+'/'+str(aclprice)+' '+currency_mark+'\n\n'
		print(Fore.RED+'Bad game: '+game['name']+' | '+str(game['id'])+'\nPrice: '+game['price']+'\nCard will drop: '+str(times)+'\nCards approximate cost: '+str(cprice)+'/'+str(acprice)+' '+currency_mark+'\nCards approximate cost(quicksell): '+str(clprice)+'/'+str(aclprice)+' '+currency_mark+"\n\n"+Fore.RESET)


text = "===END=="+str(time.time())+"=DATE==="
line = "=" * int(len(text))
LogFile("\n"+line+"\n"+text+"\n"+line+"\n\n")
open('last parsed games.txt', 'w', encoding = "utf-8").write(text)
