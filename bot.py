import telebot
from telebot.types import Message,User,Chat,PreCheckoutQuery,LabeledPrice,ReplyKeyboardMarkup, KeyboardButton
import requests
from bs4 import BeautifulSoup
import re
import random
import sqlite3
########################################################################
#
def add_user(telegram_id,is_lifetime_member=False):

    conn = sqlite3.connect('user_data.db')

    cursor = conn.cursor()

    # Create a table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            is_lifetime_member BOOLEAN NOT NULL
        )
    ''')

    # Insert or update user data
    cursor.execute('INSERT OR REPLACE INTO users (user_id, is_lifetime_member) VALUES (?, ?)', (telegram_id, is_lifetime_member))

    # Commit the changes
    conn.commit()

    # Close the connection
    conn.close()


def user_is_in_database(telegram_id):

    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()

    # Check if the user exists in the database
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (telegram_id,))
    user_data = cursor.fetchone()

    if user_data:
        return True
    else:
        return False

def is_lifetime_member(telegram_id):
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()

    # Execute a SELECT query to retrieve the user's data
    cursor.execute('SELECT is_lifetime_member FROM users WHERE user_id = ?', (telegram_id,))

    # Fetch the result
    result = cursor.fetchone()

    # Close the connection
    conn.close()

    # Check if the result is not None
    if result is not None:
        # The user exists, and you can access the is_lifetime_member value
        is_lifetime_member_value = result[0]
        return is_lifetime_member_value
    else:
        # The user does not exist in the database
        return False

def give_lifetime_membership(telegram_id):

    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()

    user_in_database = user_is_in_database(telegram_id=telegram_id)

    if user_in_database:
        # User exists, update the is_lifetime_member field to True
        cursor.execute('UPDATE users SET is_lifetime_member = 1 WHERE user_id = ?', (telegram_id,))
        conn.commit()
        conn.close()
        print('lifetime membership granted!')
        return True

    else:
        # User not found
        conn.close()
        return False

########################################################################
#PAYMASTER TEST STUFF
PAYMASTER_TEST_TOKEN = '1744374395:TEST:dd78934ceacd8789b8b2'
########################################################################
# # TELEGRAM STUFF
API_KEY = '6970037214:AAHplF29QE9IrSxeGPaFAxVkAHxddpMIOLU'
bot = telebot.TeleBot(API_KEY)

#markup_reply = ReplyKeyboardMarkup(resize_keyboard=True)

PRICE = LabeledPrice(label='Lifetime Subscription',amount=10*100)

##################################################################################################################
# SUBSCRIPTION STUFF
@bot.message_handler(commands=['subscribe'], content_types=['text'])
def subscribe(message):
    telegram_id = message.from_user.id
    is_already_user = user_is_in_database(telegram_id)
    if is_already_user:
        msg = bot.send_message(message.chat.id, f"You are already subscribed to the TVShowFinderBot")
    else:
        add_user(telegram_id=telegram_id)
        #msg = bot.send_message(message.chat.id, f"You have successfully subscribed to the TVShowFinderBot")
        # refreshing the button menu...
        markup_reply = ReplyKeyboardMarkup(resize_keyboard=True)
        #
        # Trending TV shows in general
        item_search = KeyboardButton(text='Find Trending Shows')

        # Trending TV shows by genre
        horror_search = KeyboardButton(text='Horror Shows')
        scifi_search = KeyboardButton(text='Sci-Fi Shows')
        comedy_search = KeyboardButton(text='Comedy Shows')

        action_search = KeyboardButton(text='Action Shows')
        animation_search = KeyboardButton(text='Animation Shows')
        drama_search = KeyboardButton(text='Drama Shows')

        adventure_search = KeyboardButton(text='Adventure Shows')
        fantasy_search = KeyboardButton(text='Fantasy Shows')
        documentary_search = KeyboardButton(text='Documentaries')

        game_show_search = KeyboardButton(text='Talk Shows')
        romance_search = KeyboardButton(text='Romance Shows')
        family_search = KeyboardButton(text='Family Shows')

        # Trending movies in general
        movie_search = KeyboardButton(text='Find Random Popular Movies')

        # Trending videogames in general
        video_game_search = KeyboardButton(text='Find Random Popular Video Games')

        row1 = [item_search]
        row2 = [horror_search, scifi_search, documentary_search]
        row3 = [comedy_search, action_search, animation_search]
        row4 = [drama_search, adventure_search, fantasy_search]
        row5 = [game_show_search, romance_search, family_search]
        row6 = [movie_search]
        row7 = [video_game_search]

        markup_reply.add(*row1)

        if is_lifetime_member(telegram_id=telegram_id):
            markup_reply.add(*row2)
            markup_reply.add(*row3)
            markup_reply.add(*row4)
            markup_reply.add(*row5)
            markup_reply.add(*row6)
            markup_reply.add(*row7)
        elif user_is_in_database(telegram_id):
            markup_reply.add(*row6)
        msg = bot.send_message(message.chat.id, "You have successfully subscribed to the TVShowFinderBot. You can now search for popular movies.",
                               reply_markup=markup_reply
                               )
##################################################################################################################

@bot.message_handler(commands=['buy'], content_types=['text'])
def buy(message):
    telegram_id = message.from_user.id
    # check subscribed status
    if user_is_in_database(telegram_id):
        print('user subscribed and in database')
        # check lifetime status
        is_user_already_lifetime_member = is_lifetime_member(telegram_id)
        print(f"user is already a lifetime member: {is_user_already_lifetime_member}")

        if not is_user_already_lifetime_member:

            msg = bot.send_message(message.chat.id, f"Use 4242 4242 4242 4242 as the debit card number. Any valid date. Any three digits for CVV.")

            bot.send_invoice(message.chat.id,
                             title='Lifetime Subscription',
                             description='One time payment for unlimited access to all bot features',
                             provider_token='1744374395:TEST:dd78934ceacd8789b8b2',
                             currency="RUB",
                             photo_url="https://media.npr.org/assets/img/2023/05/25/2023summerfilmtvpreview-copy_wide-ec66db18be9a0f2b5512c34448cf3bb3354b7c5f-s1100-c50.jpg",
                             prices=[PRICE],
                             photo_width=416,
                             photo_height=234,
                             photo_size=416,
                             is_flexible=False,
                             start_parameter='Receipt',
                             invoice_payload='test-invoice-payload'
                             )
        else:
            msg = bot.send_message(message.chat.id, f"You already have a lifetime membership.")

    else:
        msg = bot.send_message(message.chat.id, f"Please subscribe first, then try again.")

#pre checkout
@bot.pre_checkout_query_handler(lambda query:True)
def pre_checkout_query(pre_checkout_q:PreCheckoutQuery):
    bot.answer_pre_checkout_query(int(pre_checkout_q.id),ok=True)

#successful payment
@bot.message_handler(content_types=['successful_payment'])
def got_payment(message: Message):
    telegram_id = message.from_user.id
    result = give_lifetime_membership(telegram_id=telegram_id)
    if result:
        bot.send_message(message.chat.id,
f'''             
Payment Successful.

