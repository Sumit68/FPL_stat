import requests
# import json

# with open('raw.json') as f:
#     jsondata = json.load(f)

# #print(jsondata)
# possession = jsondata['statistics']['groups']
# print(possession)


url = "https://api.sofascore.com/api/v1/event/10385440/statistics"

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

response = requests.request("GET", url, data=payload, headers=headers)

print(response.text)