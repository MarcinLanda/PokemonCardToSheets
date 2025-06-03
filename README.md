# PokemonCardToSheets

## What it Does
PokemonCardToSheets is a Python application that updates a google sheet for a Pokemon card collection of 1 of every Pokemon. Listed in the sheet is a column filled with spaces for if the Pokemon card should be updated. If the new card column has any characters, the application creates a list with all of the row numbers that contain a character so that these cards can be searched for and updated. After fetching all the necessary card updates, it searches and filters through an online pokemon card API for every card that is available in the English set of Pokemon cards. For each card in the list, it displays all cards that exist for that specific Pokemon, using matplotlib to display all images, allowing you to click on the image which card you own to notify the application that that is the card you own. The application then verifies the google sheet and takes the card previously clicked and sends the image link to the connected google sheet, updating the image associated with the card.

## Tech Stack
- Python

- ## Application Walkthrough
When you first run the program, nothing will happen unless there already is a connected google sheet with characters inside of the G column. If there are characters in the G column, the application will load and a popup will appear with the first Pokemon that contains a character in the G column. The user then interacts with the screen by either clicking on one of the cards, which automatically changes the image within the google sheets, removes the character(s) in the G column aswell as checks the have column to true, or clicking on the X or white space to exit out the application (this skips updating the card and goes straight onto the first card). This continues until every card that was marked as needing updating has been shown once.

- ## Hidden Neccessities
A credentials.json file is required in order to connect each application to Google's sheets API which allows the application to edit a personal google sheet.

Python Packages:
pip install requests
pip install opencv-python
pip install numpy
pip install matplotlib
pip install pokemontcgsdk
pip install google-auth
pip install google-auth-oauthlib
pip install google-auth-httplib2
pip install google-api-python-client
