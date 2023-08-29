import asyncio
from time import sleep
import websockets
import json
from json import encoder
import requests
import simpleobsws
import string
import random
import configparser
from datetime import datetime

config = configparser.ConfigParser()
config.read("config.ini")

channel_auth = config.get("picarto", "channel_auth")
channel_owner = config.get("picarto", "channel_owner")
animations = {}
user_list = {}
boosted_users = {}
active_users = []
clean_up_list = []

chat_uri = "wss://chat.picarto.tv/bot/"
headers = {"User-Agent": f"PTV-BOT-{channel_owner}"}


def get_saved_standings():
    file = open("user_points.json", "r")
    standings = {}
    try:
        standings = json.load(file)
    except Exception:
        print("File Empty!")
    file.close()
    return standings


def get_boosted_users():
    file = open("boosted_users.json", "r")
    boosted = []
    try:
        boosted = json.load(file)
    except Exception:
        print("File Empty!")
    file.close()
    return boosted


def get_animation_definitions():
    with open("animations.json") as json_file:
        data = json.load(json_file)
        return data


def save_standings():
    file = open("user_points.json", "w+")
    json.dump(user_list, file)
    file.close()


async def connect_to_chat(loop):
    uri = chat_uri + f"username={channel_owner}&password={channel_auth}"

    async with websockets.connect(uri, extra_headers=headers) as websocket_listener:
        print(f"connecting to {uri}")
        asyncio.ensure_future(update_standings())
        if config.get("obs", "fade_text_field"):
            asyncio.ensure_future(display_text_field_loop())
        while True:
            try:
                message = await websocket_listener.recv()
                print("Received from Chat:", message)
                await check_for_message(message)
            except websockets.exceptions.ConnectionClosed:
                print("Connection closed.")
                break


async def send_message(websocket, message):
    message_data = {"type": "chat", "message": message}
    print("Sending message")
    await websocket.send(json.dumps(message_data))


async def send_whisper(websocket, message, user):
    message_data = {"type": "whisper", "displayName": user, "message": message}
    print("Sending message")
    await websocket.send(json.dumps(message_data))


async def check_for_message(message):
    message_content = json.loads(message)
    if message_content["t"] == "un":
        user_name = message_content["m"]["n"]
        print(f"User {user_name} joined!")
        if user_name not in user_list:
            user_list[user_name] = 0
        active_users.append(user_name)
    if message_content["t"] == "ur":
        user_name = message_content["m"]["n"]
        print(f"User {user_name} left!")
        if user_name in active_users:
            active_users.remove(user_name)
    if message_content["t"] == "c":
        chat_message = message_content["m"][0]["m"]
        message_author = message_content["m"][0]["n"]
        print(f"Message {chat_message} from {message_author}")
        check_online_state(message_author)
        await check_for_channel_owner(chat_message, message_author)
        await determine_animation_and_price(chat_message, message_author)

async def check_for_channel_owner(chat_message, message_author):
    if message_author == config.get("picarto", "granter") and '!grant' in chat_message:
        print("Got granting message!")
        split_text = chat_message.split()
        user = split_text[2]
        amount = int(split_text[1])
        if user in user_list:
            user_list[user] += amount
            print(f"Updated {user} to {user_list[user]}")


async def determine_animation_and_price(message, user):
    for animation in animations:
        if animations[animation]["trigger"] in message:
            await spend_points(
                user,
                animations[animation]["price"],
                animations[animation]["file"],
                animations[animation]["coordinates"],
                animations[animation]["scale"],
                animations[animation]["random_position"],
                animations[animation]["random_rotation"],
                animations[animation]["random_scale"],
                str(animation),
                animations[animation]["fade"],
                animations[animation]["static"],
                animations[animation]["fade_time"],
                animations[animation]["volume"],
                animations[animation]["rare_file"],
                animations[animation]["rare_chance"]
            )


async def spend_points(
    user,
    price,
    file,
    coordinates,
    scale,
    random_position,
    random_rotation,
    random_scale,
    animation_name,
    fade,
    static,
    fade_time,
    volume,
    rare_file,
    rare_chance,
):
    if user_list[user] >= price:
        user_list[user] -= price
        await trigger_obs_animation(
            file,
            coordinates,
            scale,
            user,
            random_position,
            random_rotation,
            random_scale,
            animation_name,
            fade,
            static,
            fade_time,
            volume,
            rare_file,
            rare_chance,
        )
        log_redemption(user, animation_name, price)
    elif user_list[user] <= price:
        print(f"{user} does not have enough points to spend!")


def check_online_state(user):
    # if the user is chatting, they're obviously there, so let's make sure they're marked as active
    if user not in active_users:
        active_users.append(user)


async def update_standings():
    frequency = int(config.get("points", "frequency"))
    base = int(config.get("points", "base"))
    boosted = int(config.get("points", "boosted"))
    while True:
        await asyncio.sleep(frequency)
        for user in active_users:
            if user in boosted_users:
                user_list[user] += boosted
            else:
                user_list[user] += base
            print(f"{user} now has {user_list[user]} points!")
        save_standings()
        await update_obs_scroll_text()