RECEIPT INFORMATION:
                
Currency: {message.successful_payment.currency}

Total Amount: {message.successful_payment.total_amount/100}

Invoice Payload: {message.successful_payment.invoice_payload}

Telegram Payment Charge ID: {message.successful_payment.telegram_payment_charge_id}

Provider Payment Charge ID: {message.successful_payment.provider_payment_charge_id}
''')
        #refreshing the button menu...
        markup_reply = ReplyKeyboardMarkup(resize_keyboard=True)
        #
        # Trending TV shows in general
        item_search = KeyboardButton(text='Find Trending Shows')

        # Trending TV shows by genre
        horror_search = KeyboardButton(text='Horror Shows')
        scifi_search = KeyboardButton(text='Sci-Fi Shows')
        comedy_search = KeyboardButton(text='Comedy Shows')

        action_search = KeyboardButton(text='Action Shows')
        animation_search = KeyboardButton(text='Animation Shows')
        drama_search = KeyboardButton(text='Drama Shows')

        adventure_search = KeyboardButton(text='Adventure Shows')
        fantasy_search = KeyboardButton(text='Fantasy Shows')
        documentary_search = KeyboardButton(text='Documentaries')

        game_show_search = KeyboardButton(text='Talk Shows')
        romance_search = KeyboardButton(text='Romance Shows')
        family_search = KeyboardButton(text='Family Shows')

        # Trending movies in general
        movie_search = KeyboardButton(text='Find Random Popular Movies')

        # Trending videogames in general
        video_game_search = KeyboardButton(text='Find Random Popular Video Games')

        row1 = [item_search]
        row2 = [horror_search, scifi_search, documentary_search]
        row3 = [comedy_search, action_search, animation_search]
        row4 = [drama_search, adventure_search, fantasy_search]
        row5 = [game_show_search, romance_search, family_search]
        row6 = [movie_search]
        row7 = [video_game_search]

        markup_reply.add(*row1)

        if is_lifetime_member(telegram_id=telegram_id):
            markup_reply.add(*row2)
            markup_reply.add(*row3)
            markup_reply.add(*row4)
            markup_reply.add(*row5)
            markup_reply.add(*row6)
            markup_reply.add(*row7)
        elif user_is_in_database(telegram_id):
            markup_reply.add(*row6)
        msg = bot.send_message(message.chat.id, "You now have permanent access to all bot features:",
                               reply_markup=markup_reply
                               )


@bot.message_handler(commands=['start'], content_types=['text'])
def start(message):

    telegram_id = message.from_user.id

    markup_reply = ReplyKeyboardMarkup(resize_keyboard=True)
    #
    # Trending TV shows in general
    item_search = KeyboardButton(text='Find Trending Shows')

    # Trending TV shows by genre
    horror_search = KeyboardButton(text='Horror Shows')
    scifi_search = KeyboardButton(text='Sci-Fi Shows')
    comedy_search = KeyboardButton(text='Comedy Shows')

    action_search = KeyboardButton(text='Action Shows')
    animation_search = KeyboardButton(text='Animation Shows')
    drama_search = KeyboardButton(text='Drama Shows')

    adventure_search = KeyboardButton(text='Adventure Shows')
    fantasy_search = KeyboardButton(text='Fantasy Shows')
    documentary_search = KeyboardButton(text='Documentaries')

    game_show_search = KeyboardButton(text='Talk Shows')
    romance_search = KeyboardButton(text='Romance Shows')
    family_search = KeyboardButton(text='Family Shows')

    # Trending movies in general
    movie_search = KeyboardButton(text='Find Random Popular Movies')

    # Trending videogames in general
    video_game_search = KeyboardButton(text='Find Random Popular Video Games')

    row1 = [item_search]
    row2 = [horror_search, scifi_search, documentary_search]
    row3 = [comedy_search, action_search, animation_search]
    row4 = [drama_search, adventure_search, fantasy_search]
    row5 = [game_show_search, romance_search, family_search]
    row6 = [movie_search]
    row7 = [video_game_search]

    markup_reply.add(*row1)

    if is_lifetime_member(telegram_id=telegram_id):
        markup_reply.add(*row2)
        markup_reply.add(*row3)
        markup_reply.add(*row4)
        markup_reply.add(*row5)
        markup_reply.add(*row6)
        markup_reply.add(*row7)
    elif user_is_in_database(telegram_id):
        markup_reply.add(*row6)

    msg = bot.send_message(message.chat.id, "Don't know what to watch? Let me help! Choose a button from the menu! /subscribe or /buy to unlock more features",
                   reply_markup=markup_reply
                   )

@bot.message_handler(commands=['support'], content_types=['text'])
def support(message):

    bot.send_message(message.chat.id,
f'''
For any issues or inquires please contact me at: https://t.me/tImoHyDe

