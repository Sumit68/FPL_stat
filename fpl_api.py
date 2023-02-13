import pandas as pd
from prettytable import PrettyTable
from fpl import FPL
import aiohttp
import asyncio
from colorama import Fore, init
from understat import Understat
from nltk.corpus import stopwords
import numpy as np
from nltk.tag import StanfordNERTagger
from nltk.tokenize import word_tokenize

import http.client

import json


st = StanfordNERTagger('/Users/sumit/Downloads/stanford-ner-2020-11-17/classifiers/english.all.3class.distsim.crf.ser.gz',
					   '/Users/sumit/Downloads/stanford-ner-2020-11-17/stanford-ner.jar',
					   encoding='utf-8')


from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('all-MiniLM-L6-v2')

from nltk import pos_tag
from nltk import RegexpParser
 
from quart import Quart, render_template, redirect, url_for, request

app = Quart(__name__)

@app.route("/")
async def index():
	return await render_template('index.html')

@app.route("/standings")
async def standings():
	return await render_template('standings.html')

@app.route("/fixtures")
async def fixtures():
	return await render_template('fixtures.html')


# @app.route("/goals")
# async def goals(x):
# 	return await render_template('index.html', value = x)

@app.route('/', methods=['POST'])
async def getdata():
	variable = (await request.form)["search"]
	await nlpprocess(variable)
	# if (variable == 'goals'):
	# 	names, goals, teams = await getmostgoalscored()
		#return x
		# print(x,"*********************************")
	#return await render_template('result.html', value = names, value1 = goals, value2 = teams)

	# else:
	# 	x = await getplayer(variable)
	# 	return x
	return variable

async def getplayer(name):
	session = aiohttp.ClientSession()
	fpl = FPL(session)
	df = pd.read_csv("fpl_ids.csv")
	fpl_id = df.loc[df['web_name']==name,'22-23'].values[0]
	player = await fpl.get_player(fpl_id )
	print(dir(player))
	player_detail = [player.web_name,  player.total_points, player.points_per_game, player.form]
	return player_detail
	await session.close()


async def getmostgoalscored():
	session = aiohttp.ClientSession()
	fpl = FPL(session)
	players = await fpl.get_players()
	goals = []
	teams = []
	names = []
	top_performers = sorted(
	players, key=lambda x: x.goals_scored, reverse=True)
	#print(top_performers[0].code)
	player_table = PrettyTable(["Player", "£", "Team", "G", "Total Points"])
	for player in top_performers[:10]:
		goals.append(player.goals_scored)
		team = await fpl.get_team(player.team)
		teams.append(str(team))
		names.append(player.web_name)

		
		# player_table.add_row([player.web_name, f"£{player.now_cost / 10}",team, goals, player.total_points])

	#print(player_table)
	#print(names)
	#x = player_table.get_string()
	#return top_performers
	return names, goals, teams
	await session.close()

async def getmostassistscored():
	session = aiohttp.ClientSession()
	fpl = FPL(session)
	players = await fpl.get_players()
	assists = []
	teams = []
	names = []
	top_performers = sorted(
	players, key=lambda x: x.assists, reverse=True)
	#print(top_performers[0].code)
	player_table = PrettyTable(["Player", "£", "Team", "A", "Total Points"])
	for player in top_performers[:10]:
		assists.append(player.assists)
		team = await fpl.get_team(player.team)
		teams.append(str(team))
		names.append(player.web_name)

		
		# player_table.add_row([player.web_name, f"£{player.now_cost / 10}",team, goals, player.total_points])

	#print(player_table)
	#print(names)
	#x = player_table.get_string()
	#return top_performers
	return names, assists, teams
	await session.close()

async def alternatefdr():
	async with aiohttp.ClientSession() as session:
		fpl = FPL(session)
		fdr = await fpl.FDR()

	fdr_table = PrettyTable()
	fdr_table.field_names = [
		"Team", "All (H)", "All (A)", "GK (H)", "GK (A)", "DEF (H)", "DEF (A)",
		"MID (H)", "MID (A)", "FWD (H)", "FWD (A)"]
 
	for team, positions in fdr.items():
		row = [team]
		for difficulties in positions.values():
			for location in ["H", "A"]:
				if difficulties[location] == 5.0:
					row.append(Fore.RED + "5.0" + Fore.RESET)
				elif difficulties[location] == 1.0:
					row.append(Fore.GREEN + "1.0" + Fore.RESET)
				else:
					row.append(f"{difficulties[location]:.2f}")

		fdr_table.add_row(row)

	fdr_table.align["Team"] = "l"
	print(fdr_table)

