import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import requests
from bs4 import BeautifulSoup
import re
import random

########################################################################
# # TELEGRAM STUFF
API_KEY = '6970037214:AAHplF29QE9IrSxeGPaFAxVkAHxddpMIOLU'
bot = telebot.TeleBot(API_KEY)

markup_reply = ReplyKeyboardMarkup(resize_keyboard=True)

item_search = KeyboardButton(text='Find Trending Shows')
horror_search = KeyboardButton(text='Horror Shows')
scifi_search = KeyboardButton(text='Sci-Fi Shows')
comedy_search = KeyboardButton(text='Comedy Shows')
action_search = KeyboardButton(text='Action Shows')
animation_search = KeyboardButton(text='Animation Shows')
drama_search = KeyboardButton(text='Drama Shows')
adventure_search = KeyboardButton(text='Adventure Shows')
fantasy_search = KeyboardButton(text='Fantasy Shows')
movie_search = KeyboardButton(text='Find Random Popular Movies')

markup_reply.add(item_search)
markup_reply.add(horror_search)
markup_reply.add(scifi_search)
markup_reply.add(comedy_search)
markup_reply.add(action_search)
markup_reply.add(animation_search)
markup_reply.add(drama_search)
markup_reply.add(adventure_search)
markup_reply.add(fantasy_search)
markup_reply.add(movie_search)

@bot.message_handler(commands=['start'], content_types=['text'])
def start(message):

  msg = bot.send_message(message.chat.id, "Don't know what to watch? Let me help! Choose a button from the menu!",
                   reply_markup=markup_reply
                   )

@bot.message_handler(content_types=['text'])
def handle_start_response(message):

  if message.text == 'Find Trending Shows':
      find_five_random_shows(message)

  elif message.text == 'Horror Shows':
      find_five_genre_shows(message,genre='Horror')

  elif message.text == 'Sci-Fi Shows':
      find_five_genre_shows(message,genre='Sci-Fi')

  elif message.text == 'Comedy Shows':
      find_five_genre_shows(message,genre='Comedy')

  elif message.text == 'Action Shows':
      find_five_genre_shows(message,genre='Action')

  elif message.text == 'Animation Shows':
      find_five_genre_shows(message,genre='Animation')

  elif message.text == 'Drama Shows':
      find_five_genre_shows(message,genre='Drama')

  elif message.text == 'Adventure Shows':
      find_five_genre_shows(message,genre='Adventure')

  elif message.text == 'Fantasy Shows':
      find_five_genre_shows(message,genre='Fantasy')

  elif message.text == 'Find Random Popular Movies':
      find_five_random_movies(message)

  else:
      bot.send_message(message.chat.id, "Invalid choice. Please press one of the available buttons.")

def find_five_genre_shows(message,genre):

  bot.send_message(message.chat.id, "Loading results, please wait...")

  tv_shows = imdb_genre_search(genre=genre,num_results=5)

  while tv_shows == []:
      tv_shows = imdb_genre_search(genre=genre,num_results=5)

  for show in tv_shows:
    result = tv_database_lookup(show)
    genres = ", ".join(result['genre'])
    summary = result['summary']
    summary = re.sub(r'<[^>]*>', '', summary)
    bot.send_message(message.chat.id,
f'''
Name: {result['name']}

Image Link: {result['image']}

Genre: {genres}

Summary: {summary}

''')


def find_five_random_movies(message):

  bot.send_message(message.chat.id, "Loading results, please wait...")

  results = imdb_top_trending_movies(5)

  for result in results:
    name = result[0]
    image = result[1]
    bot.send_message(message.chat.id,
f'''
Name: {name}
Image Link: {image}
''')


def find_five_random_shows(message):

  bot.send_message(message.chat.id, "Loading results, please wait...")

  tv_shows = imdb_top_trending_shows(num_results=5)

  while tv_shows == []:
      tv_shows = imdb_top_trending_shows(num_results=5)

  for show in tv_shows:
      result = tv_database_lookup(show)
      genres = ", ".join(result['genre'])
      summary = result['summary']
      summary = re.sub(r'<[^>]*>', '', summary)
      bot.send_message(message.chat.id,
                       f'''
  Name: {result['name']}

  Image Link: {result['image']}

  Genre: {genres}

  Summary: {summary}

  ''')