async def trigger_obs_animation(
    file,
    coordinates,
    scale,
    user,
    random_position,
    random_rotation,
    random_scale,
    animation_name,
    fade,
    static,
    fade_time,
    volume,
    rare_file,
    rare_chance,
):
    host = config.get("obs", "host")
    port = config.get("obs", "port")
    password = config.get("obs", "password")
    scene_name = config.get("obs", "animation_scene")
    # Let's set the name this spawned animation will have in OBS. Random String to make it unique
    scene_item_name = f"{user}_redeem_{animation_name}_" + get_random_string(8)
    parameters = simpleobsws.IdentificationParameters(
        ignoreNonFatalRequestChecks=False
    )  # Create an IdentificationParameters object (optional for connecting)
    ws = simpleobsws.WebSocketClient(
        url=f"ws://{host}:{port}",
        password={password},
        identification_parameters=parameters,
    )
    await ws.connect()  # Make the connection to obs-websocket
    await ws.wait_until_identified()  # Wait for the identification handshake to complete

    final_file = file
    if rare_file != "":
        if random.random() < rare_chance / 100.0:
            final_file = rare_file

    request = simpleobsws.Request(
        "CreateInput",
        {
            "sceneName": scene_name,
            "inputName": scene_item_name,
            "inputKind": "ffmpeg_source",
            "inputSettings": {"hw_decode": True, "local_file": final_file, "looping": static},
        },
    )
    await ws.call(request)
    print(f"Creating animation {animation_name} for {user}")

    request = simpleobsws.Request(
        "SetInputVolume", 
        {
            "inputName": scene_item_name, 
            "inputVolumeDb" : volume
        }
    )
    await ws.call(request)

    request = simpleobsws.Request("GetSceneItemList", {"sceneName": scene_name})
    scene_items = await ws.call(request)
    if scene_items.ok():  # Check if the request succeeded
        scene_items = json.loads(json.dumps(scene_items.responseData))["sceneItems"]
    else:
        print(scene_items)

    for item in scene_items:
        if item["sourceName"] == scene_item_name:
            scene_item_id = item["sceneItemId"]

    print(f"Requesting scene tree for {scene_name}")

    # queue a cleanup event for the added OBS item or fade it out if needed
    if fade:
        asyncio.ensure_future(fade_out(scene_item_name, fade_time))
    else:
        asyncio.ensure_future(clean_up(scene_item_name))

    final_coordinates = coordinates
    if random_position:
        canvas_width = int(config.get("obs", "canvas_width")) - 420
        canvas_height = int(config.get("obs", "canvas_height")) - 300
        final_coordinates[0] = random.randint(0, canvas_width - 1)
        final_coordinates[1] = random.randint(0, canvas_height - 1)

    final_rotation = 0.0
    if random_rotation:
        print("Random Rotation active!")
        final_rotation = float(random.randint(0, 360))
    print("Final rotation: " + str(final_rotation))

    final_scale = scale
    if random_scale != [1, 1]:
        temp_scale = round(random.uniform(random_scale[0], random_scale[1]), 2)
        final_scale = [temp_scale, temp_scale]

    request = simpleobsws.Request(
        "SetSceneItemTransform",
        {
            "sceneName": scene_name,
            "sceneItemId": scene_item_id,
            "sceneItemTransform": {
                "alignment": 5,
                "boundsAlignment": 0,
                "boundsHeight": 1.0,
                "boundsType": "OBS_BOUNDS_NONE",
                "boundsWidth": 1.0,
                "cropBottom": 0,
                "cropLeft": 0,
                "cropRight": 0,
                "cropTop": 0,
                "height": 100.0,
                "positionX": final_coordinates[0],
                "positionY": final_coordinates[1],
                "rotation": final_rotation,
                "scaleX": final_scale[0],
                "scaleY": final_scale[1],
                "sourceHeight": 100.0,
                "sourceWidth": 100.0,
                "width": 100.0,
            },
        },
    )
    ref = await ws.call(request)
    print(ref)
    print(f"setting transforms for {scene_item_name}")
    await update_obs_scroll_text()


async def update_obs_scroll_text():
    host = config.get("obs", "host")
    port = config.get("obs", "port")
    password = config.get("obs", "password")
    result = []
    for user in user_list:
        if user in active_users:
            result.append(
                f"{user} has {user_list[user]} point{'s' if user_list[user] != 1 else ''}"
            )
    new_text = ", ".join(result)
    await update_text_field(new_text, host, port, password)


