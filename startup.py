import discord
import pyautogui
import asyncio
import cv2
import numpy as np
from PIL import ImageGrab

# Create the intents object
intents = discord.Intents.default()
intents.message_content = True  # This is required to read message content

# Create your bot and pass the intents
client = discord.Client(intents=intents)

# Function to load lines from the text file
def load_lines():
    with open('textfile.txt', 'r') as f:
        lines = f.readlines()
    return lines

# Function to delete the first line from the text file
def delete_first_line():
    lines = load_lines()
    if lines:
        lines.pop(0)  # Remove the first line
        with open('textfile.txt', 'w') as f:
            f.writelines(lines)  # Rewrite the remaining lines back into the file

# Keep track of the current line index
current_line = 0
typing_task = None  # Keeps track of the typing task so we can stop it later
stop_typing = False  # Global flag to stop the typing loop

# Path to the reference image
image_path = r'C:\Users\salmi\OneDrive\Desktop\New folder\close.png'  # Update your image file name

# Function to simulate typing the current line in a loop
async def type_current_line():
    global current_line, stop_typing

    while not stop_typing:  # Keep typing the current line until stopped
        lines = load_lines()
        if current_line < len(lines):
            text_to_type = lines[current_line].strip()
            pyautogui.typewrite(text_to_type)
            pyautogui.press('enter')
            print(f"Typed: {text_to_type}")
        else:
            print("No more lines to type.")
            break
        await asyncio.sleep(5)  # Pause before typing again

# Function to check for the image on the screen
def detect_image(image_path):
    # Capture the screen
    screen = np.array(ImageGrab.grab())
    screen_gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)

    # Load the reference image and convert it to grayscale
    template = cv2.imread(image_path, 0)

    # Perform template matching
    res = cv2.matchTemplate(screen_gray, template, cv2.TM_CCOEFF_NORMED)
    threshold = 0.8
    loc = np.where(res >= threshold)

    return len(loc[0]) > 0 and len(loc[1]) > 0

# Periodic image check every 30 seconds
async def check_for_image():
    global current_line, typing_task, stop_typing
    while True:
        if detect_image(image_path):
            # Stop the current typing loop
            stop_typing = True
            if typing_task:
                typing_task.cancel()

            print("Image detected, moving to the next line...")

            # Increment the line index
            current_line += 1

            # If we reached the end of the file, loop back to the first line
            lines = load_lines()
            if current_line >= len(lines):
                current_line = 0

            # Delete the current line from the file
            delete_first_line()

            # Start typing the new line
            stop_typing = False
            typing_task = asyncio.create_task(type_current_line())

        # Wait 30 seconds before checking again
        await asyncio.sleep(30)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    global current_line, typing_task, stop_typing

    if message.author == client.user:
        return

    if message.content.startswith('!next'):
        # Stop the current typing loop
        stop_typing = True
        if typing_task:
            typing_task.cancel()

        await message.channel.send('Moving to the next line...')

        # Increment the line index
        current_line += 1

        # If we reached the end of the file, loop back to the first line
        lines = load_lines()
        if current_line >= len(lines):
            current_line = 0

        # Delete the current line from the file
        delete_first_line()

        # Start typing the new line
        stop_typing = False
        typing_task = asyncio.create_task(type_current_line())
        await message.channel.send(f'Typing line {current_line + 1}...')

    elif message.content.startswith('!start'):
        # Start typing the first line
        if typing_task:
            typing_task.cancel()
        stop_typing = False
        typing_task = asyncio.create_task(type_current_line())
        await message.channel.send(f'Starting with line {current_line + 1}...')

# Run the bot in an asyncio event loop
async def run_bot():
    # Start the periodic image check task
    asyncio.create_task(check_for_image())

    # Run the bot
    await client.start('MTMxNzIxMzcyNTIyODI3Mzc0NA.GfM2dO.75E-Akizb3M_LWqrEHGSfQ-nSrfmMh2yxP5Pk4')

# Execute the bot
asyncio.run(run_bot())