# ########################################################################
# # MOVIE DATABASE STUFF...
#
#
def tv_database_lookup(show_name):

    url = f"https://api.tvmaze.com/singlesearch/shows?q={show_name}"

    response = requests.get(url=url)

    # Parse the JSON response
    data = response.json()

    name = "House of Dragons"
    original_image_url = "https://m.media-amazon.com/images/M/MV5BZjBiOGIyY2YtOTA3OC00YzY1LThkYjktMGRkYTNhNTExY2I2XkEyXkFqcGdeQXVyMTEyMjM2NDc2._V1_.jpg"
    genre = ["Drama"]
    summary = "The Targaryens are on the rise..."

    if data is not None:
        # Check if data exists and update the variables if found
        if "name" in data:
            name = data["name"]
        if "image" in data:
            image = data["image"]
        if "genres" in data:
            genre = data["genres"]
        if "summary" in data:
            summary = data["summary"]

    # Access the "image" key
    if data is not None:
        image = data["image"]
        original_image_url = image["original"]
        name = data["name"]
        genre = data["genres"]
        summary = data["summary"]

    results_dictionary = {
        'name':name,
        'image':original_image_url,
        'genre':genre,
        'summary':summary,
    }

    return results_dictionary
########################################################################

########################################################################
# BEAUTIFUL SOUP STUFF


def imdb_top_trending_movies(num_results):

    url = "https://m.imdb.com/chart/moviemeter/?ref_=nv_mv_mpm"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.5'
    }
    # Send an HTTP GET request to the URL
    response = requests.get(url=url, headers=headers)

    # Parse the HTML content using Beautiful Soup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all elements with class "ipc-metadata-list-summary-item sc-59b6048d-0 cuaJSp cli-parent"
    summary_items = soup.find_all(class_="ipc-metadata-list-summary-item sc-59b6048d-0 cuaJSp cli-parent")

    # Initialize lists to store the extracted information
    list_of_src_urls = []
    list_of_titles = []

    # Loop through each summary item
    for summary_item in summary_items:
        # Find the "ipc-image" class within the current summary item
        ipc_image = summary_item.find(class_="ipc-image")

        # Extract the 'src' attribute from the 'ipc-image' element
        src_url = ipc_image['src'] if ipc_image else None
        list_of_src_urls.append(src_url)

        # Find the "ipc-title__text" class within the current summary item
        ipc_title = summary_item.find(class_="ipc-title__text")

        # Extract the text content from the 'h3' element
        title_text = ipc_title.text if ipc_title else None
        list_of_titles.append(title_text)

    # Print or use the extracted information

    connected = list(zip( list_of_titles,list_of_src_urls,))

    #print(connected)

    random.shuffle(connected)

    #print(connected)

    connected = connected[:num_results]

    return connected

    #print(connected)

#imdb_top_trending_movies(5)

def imdb_top_trending_shows(num_results):

    url = "https://m.imdb.com/chart/tvmeter/?ref_=nv_tvv_mptv"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.5'
    }

    # Send an HTTP GET request to the URL
    response = requests.get(url=url,headers=headers)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:

        # Parse the HTML content of the page using Beautiful Soup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find and extract elements with class "article_movie_title"
        # Find and extract all elements with class "ipc-title__text"
        title_elements = soup.find_all(class_="ipc-title__text")

        list_of_titles = []

        # Loop through the found elements and extract the TV show titles
        for title_element in title_elements:
            title_text = title_element.text
            list_of_titles.append(title_text)

        list_of_titles = list_of_titles[2:-12]

        #print(list_of_titles)

        random.shuffle(list_of_titles)

        output = list_of_titles[2:num_results+2]

        #print(output)

        return output
    else:
        print("Failed to retrieve the web page. Status code:", response.status_code)

def imdb_genre_search(genre,num_results):

    url = f"https://m.imdb.com/search/title/?genres={genre}&explore=genres&title_type=tv_series%2Cmini_series"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.5'
    }

    # Send an HTTP GET request to the URL
    response = requests.get(url=url,headers=headers)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:

        # Parse the HTML content of the page using Beautiful Soup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Step 1: Find all items with the class 'lister-item mode-advanced'
        items = soup.find_all('div', class_='lister-item mode-advanced')

        results = []

        # Step 2 and 3: For each item, find the 'loadlate' class and 'lister-item-header'
        for item in items:
            # Find the 'lister-item-header' within the current item
            lister_item_header = item.find('h3', class_='lister-item-header')

            # Extract the text content from the 'a' tag within 'lister-item-header'
            title_text = lister_item_header.find('a').text if lister_item_header else None

            results.append(title_text)

        random.shuffle(results)

        results = results[:num_results]

        print(results)

        return results
########################################################################
bot.polling()
########################################################################