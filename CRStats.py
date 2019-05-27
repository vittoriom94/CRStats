import requests
import json
import os
from os import path
import datetime
import re

# common rimane uguale
# rara +2
# epica +5
# legg +8

headers = {
  'auth': "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MjUyMywiaWRlbiI6IjE5MDE1MDQyNDk0OTU1NTIwMCIsIm1kIjp7fSwidHMiOjE1NTU1ODgyMTkyNDh9.qxb6N28DmMZAFP4HtU9sI-G7YPFt55jYt6P4ZSH5P0w"
}
def get_data_and_save():
  clantag = "YVRG0PQ"
  data = dict()
  data["players"] =get_crstats(clantag)

  now = datetime.datetime.now()
  data["date"] = now.strftime("%d-%m-%Y")
  if path.exists("latest.json"):
    if path.exists("old.json"):
      os.remove("old.json")
    os.rename("latest.json","old.json")

  with open("latest.json","w") as file:
    file.write(json.dumps(data,indent=2))

def get_crstats(clantag):
  num_cards = get_number_of_cards()
  data = request_clan_data(clantag)
  print(json.dumps(data,indent=2))
  players = list()
  for member in data["members"]:
    players.append(member["tag"])
  print("\n\n --- players -- \n\n")
  print(json.dumps(players,indent=2))
  # print("\n\n --- ower -- \n\n")
  playerdata = request_player_data(players)
  print(json.dumps(playerdata,indent=2))

  player_cards = list()
  for player in playerdata:
    player_cards.append( get_player_cards(player,num_cards))

  print(json.dumps(player_cards, indent=2))
  return player_cards


def get_number_of_cards():
  url = "https://api.royaleapi.com/constants"
  response = requests.request("GET", url, headers=headers)

  cards = response.json()

  return len(cards["cards"])

def get_player_cards(player,tot):
  data = dict()
  data["name"] = player["name"]
  data["tag"] = player["tag"]
  data["9"] = 0
  data["10"] = 0
  data["11"] = 0
  data["12"] = 0

  for card in player["cards"]:
    level = fix_level(card)
    if(level >= 9):
      data["9"] = data["9"]+1
      if (level >= 10):
        data["10"] = data["10"] + 1
        if (level >= 11):
          data["11"] = data["11"] + 1
          if (level >= 12):
            data["12"] = data["12"] + 1
  data["9"] = int(data["9"] * 100 / tot)
  data["10"] = int(data["10"] * 100 / tot)
  data["11"] = int(data["11"] * 100 / tot)
  data["12"] = int(data["12"] * 100 / tot)
  return data

def fix_level(card):
  rarity = card["rarity"]
  if rarity == "Common":
    plus = 0
  elif rarity == "Rare":
    plus = 2
  elif rarity == "Epic":
    plus = 5
  else:
    plus = 8
  return card["level"] + plus

def request_clan_data(clantag):
  url = "https://api.royaleapi.com/clan/" + clantag + "?keys=members"
  response = requests.request("GET", url, headers=headers)
  return response.json()

def request_player_data(playertag):
  data = list()

  for tag in playertag:
    url = "https://api.royaleapi.com/player/"+tag+"?keys=name,tag,cards"
    response = requests.request("GET", url, headers=headers)
    data.append(response.json())

  return data





def convert_data_to_html():
  if not path.exists("old.json"):
    print("ERROR: Execute the program again to generate old data.")
    return
  with open("old.json", "r") as file:
    old_data = json.loads(file.read())
  with open("latest.json", "r") as file:
    new_data = json.loads(file.read())
  # print(json.dumps(new_data, indent=2))

  html = create_header(old_data["date"],new_data["date"])
  html+= populate_table(old_data,new_data)
  html+=create_footer()

  with open("table.html","w") as file:
    file.write(html)

def create_header(old_date,new_date):
  html = """<html><head><link rel="stylesheet" type="text/css" href="style.css"></head><body><table class='crtable'>
<tr><td>Players</td><td colspan = '4'>""" + new_date +"</td><td class='empty'>    </td><td colspan = '4'>" + old_date + "</td><td class='empty'>    </td><td colspan = '4'>Improvement</td><td class='empty'>    </td></tr>"
  html+="<tr class='Levels'><td>Levels</td><td>12+</td><td>11+</td><td>10+</td><td>9+</td>"
  html+="<td></td><td>12+</td><td>11+</td><td>10+</td><td>9+</td>"
  html += "<td></td><td>12+</td><td>11+</td><td>10+</td><td>9+</td><td></td></tr>"
  return html

def populate_table(old_data,new_data):
  empty = dict()
  empty["9"] = 0
  empty["10"] = 0
  empty["11"] = 0
  empty["12"] = 0
  html = ""
  for new_player_data in sorted(new_data["players"], key = lambda v: re.sub(r'[^\w]','',v["name"].lower())):
    empty["name"] = new_player_data["name"]
    old_player_data = next((item for item in old_data["players"] if item["name"] == new_player_data["name"]), empty)
    row = "<tr>"
    row+="<tr><td>" +new_player_data["name"]+"</td><td>"+format_level(new_player_data["12"])+"</td><td>"+format_level(new_player_data["11"])+"</td><td>"+format_level(new_player_data["10"])+"</td><td>"+format_level(new_player_data["9"])+"</td>"
    row+="<td></td><td>"+format_level(old_player_data["12"])+"</td><td>"+format_level(old_player_data["11"])+"</td><td>"+format_level(old_player_data["10"])+"</td><td>"+format_level(old_player_data["9"])+"</td>"

    row+="<td></td><td>"+ get_difference(old_player_data["12"],new_player_data["12"])+"</td><td>"+ get_difference(old_player_data["11"],new_player_data["11"])+"</td><td>"+ get_difference(old_player_data["10"],new_player_data["10"])+"</td><td>"+ get_difference(old_player_data["9"],new_player_data["9"])+"</td><td>    </td></tr>"
    html+=row

  return html

def format_level(level):
  if level < 5:
    color =  "red"
  elif level < 10:
    color = "orange"
  else:
    color = "black"

  string = "<p style='color:" + color + ";'>"+str(level)+"%</p>"
  return string

def get_difference(old, new):
  diff = new-old
  return str(diff)+"%"

def create_footer():
  html = "</table></body></html>"
  return html


if __name__ == "__main__":

  get_data_and_save()
  convert_data_to_html()


