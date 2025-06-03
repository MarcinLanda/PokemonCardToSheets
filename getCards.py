import copy
import json
import requests
import cv2 
import numpy as np 
import urllib.request
import os.path
import matplotlib.pyplot as plt
from matplotlib.backend_bases import MouseButton
from pokemontcgsdk import RestClient 
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow

#import gspread
#from oauth2client.client import OAuth2WebServerFlow
#from oauth2client.file import Storage
#from oauth2client.service_account import ServiceAccountCredentials

APIKEY = '28722abd-8d37-4293-9845-66a4c27ca326'
keys = ['name', 'images', 'set', 'number'] #keys that will be filtered out in query
updateWant = False
newCards = []
notInDataset = [122, 245, 249, 923, range(1011, 1025)]
x = y = z = 0

if(updateWant == False):
    cardList = newCards
else:
    cardList = range(1, 1026) #92, 104, 115, 132? # Finish Want Cards

# With a url, turn the url into a viable image to display with cv2 and matplotlib
def urlToImage(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
        image_data = response.read()
    image_array = np.asarray(bytearray(image_data), dtype=np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    return image

#Update the google sheet with the new card
def updateSheets(n, card):
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    sheet_id = '1HNb0SO4lkEgw9UvZ-fPevp60UQ1O5GaltV8yRxQ_YQQ'
    creds = None
    
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", scope)
        # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", scope)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("sheets", "v4", credentials=creds)
        sheet = service.spreadsheets()

        newVal = "=IMAGE(\"" + card['images'] + "\")"
        if(not(updateWant)):
            changeRange = 'Gigadex!E' + (str)(n + 1) #IMAGES COLUMN
            boolRange = 'Gigadex!C' + (str)(n + 1) #REMAINING COLUMN
            updateRange = 'Gigadex!G' + (str)(n + 1) #NEED TO UPDATE COLUMN
            data = [
            {"range": changeRange, "values": [[newVal]]},
            {"range": boolRange, "values": [[True]]},
            {"range": updateRange, "values": [['']]}
            ]
        else:
            changeRange = 'Gigadex!F' + (str)(n + 1)
            data = [{"range": changeRange, "values": [[newVal]]}]
        
        body = {
        "valueInputOption": "USER_ENTERED",
        "data": data
        }

        result = sheet.values().batchUpdate(
            spreadsheetId=sheet_id, 
            body=body
        ).execute()

        print(f"Cell [{changeRange[8:]}] updated successfully with value {card['name']}")        
    except HttpError as err:
        print(err)

#Get all the cards that need updating
def getCards():
    API_KEY = 'AIzaSyAkbL2ulDMJbfoj4ftT-6WDl3ukWvhdS9k'
    sheet_id = '1HNb0SO4lkEgw9UvZ-fPevp60UQ1O5GaltV8yRxQ_YQQ'
    range_name = 'Gigadex!G2:G1026'
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{sheet_id}/values/{range_name}?key={API_KEY}"
    response = requests.get(url)
    data = response.json()['values']
    for i in range (len(data)):
        if(data[i] != []):
            newCards.append(i + 1)

# With a pokedex number, fetch all the cards of that pokemon, turn the image urls into
# images and show all of those cards, then ask the user to input the number of the 
# card they want
def pickCard(n):
    pokedexNum = n
    #Create a filter based off of pokedex number
    data = {'q':f'nationalPokedexNumbers:[{pokedexNum} TO {pokedexNum}]'} 
    #Grab the filtered data from the api
    response = requests.get("https://api.pokemontcg.io/v2/cards", data=data)
    #Filter data down to only the selected keys
    list = [{key: item[key] for key in keys if key in item} for item in(response.json().get('data'))] 
    images = []
    
    #loop through all of the card images
    for i in range (len(list)):
        list[i]['images'] = list[i]['images'].get('small')
        try:
            images.append(urlToImage(list[i]['images']))
            images[i] = cv2.resize(images[i], (500, 700))
        except: #if the card url isn't valid, set it to white
            images.append(cv2.imread('CardPNGs/white.png'))
            images[len(images) - 1] = cv2.resize(images[len(images) - 1], (500, 700))
    images.append(cv2.imread('CardPNGs/CardBack.jpg')) #add empty image to set of images
    images[len(images) - 1] = cv2.resize(images[len(images) - 1], (500, 700))

    list.append(copy.copy(list[0])) #add extra blank card to end of list
    list[len(list) - 1]['images'] = 'https://raw.githubusercontent.com/MarcinLanda/PokemonCardToSheets/main/CardPNGs/CardBack.jpg' #set extra cards image to blank

    #add white image at the end to make the last row 10 images wide
    for _ in range (10 - len(images) % 10): 
        images.append(cv2.imread('CardPNGs/white.png'))
        images[len(images) - 1] = cv2.resize(images[len(images) - 1], (500, 700))
  
    #combine the images into one large grid, 10 wide, until there are none left
    combinedImages = []
    j = 0
    while(j < len(images)):
        combinedImages.append(np.hstack(images[j:j+10]))
        j += 10
    combinedImage = np.vstack(combinedImages)
    combinedImageRGB = cv2.cvtColor(combinedImage, cv2.COLOR_BGR2RGB)
    #Show all the card images and allow user to click on wanted card
    plt.imshow(combinedImageRGB)
    plt.axis('off')
    plt.connect('button_press_event', on_click)
    mng = plt.get_current_fig_manager()
    mng.window.state('zoomed')
    plt.show()
    
    global z
    if(z == 1):
        pokemon = list[0]['name']
        cardNum = (int)(str(y) + str(x))
        list[cardNum]['name'] = pokemon
        updateSheets(n, list[cardNum])
        z = 0
    else:
        print("Skipped " + str(n))
    plt.close()

# Obtains data from clicked card and translates this data into which card is wanted by 
# the user
def on_click(event):
    if event.button is MouseButton.LEFT:
        if(event.xdata != None and event.ydata != None):
            plt.close()
            global x 
            global y
            global z
            x = (int)(event.xdata / 500)
            y = (int)(event.ydata / 700)
            z = 1

RestClient.configure(APIKEY)
getCards()
for i in cardList:
    pickCard(i)