async def update_text_field(new_text, host, port, password):
    parameters = simpleobsws.IdentificationParameters(
        ignoreNonFatalRequestChecks=False
    )  # Create an IdentificationParameters object (optional for connecting)
    ws = simpleobsws.WebSocketClient(
        url=f"ws://{host}:{port}",
        password={password},
        identification_parameters=parameters,
    )
    await ws.connect()  # Make the connection to obs-websocket
    await ws.wait_until_identified()  # Wait for the identification handshake to complete

    inputSettings = {"text": new_text}
    request = simpleobsws.Request(
        "SetInputSettings", {"inputName": "Ticker", "inputSettings": inputSettings}
    )
    print(request)
    ret = await ws.call(request)  # Perform the request
    if ret.ok():  # Check if the request succeeded
        print("Request succeeded! Response data: {}".format(ret.responseData))
    else:
        print(ret)

async def display_text_field_loop():
    host = config.get("obs", "host")
    port = config.get("obs", "port")
    password = config.get("obs", "password")
    display_time = int(config.get("obs", "points_display_time"))
    scene = config.get("obs", "animation_scene")
    wait_time = int(config.get("obs", "points_display_interval"))
    parameters = simpleobsws.IdentificationParameters(
        ignoreNonFatalRequestChecks=False
    )
    ws = simpleobsws.WebSocketClient(
        url=f"ws://{host}:{port}",
        password={password},
        identification_parameters=parameters,
    )
    await ws.connect()  
    await ws.wait_until_identified()

    request = simpleobsws.Request("GetSceneItemList", {"sceneName": scene})
    scene_items = await ws.call(request)
    if scene_items.ok():  # Check if the request succeeded
        scene_items = json.loads(json.dumps(scene_items.responseData))["sceneItems"]
    else:
        print(scene_items)

    for item in scene_items:
        if item["sourceName"] == "Ticker":
            scene_item_id = item["sceneItemId"]

    while True:
        print("Waiting for ticker to be displayed ")
        await asyncio.sleep(wait_time)
        print("Displaying ticker now!")
        request = simpleobsws.Request(
            "SetSceneItemEnabled", 
            {
                "sceneName": scene, 
                "sceneItemId": scene_item_id, 
                "sceneItemEnabled": True
            }
        )
        await ws.call(request)
        await asyncio.sleep(display_time)
        print("Hiding Ticker now!")
        request = simpleobsws.Request(
            "SetSceneItemEnabled", 
            {
                "sceneName": scene, 
                "sceneItemId": scene_item_id, 
                "sceneItemEnabled": False
            }
        )
        await ws.call(request)


async def clean_up(id):
    host = config.get("obs", "host")
    port = config.get("obs", "port")
    password = config.get("obs", "password")
    parameters = simpleobsws.IdentificationParameters(
        ignoreNonFatalRequestChecks=False
    )  # Create an IdentificationParameters object (optional for connecting)
    ws = simpleobsws.WebSocketClient(
        url=f"ws://{host}:{port}",
        password={password},
        identification_parameters=parameters,
    )
    await asyncio.sleep(90)
    print(f"Removing redeem item {id}")
    await ws.connect()  # Make the connection to obs-websocket
    await ws.wait_until_identified()  # Wait for the identification handshake to complete
    request = simpleobsws.Request("RemoveInput", {"inputName": id})
    await ws.call(request)


async def fade_out(scene_item, time):
    host = config.get("obs", "host")
    port = config.get("obs", "port")
    password = config.get("obs", "password")
    parameters = simpleobsws.IdentificationParameters(
        ignoreNonFatalRequestChecks=False
    )  # Create an IdentificationParameters object (optional for connecting)
    ws = simpleobsws.WebSocketClient(
        url=f"ws://{host}:{port}",
        password={password},
        identification_parameters=parameters,
    )
    await ws.connect()  # Make the connection to obs-websocket
    await ws.wait_until_identified()  # Wait for the identification handshake to complete
    request = simpleobsws.Request(
        "CreateSourceFilter",
        {
            "sourceName": scene_item,
            "filterName": "fade",
            "filterKind": "color_filter_v2",
            "filterSettings": {"opacity": 1.0},
        },
    )
    await ws.call(request)
    await asyncio.sleep(time)
    num_steps = int(1.0 / 0.02)
    step_size = (1.0 - 0.0) / num_steps
    current_value = 1.0
    for _ in range(num_steps):
        current_value -= step_size
        await asyncio.sleep(0.02)
        request = simpleobsws.Request(
            "SetSourceFilterSettings",
            {
                "sourceName": scene_item,
                "filterName": "fade",
                "filterSettings": {"opacity": current_value},
            },
        )
        await ws.call(request)
    request = simpleobsws.Request("RemoveInput", {"inputName": scene_item})
    await ws.call(request)


def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = "".join(random.choice(letters) for i in range(length))
    return result_str


def log_redemption(user, animation, price):
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    with open("redemption.log", "a") as fd:
        fd.write(f"[{dt_string}] - Redemption of {animation} for {price} by {user} \n")


# Run the WebSocket connection
# asyncio.get_event_loop().run_until_complete(connect_to_chat())
if __name__ == "__main__":
    user_list = get_saved_standings()
    animations = get_animation_definitions()
    boosted_users = get_boosted_users()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(connect_to_chat(loop))