Please allow up to 24 hours for a response.
''')

@bot.message_handler(commands=['terms'], content_types=['text'])
def terms(message):
    bot.send_message(message.chat.id,
f'''
TERMS OF SERVICE FOR TVSHOWFINDERBOT:-

By using TVShowFinderBot, you agree to the following terms and conditions:

Usage: TVShowFinderBot is a Telegram bot designed to help users find information about trending movies and TV shows. The bot provides recommendations based on user queries and preferences.

Information Accuracy: While TVShowFinderBot strives to provide accurate and up-to-date information, we do not guarantee the accuracy or completeness of the data. Users are encouraged to verify information independently.

User Conduct: Users must use TVShowFinderBot in compliance with applicable laws and regulations. Any misuse, abuse, or violation of these terms may result in the termination of access to the bot.

Personal Responsibility: TVShowFinderBot does not endorse or promote any specific content. Users are solely responsible for their choices and actions based on the information provided by the bot.

Privacy: TVShowFinderBot respects user privacy and does not store personal information. However, telegram ID is stored in a database to keep track of subscribed members and lifetime members. Interactions with the bot may be logged for the purpose of improving service quality.

Changes to Terms: TVShowFinderBot reserves the right to update or modify these terms of service at any time. Users will be notified of any significant changes.

