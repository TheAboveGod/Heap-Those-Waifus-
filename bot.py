import random
import pyrogram
from pyrogram import Client, filters, idle
from pymongo import MongoClient

# Initialize the Pyrogram client
api_id = "YOUR_API_ID"
api_hash = "YOUR_API_HASH"
bot_token = "YOUR_BOT_TOKEN"

app = Client("waifu_catch_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# Connect to MongoDB
mongo_url = "YOUR_MONGODB_URL"
mongo_client = MongoClient(mongo_url)
db = mongo_client["waifu_catch_bot"]
waifus_collection = db["waifus"]

# Global variables
message_count = 0
spawned_waifu = None

# Filter to check if it's the 10th message
@filters.group & filters.text
def tenth_message_filter(_, __, message):
    global message_count
    message_count += 1
    return message_count % 10 == 0

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
        message.reply_text(f"{spawned_waifu['name']} from {spawned_waifu['series']} is already caught!")
        return

    # Save the caught waifu in the collection
    waifus_collection.insert_one({
        "name": spawned_waifu["name"],
        "series": spawned_waifu["series"],
        "image_url": spawned_waifu["image_url"]
    })
    message.reply_text(f"Congratulations! You caught {spawned_waifu['name']} from {spawned_waifu['series']}!")

# Spawn a random waifu with an image
def spawn_random_waifu(chat_id):
    global spawned_waifu

    # Make an API request to Anime-Planet to retrieve a random waifu
    # Adapt the following code based on the specific Anime-Planet API endpoint you want to use
    response = pyrogram.Client.get(f"https://www.anime-planet.com/api/character/{random.randint(1, 10000)}")

    if response.status_code == 200:
        waifu_data = response.json()
        spawned_waifu = {
            "name": waifu_data["name"],
            "series": waifu_data["series"],
            "image_url": waifu_data["image_url"]
        }

        # Send the waifu image to the chat
        app.send_photo(chat_id=chat_id, photo=spawned_waifu["image_url"])
    else:
        print("Failed to spawn a waifu. Please try again.")

# Handle the 10th message event in group chat
@app.on_message(tenth_message_filter)
def handle_tenth_message(_, message):
    chat_id = message.chat.id
    spawn_random_waifu(chat_id)

# Start the bot
app.run()
idle()
