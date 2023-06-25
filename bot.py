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
@app.on_message(filters.command("heap"))
def catch_waifu(_, message):
    if not spawned_waifu:
        message.reply_text("There is no spawned waifu currently. Please wait for a new waifu to appear.")
        return

    # Retrieve the character name from the command
    character_name = " ".join(message.command[1:]).strip().lower()

    if not character_name:
        message.reply_text("Please provide the name of the waifu you want to catch. "
                           "Use the command in the format: `/heap character_name`.")
        return

    if character_name.lower() != spawned_waifu["name"].lower():
        message.reply_text("Oops! You caught the wrong waifu. Please try again.")
        return

    # Check if the waifu is already caught
    if waifus_collection.find_one({"name": spawned_waifu["name"]}):
        message.reply_text(f"{spawned_waifu['name']} from {spawned_waifu['series']} is already caught!")
        return

    # Save the caught waifu in the collection
    waifus_collection.insert_one({
        "name": spawned_waifu["name"],
        "series": spawned_waifu["series"],
        "image_url": spawned_waifu["image_url"]
    })
    message.reply_text(f"Congratulations! You caught {spawned_waifu['name']} from {spawned_waifu['series']}!")


def spawn_random_waifu(chat_id):
    global spawned_waifu

    # Set your Kitsu API headers
    headers = {
        "Accept": "application/vnd.api+json",
        "Content-Type": "application/vnd.api+json"
    }

    # Make an API request to Kitsu to retrieve a random character
    response = requests.get("https://kitsu.io/api/edge/characters?page[limit]=1&page[offset]=0", headers=headers)
    if response.status_code == 200:
        character_data = response.json()["data"][0]
        attributes = character_data["attributes"]
        spawned_waifu = {
            "name": attributes["name"],
            "series": attributes["media"]["data"]["attributes"]["titles"]["en"],
            "image_url": attributes["image"]["original"]
        }

        # Send the waifu image to the chat
        app.send_photo(chat_id=chat_id, photo=spawned_waifu["image_url"])
    else:
        print("Failed to spawn a waifu. Please try again.")

# Start the bot
app.run()
idle()