Bot Availability: TVShowFinderBot availability may be subject to interruptions or downtime. We strive to provide uninterrupted service but cannot guarantee constant availability.

Feedback and Support: Users are encouraged to provide feedback on their experience with TVShowFinderBot. For support or assistance, please contact: https://t.me/tImoHyDe.

By using TVShowFinderBot, you acknowledge that you have read, understood, and agreed to these terms of service.

Last Updated: 17/11/2023
''')


@bot.message_handler(content_types=['text'])
def handle_start_response(message):

  if message.text == 'Find Trending Shows':
      find_five_random_shows(message)

  elif message.text == 'Horror Shows':
      find_five_genre_shows(message,genre='Horror')

  elif message.text == 'Sci-Fi Shows':
      find_five_genre_shows(message,genre='Sci-Fi')

  elif message.text == 'Documentaries':
      find_five_genre_shows(message, genre='Documentary')

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

  elif message.text == 'Talk Shows':
      find_five_genre_shows(message,genre='talk-show')

  elif message.text == 'Romance Shows':
      find_five_genre_shows(message,genre='Romance')

  elif message.text == 'Family Shows':
      find_five_genre_shows(message,genre='Family')

  elif message.text == 'Find Random Popular Video Games':
      find_five_genre_videogames(message)

  else:

      telegram_id = message.from_user.id

      bot.send_message(message.chat.id, "Invalid choice. Please press one of the available buttons.")

      markup_reply = ReplyKeyboardMarkup(resize_keyboard=True)
      #
      # Trending TV shows in general
      item_search = KeyboardButton(text='Find Trending Shows')

      # Trending TV shows by genre
      horror_search = KeyboardButton(text='Horror Shows')
      scifi_search = KeyboardButton(text='Sci-Fi Shows')
      comedy_search = KeyboardButton(text='Comedy Shows')

      action_search = KeyboardButton(text='Action Shows')
      animation_search = KeyboardButton(text='Animation Shows')
      drama_search = KeyboardButton(text='Drama Shows')

      adventure_search = KeyboardButton(text='Adventure Shows')
      fantasy_search = KeyboardButton(text='Fantasy Shows')
      documentary_search = KeyboardButton(text='Documentaries')

      game_show_search = KeyboardButton(text='Talk Shows')
      romance_search = KeyboardButton(text='Romance Shows')
      family_search = KeyboardButton(text='Family Shows')

      # Trending movies in general
      movie_search = KeyboardButton(text='Find Random Popular Movies')

      # Trending videogames in general
      video_game_search = KeyboardButton(text='Find Random Popular Video Games')

      row1 = [item_search]
      row2 = [horror_search, scifi_search, documentary_search]
      row3 = [comedy_search, action_search, animation_search]
      row4 = [drama_search, adventure_search, fantasy_search]
      row5 = [game_show_search, romance_search, family_search]
      row6 = [movie_search]
      row7 = [video_game_search]

      markup_reply.add(*row1)

      if is_lifetime_member(telegram_id=telegram_id):
          markup_reply.add(*row2)
          markup_reply.add(*row3)
          markup_reply.add(*row4)
          markup_reply.add(*row5)
          markup_reply.add(*row6)
          markup_reply.add(*row7)
      elif user_is_in_database(telegram_id):
          markup_reply.add(*row6)

      msg = bot.send_message(message.chat.id, "Don't know what to watch? Let me help! Choose a button from the menu! /subscribe or /buy to unlock more features",
                             reply_markup=markup_reply
                             )

def find_five_genre_videogames(message):

  bot.send_message(message.chat.id, "Loading results, please wait...")

  results = imdb_top_trending_videogames(5)

  if results == []:
      bot.send_message(message.chat.id,'An error occurred. Please contact: https://t.me/tImoHyDe')
  else:
      results = imdb_top_trending_videogames(num_results=5)

      for result in results:
        name = result[0]
        image = result[1]
        description = result[2]
        bot.send_message(message.chat.id,
f'''
Name: {name}

