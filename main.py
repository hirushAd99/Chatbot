import json
import random
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import spacy

# Load spaCy English language model
nlp = spacy.load("en_core_web_sm")

# Load menu and intents from JSON files
with open('menu.json', 'r') as menu_file:
    menu = json.load(menu_file)

with open('intents.json', 'r') as intents_file:
    intents = json.load(intents_file)["intents"]

# Telegram Bot Token
TOKEN = '5881058982:AAGJYI0beRW2Ke7xeJ89M_vUd5lHtjzUZUI'

# Create updater and dispatcher
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

# Function to handle regular messages
def handle_messages(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text.lower()

    # Check if the user mentioned an author name or book title
    mentioned_authors = [author['author'].lower() for author in menu if author['author'].lower() in user_message]
    mentioned_titles = [book['title'].lower() for book in menu if book['title'].lower() in user_message]

    if mentioned_authors or mentioned_titles:
        if mentioned_authors:
            books_info = [book for book in menu if book['author'].lower() in mentioned_authors]
            mention_type = 'author'
        else:
            books_info = [book for book in menu if book['title'].lower() in mentioned_titles]
            mention_type = 'title'

        if books_info:
            suggestions = f"We found the following books by {', '.join(mentioned_authors)}:\n\n" if mention_type == 'author' else f"We found the following books with titles {', '.join(mentioned_titles)}:\n\n"
            for book in books_info:
                suggestions += f"Title: {book['title']}\nAuthor: {book['author']}\nCategory: {book['category']}\nPrice: {book['price_lkr']} LKR\n\n"

            update.message.reply_text(suggestions)
        else:
            if mention_type == 'author':
                update.message.reply_text(f"I'm sorry, but we don't have any books by {', '.join(mentioned_authors)} at the moment.")
            else:
                update.message.reply_text(f"I'm sorry, but we don't have any books with titles {', '.join(mentioned_titles)} at the moment.")
        return
    else:
        # Iterate through intents
        for intent in intents:
            if 'patterns' in intent and 'responses' in intent:
                for pattern in intent['patterns']:
                    # Check for similarity using spaCy
                    doc_user = nlp(user_message)
                    doc_pattern = nlp(pattern.lower())

                    similarity = doc_user.similarity(doc_pattern)
                    if similarity >= 0.6:  # Adjust the similarity threshold as needed
                        response = random.choice(intent['responses'])
                        update.message.reply_text(response)

                        # If the intent is related to book categories or menu, provide the introduction
                        if intent['tag'] == "book_menu":
                            book_menu(update, context)
                        return

        # Check if the user mentioned a specific category
        mentioned_categories = [category for category in [book['category'].lower() for book in menu] if category in user_message]

        if mentioned_categories:
            for category in mentioned_categories:
                category_books = [book for book in menu if book['category'].lower() == category]

                if category_books:
                    suggestions = f"It sounds like you're interested in {category}. We recommend the following books:\n\n"
                    for book in category_books:
                        suggestions += f"Title: {book['title']}\nAuthor: {book['author']}\nPrice: {book['price_lkr']} LKR\nDescription: {book.get('description', 'Not available')}\n\n"

                    update.message.reply_text(suggestions)
                else:
                    update.message.reply_text(f"I'm sorry, but we don't have any books in the {category} category at the moment.")
                return
        else:
            # If no intent matches and no mentioned categories, handle as an unknown query
            unknown_query(update)



# Command handler for /start
def start(update: Update, context: CallbackContext) -> None:
    introduction = "Hello! I'm your Book Chatbot. I can help you with book recommendations, information about authors, and book orders.\n\n"\
                    "If you want to explore our book categories, just type 'book menu' or any related query."
    
    update.message.reply_text(introduction)

# Command handler for /book_menu
def book_menu(update: Update, context: CallbackContext) -> None:
    introduction = "We have books under the following categories only:\n\n"\
                    "1. Combined Maths\n"\
                    "2. Chemistry\n"\
                    "3. Physics\n"\
                    "4. Biology\n\n"\
                    "Please select a category by pressing the buttons from your keyboard."
    
    # Use ReplyKeyboardMarkup to provide category options
    category_buttons = [
        [KeyboardButton("1. Combined Maths"), KeyboardButton("2. Chemistry")],
        [KeyboardButton("3. Physics"), KeyboardButton("4. Biology")]
    ]
    reply_markup = ReplyKeyboardMarkup(category_buttons, one_time_keyboard=True)

    update.message.reply_text(introduction, reply_markup=reply_markup)

# Function to handle unknown queries
def unknown_query(update: Update) -> None:
    response = random.choice([
        "I'm sorry, but I couldn't understand that. Could you please rephrase?",
        "I didn't catch that. Could you please provide more clarity?"
    ])
    update.message.reply_text(response)

# Add command handlers
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_messages))

# Start the bot
updater.start_polling()
updater.idle()

# # Telegram Bot Token
# TOKEN = '5881058982:AAGJYI0beRW2Ke7xeJ89M_vUd5lHtjzUZUI'