async def playerrecommendation():
	session = aiohttp.ClientSession()
	understat = Understat(session)
	fpl = FPL(session)
	players = await fpl.get_players()
	#data = await understat.get_league_players("epl", 2022)
	#print(data[0])
	for player in data:
		weight = 0
		weight = (0.6 * (float(player['xG']) + float(player['xA']))) + (-0.1*(float(player['yellow_cards']) + float(player['red_cards'])) + (0.2*(float(player['npxG']))))
		#print(weight)
		player.update({"weight": weight})
		#print(player)
	
	#print(data[0])
	top_recommendation = sorted(data, key=lambda x: x['weight'], reverse = True)
	print("Top Forwards or Midfielders you can buy.")
	for player in top_recommendation[:10]:
		print(player['player_name'])

	return top_recommendation
		
async def recommenddefenders():
	session = aiohttp.ClientSession()
	understat = Understat(session)
	fpl = FPL(session)
	df = pd.read_csv("Master.csv")
	players = await fpl.get_players()
	#data = await understat.get_league_players("epl", 2022)
	#print(data)
	for player in players:
		
		weight = 0
		try:
			if (float(player.minutes)/float(await player.games_played) >= 60) and (int(player.element_type) == 2):
				#print(player.form, player.yellow_cards, player.red_cards, player.clean_sheets, player.points_per_game, player.ict_index_rank)
				weight = (0.5 * float(player.form) -0.1*(float(player.yellow_cards) + float(player.red_cards)) + 0.3*float(player.clean_sheets) + 0.2*float(player.points_per_game) - 0.01*float(player.ict_index_rank))
			else:
				weight = -100
		except ZeroDivisionError:
			weight = -100
		setattr(player, 'weight', weight)
		
	top_recommendation = sorted(players, key=lambda x: x.weight, reverse = True)
	print("Top Defenders you can buy.")
	for player in top_recommendation[:10]:
		print(player.web_name)

async def playerrecommendation2():
	session = aiohttp.ClientSession()
	understat = Understat(session)
	fpl = FPL(session)
	players = await fpl.get_players()
	#data = await understat.get_league_players("epl", 2022)
	#print(data[0])
	for player in players:
		weight = 0
		weight = (0.6 * (float(player.expected_goals) + float(player.expected_assists))) + (-0.1*(float(player.yellow_cards) + float(player.red_cards)))
		#print(weight)
		#player.update({"weight": weight})
		setattr(player, 'weight', weight)
		#print(player)
	
	#print(data[0])
	top_recommendation = sorted(players, key=lambda x: x.weight, reverse = True)
	print("Top Forwards or Midfielders you can buy.")
	for player in top_recommendation[:10]:
		print(player.web_name)

	return top_recommendation


async def playercomparison(name1, name2):
	session = aiohttp.ClientSession()
	fpl = FPL(session)
	df = pd.read_csv("fpl_ids.csv")
	fpl_id_1 = df.loc[df['web_name']==name1,'22-23'].values[0]
	fpl_id_2 = df.loc[df['web_name']==name2,'22-23'].values[0]
	player_1 = await fpl.get_player(fpl_id_1)
	player_2 = await fpl.get_player(fpl_id_2)
	#print(player_1.element_type)
	#print(dir(player_1))
	vapm1 = await player_1.vapm
	vapm2 = await player_2.vapm
	weight_1 = 0
	weight_1 = (0.2*(float(player_1.form)) + 0.3*(float(vapm1)) + 0.5*(float(player_1.ep_next)))
	#print(weight_1)
	weight_2 = 0
	weight_2 = (0.2*float(player_2.form) + 0.3*float(vapm2) + 0.5*float(player_2.ep_next))
	#print(weight_2)

	if (weight_1 > weight_2):
		print("FPLstat suggests "+ player_1.web_name)
	else:
		print("FPLstat suggests "+ player_2.web_name)


