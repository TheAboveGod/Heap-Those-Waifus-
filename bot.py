import random
import requests
import pyrogram
from pyrogram import Client, filters, idle
from pymongo import MongoClient

# Initialize the Pyrogram client
api_id = "21093975"
api_hash = "1b4009789670ce79fb775ab4b8512149"
bot_token = "6114185244:AAHkoM2xQPW_vPY2w2JPHgOxyinNn4SPBKA"

app = Client("waifu_catch_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# Connect to MongoDB
mongo_url = "mongodb+srv://sonu55:sonu55@cluster0.vqztrvk.mongodb.net/?retryWrites=true&w=majority"
mongo_client = MongoClient(mongo_url)
db = mongo_client["waifu_catch_bot"]
waifus_collection = db["waifus"]

# Global variables
message_count = 0
spawned_waifu = None

# Command to catch a waifu
@app.on_message(filters.command("catch"))
def catch_waifu(_, message):
    if not spawned_waifu:
        message.reply_text("There is no spawned waifu currently. Please wait for a new waifu to appear.")
        return

    # Retrieve the character name from the command
    character_name = " ".join(message.command[1:]).strip().lower()

    if not character_name:
        message.reply_text("Please provide the name of the waifu you want to catch. "
                           "Use the command in the format: `/catch character_name`.")
        return

    if character_name.lower() != spawned_waifu["name"].lower():
        message.reply_text("Oops! You caught the wrong waifu. Please try again.")
        return

    # Check if the waifu is already caught
    if waifus_collection.find_one({"name": spawned_waifu["name"]}):
        message.reply_text(f"{spawned_waifu['name']} from {spawned_waifu['anime']} is already caught!")
        return

    # Save the caught waifu in the collection
    waifus_collection.insert_one({
        "name": spawned_waifu["name"],
        "anime": spawned_waifu["anime"],
        "image_url": spawned_waifu["image_url"]
    })
    message.reply_text(f"Congratulations! You caught {spawned_waifu['name']} from {spawned_waifu['anime']}!")


def spawn_random_waifu(chat_id):
    global spawned_waifu

    # Set your MAL API username and password
    username = "9c35b9e4b9a9aadbf189c4500bb50968"
    password = "768d6227f1336bc49cf142722a11d20de49590eb69098b377934d1d6e5dbd29c"

    # Make an API request to MyAnimeList to retrieve a random character
    response = requests.get("https://api.myanimelist.net/v2/anime/1/characters", auth=(username, password))
    if response.status_code == 200:
        anime_data = response.json()
        characters = anime_data["characters"]
        random_character = random.choice(characters)
        spawned_waifu = {
            "name": random_character["name"],
            "series": anime_data["title"],
            "image_url": random_character["image_url"]
        }

        # Send the waifu image to the chat
        app.send_photo(chat_id=chat_id, photo=spawned_waifu["image_url"])
    else:
        print("Failed to spawn a waifu. Please try again.")

# Start the bot
app.run()
idle() 