Image Link: {image}

Description: {description}
''')

def find_five_genre_shows(message,genre):

  bot.send_message(message.chat.id, "Loading results, please wait...")

  tv_shows = imdb_genre_search(genre=genre,num_results=5)

  if tv_shows == []:
      bot.send_message(message.chat.id,'An error occurred. Please contact: https://t.me/tImoHyDe')
  else:
      tv_shows = imdb_genre_search(genre=genre,num_results=5)

      for show in tv_shows:
        name = show[0]
        image = show[1]
        description = show[2]
        bot.send_message(message.chat.id,
f'''
Name: {name}

Image Link: {image}

Summary: {description}

''')

def find_five_random_movies(message):

  bot.send_message(message.chat.id, "Loading results, please wait...")

  results = imdb_top_trending_movies(5)

  if results == []:
      bot.send_message(message.chat.id,'An error occurred. Please contact: https://t.me/tImoHyDe')
  else:

      for result in results:
        name = result[0]
        image = result[1]
        description = result[2]
        bot.send_message(message.chat.id,
f'''
Name: {name}

Image Link: {image}

Summary: {description}

''')


def find_five_random_shows(message):

  bot.send_message(message.chat.id, "Loading results, please wait...")

  tv_shows = imdb_top_trending_shows(num_results=5)

  if tv_shows == []:
      bot.send_message(message.chat.id, 'An error occurred. Please contact: https://t.me/tImoHyDe')
  else:

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

    name = "Scavenger's Reign"
    original_image_url = "https://beam-images.warnermediacdn.com/BEAM_LWM_DELIVERABLES/50c8ce6d-088c-42d9-9147-d1b19b1289d4/49ae26f26931839ad88ac02777d6f24fc22a2134.jpg?host=wbd-images.prod-vod.h264.io&partner=beamcom"
    genre = ["Drama, Sci-Fi, Action, Mystery, Adventure, Animation, Horror, Fantasy"]
    summary = " The series follows the survivors of the damaged interstellar cargo ship Demeter 227 who are stranded on Vesta, an alien planet bustling with flora and fauna but filled with dangers. The survivors start off separated in three groups: Azi and her robot companion Levi, Sam and Ursula, and the isolated Kamen."

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


def imdb_top_trending_videogames(num_results):

    url = "https://m.imdb.com/search/title/?title_type=video_game"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.5'
    }
    # Send an HTTP GET request to the URL
    response = requests.get(url=url, headers=headers)

    # Parse the HTML content using Beautiful Soup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all elements with class "ipc-metadata-list-summary-item sc-59b6048d-0 cuaJSp cli-parent"
    summary_items = soup.find_all(class_="ipc-metadata-list-summary-item")

    # Initialize lists to store the extracted information
    list_of_titles = []
    list_of_sources = []
    list_of_descriptions = []

    # Loop through each summary item
    try:
        for summary_item in summary_items:

            text_box = summary_item.find('h3', class_='ipc-title__text').text
            text_box = re.sub('^[0-9]+\.\s*', '', text_box)
            list_of_titles.append(text_box)

            description = summary_item.find(class_='ipc-html-content-inner-div').text
            list_of_descriptions.append(description)

            image_container = summary_item.find(class_="ipc-image")
            srcset_attribute = image_container.get('srcset')
            all_sources = srcset_attribute.split(sep=',')

            if all_sources[-4]:
                list_of_sources.append(all_sources[-4])
            else:
                list_of_sources.append(all_sources[0])
        combined_lists = list(zip(list_of_titles, list_of_sources, list_of_descriptions))

        random.shuffle(combined_lists)

        combined_lists = combined_lists[:num_results]

        return combined_lists
    except:
        return []

def imdb_top_trending_movies(num_results):

    url = "https://m.imdb.com/search/title/?title_type=feature"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.5'
    }
    # Send an HTTP GET request to the URL
    response = requests.get(url=url, headers=headers)

    # Parse the HTML content using Beautiful Soup
    soup = BeautifulSoup(response.text, 'html.parser')

    try:
        # Find all elements with class "ipc-metadata-list-summary-item sc-59b6048d-0 cuaJSp cli-parent"
        summary_items = soup.find_all(class_="ipc-metadata-list-summary-item")

        # Initialize lists to store the extracted information
        list_of_titles = []
        list_of_sources = []
        list_of_descriptions = []

        # Loop through each summary item
        for summary_item in summary_items:

            text_box = summary_item.find('h3', class_='ipc-title__text').text
            text_box = re.sub('^[0-9]+\.\s*', '', text_box)
            list_of_titles.append(text_box)

            description = summary_item.find(class_='ipc-html-content-inner-div').text
            list_of_descriptions.append(description)

            image_container = summary_item.find(class_="ipc-image")
            srcset_attribute = image_container.get('srcset')
            all_sources = srcset_attribute.split(sep=',')

            if all_sources[-4]:
                list_of_sources.append(all_sources[-4])
            else:
                list_of_sources.append(all_sources[0])

        combined_lists = list(zip(list_of_titles, list_of_sources, list_of_descriptions))

        random.shuffle(combined_lists)

        combined_lists = combined_lists[:num_results]

        return combined_lists
    except:
        return []

def imdb_top_trending_shows(num_results):

    url = "https://m.imdb.com/chart/tvmeter/?ref_=nv_tvv_mptv"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.5'
    }

    # Send an HTTP GET request to the URL
    response = requests.get(url=url,headers=headers)

    try:
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
    except:
        return []

def imdb_genre_search(genre,num_results):

    url = f"https://m.imdb.com/search/title/?title_type=tv_series&genres={genre}"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.5'
    }
    # Send an HTTP GET request to the URL
    response = requests.get(url=url, headers=headers)

    try:
        # Parse the HTML content using Beautiful Soup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all elements with class "ipc-metadata-list-summary-item sc-59b6048d-0 cuaJSp cli-parent"
        summary_items = soup.find_all(class_="ipc-metadata-list-summary-item")

        # Initialize lists to store the extracted information
        list_of_titles = []
        list_of_sources = []
        list_of_descriptions = []

        # Loop through each summary item
        for summary_item in summary_items:

            text_box = summary_item.find('h3', class_='ipc-title__text').text
            text_box = re.sub('^[0-9]+\.\s*', '', text_box)
            list_of_titles.append(text_box)

            description = summary_item.find(class_='ipc-html-content-inner-div').text
            list_of_descriptions.append(description)

            image_container = summary_item.find(class_="ipc-image")
            srcset_attribute = image_container.get('srcset')
            all_sources = srcset_attribute.split(sep=',')

            if all_sources[-4]:
                list_of_sources.append(all_sources[-4])
            else:
                list_of_sources.append(all_sources[0])

        combined_lists = list(zip(list_of_titles, list_of_sources, list_of_descriptions))

        random.shuffle(combined_lists)

        combined_lists = combined_lists[:num_results]

        return combined_lists
    except:
        return []
########################################################################
bot.polling()
########################################################################