async def nlpprocess(variable):
	
	variable = variable.split()

	stop_words = {'Who', 'Which', 'When', 'What', 'Why', 'Where', 'Is'}

	#text = 'Which is better Kane or Haaland?'

	#tokenized_text = word_tokenize(text)
	ner_tag = st.tag(variable)
	print(ner_tag)


	#print(classified_text)

	#filtered_variable =  []
	# for i in variable:
	# 	if i not in stop_words:
	# 		filtered_variable.append(i)

	# tokens_tag = pos_tag(filtered_variable)
	# print(tokens_tag)

	count = 0
	names = []
	for i in ner_tag:
		if i[1] == 'PERSON':
			names.append(i[0])
			count = count + 1

	if count == 2:
		player1 = names[0]
		player2 = names[1]
		await playercomparison(player1,player2)
	elif count == 1:
		player_detail = await getplayer(names[0])
		print(player_detail)
	else:
		sentences1 = " ".join(variable)
		print(sentences1)

		sentences2 = ['Who scored most goals?',
				  'Which forward player to buy in next gameweek?',
				  'Which defender player to buy in next gameweek?',
				  'Who scored most assists?',
				  'Livescore livestats'
				  ]

		embeddings1 = model.encode(sentences1, convert_to_tensor=True)
		embeddings2 = model.encode(sentences2, convert_to_tensor=True)

		cosine_scores = util.cos_sim(embeddings1, embeddings2)

		x = np.argmax(cosine_scores[0])

		if x == 0:
			names, goals, teams = await getmostgoalscored()
			print(names, goals, teams)
			return await render_template('result.html', value = names, value1 = goals, value2 = teams)

		if x == 1:
			top_players = await playerrecommendation2()

		if x == 2:
			await recommenddefenders()
		if x == 3:
			names, assists, teams = await getmostassistscored()
			print(names, assists, teams)
			#await getmostassistscored()
		if x == 4:
			fixture_ids = getfixtureid()
			predictions(fixture_ids)

		

		print(cosine_scores[0])

def getfixtureid():
	conn = http.client.HTTPSConnection("api-football-v1.p.rapidapi.com")

	headers = {
		'Content-type': 'application/json',
    	'X-RapidAPI-Key': "aa611c9650mshd731dec79f3ef88p15d758jsn926e4b339d85",
    	'X-RapidAPI-Host': "api-football-v1.p.rapidapi.com"
    	}

	conn.request("GET", "/v3/fixtures?live=39-39&season=2022", headers=headers)

	res = conn.getresponse()
	data = res.read()
	#print(type(res))
	#print(type(data))
	#print(type(data.decode("utf-8")

	f = data.decode("utf-8")
	print(f)

	data1 = json.loads(f)
	fixture_id = []
	for i in data1['response']:
		fixture_id.append(i['fixture']['id'])

	return fixture_id


def predictions(fixture_id):
	for i in fixture_id:
		print(type(i))
		conn = http.client.HTTPSConnection("api-football-v1.p.rapidapi.com")

		headers = {
			'Content-type': 'application/json',
    		'X-RapidAPI-Key': "aa611c9650mshd731dec79f3ef88p15d758jsn926e4b339d85",
    		'X-RapidAPI-Host': "api-football-v1.p.rapidapi.com"
    		}
		conn.request("GET", "/v3/predictions?fixture="+str(i), headers=headers)

		res_pred = conn.getresponse()
		data_pred = res_pred.read()
		data_f = data_pred.decode("utf-8")

		data_pred = json.loads(data_f)

		for i in data_pred['response']:
			print("Chance of for "+ str(i['teams']['home']['name']) + " " + str(i['predictions']['percent']['home']))
			print("Chance of for "+ str(i['teams']['away']['name']) + " " + str(i['predictions']['percent']['away']))
			print("Chance of for Draw" + " "+str(i['predictions']['percent']['draw']))

		

	


# def jsonpreprocess():
# 	f = open('fixtures_14Jan.json')
# 	data = json.load(f)
# 	for i in data['response']:
# 		print(i['fixture']['id'])

	

#jsonpreprocess()
# fixture_ids = getfixtureid()
# predictions(fixture_ids)
#asyncio.run(getplayer('Haaland'))
#asyncio.run(getmostgoalscored())

#asyncio.run(playerrecommendation2())
#asyncio.run(alternatefdr())

#asyncio.run(recommenddefenders())
#asyncio.run(playercomparison('Haaland','Kane'))

if __name__ == "__main__":
	app.run(host="127.0.0.1", port=8080, debug=True)



