

# url = "https://api.sofascore.com/api/v1/sport/football/events/live"

import pickle
import requests
import xgboost as xgb
import pandas as pd

# import json

# with open('raw.json') as f:
#     jsondata = json.load(f)

# #print(jsondata)
# possession = jsondata['statistics']['groups']
# print(possession)


#url = "https://api.sofascore.com/api/v1/event/10385440/statistics"

payload = ""
headers = {
    "authority": "api.sofascore.com",
    "accept": "*/*",
    "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
    "cache-control": "max-age=0",
    "if-none-match": "W/\"cf18cf472d\"",
    "origin": "https://www.sofascore.com",
    "referer": "https://www.sofascore.com/",
    "sec-ch-ua": "Not_A Brand;v=99, Google Chrome;v=109, Chromium;v=109",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"macOS\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
}



#print(response.text)
away_dict = {'Arsenal': 1270, 'Man City': 1370, 'Man United': 1220, 'Newcastle': 1210, 'Tottenham': 1230,'Leeds': 1100,'Brentford': 1130,'Everton': 1100,'Burnley': 1060,'Chelsea': 1220,'Crystal Palace': 1140,'Brighton': 1160,'Southampton': 1100,'Leicester': 1130,'Wolves': 1100,'Watford': 1060,'Aston Villa': 1100,'Norwich': 1060,'Liverpool': 1350,'West Ham': 1120}
home_dict = {'Arsenal': 1220, 'Man City': 1350, 'Man United': 1150, 'Newcastle': 1160, 'Tottenham': 1190,'Leeds': 1100,'Brentford': 1100,'Everton': 1080,'Burnley': 1050,'Chelsea': 1200,'Crystal Palace': 1100,'Brighton': 1150,'Southampton': 1090,'Leicester': 1130,'Wolves': 1100,'Watford': 1050,'Aston Villa': 1090,'Norwich': 1050,'Liverpool': 1300,'West Ham': 1100}
# with open("FPL_stat_model.pickle", 'rb') as f:
#         model = pickle.load(f)

model2 = xgb.XGBClassifier()
test1=[[1100,1100,0,2,0,1,0,1]]
test2= pd.DataFrame(test1,columns=['HomeTeam','AwayTeam','FTHG','FTAG','HST','AST','HC','AC'],dtype=float)


model2.load_model("model_sklearn.txt")
print(model2.predict(test2))

#print("Predicition: ",model2.predict_proba(test2))

import json
with open('matchid.json') as f:
    jsondata = json.load(f)

def getmatchid():

    matchids = []
    Home = []
    Away = []
    Homescore = []
    Awayscore = []
    print(len(jsondata['events']))
    for i in range(len(jsondata['events'])):
    #print(i)
        if (jsondata['events'][i]['tournament']['name'] == 'Premier League' and jsondata['events'][i]['tournament']['category']['name'] == 'England'):
            matchid = jsondata['events'][i]['id']
            Awayteam = jsondata['events'][i]['awayTeam']['name']
            Hometeam = jsondata['events'][i]['homeTeam']['name']
            Homescores = jsondata['events'][i]['homeScore']['current']
            Awayscores = jsondata['events'][i]['awayScore']['current']
            matchids.append(matchid)
            Home.append(Hometeam)
            Away.append(Awayteam)
            Homescore.append(Homescores)
            Awayscore.append(Awayscores)

    return matchids, Home, Away, Homescore, Awayscore

matchids, Home, Away, Homescore, Awayscore = getmatchid()

print(Homescore)
print(Awayscore)

def getstats(matchids, Home, Away, Homescore, Awayscore):
    Corners_home = []
    Corners_away = []
    Shots_home = []
    Shots_away = []
    

    for i in matchids:
        url = "https://api.sofascore.com/api/v1/event/"+str(i)+"/statistics"
        response = requests.request("GET", url, data=payload, headers=headers)
        json_data = json.loads(response.text)
        shots_on_target_home, shots_on_target_away, corner_kicks_home, corner_kicks_away = [item.get(side, '') for group in json_data['statistics'][0]['groups'] for item in group['statisticsItems'] if item['name'] in ['Shots on target', 'Corner kicks'] for side in ['home', 'away']]

        Corners_home.append(corner_kicks_home)
        Corners_away.append(corner_kicks_away)
        Shots_home.append(shots_on_target_home)
        Shots_away.append(shots_on_target_away)
        print([home_dict[Home[i]],away_dict[Away[i]],Homescore[i],Awayscore[i],Shots_home[i],Shots_away[i],Corners_home[i],Corners_away[i]])
        test1=pd.DataFrame([[home_dict[Home[i]],away_dict[Away[i]],Homescore[i],Awayscore[i],Shots_home[i],Shots_away[i],Corners_home[i],Corners_away[i]]])

        print(model2.predict(test1))


getstats(matchids, Home, Away, Homescore, Awayscore)

#print(jsondata)
