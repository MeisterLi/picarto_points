# Picarto channel points

This project aims to replicate a feature called "Channel points", as they are known on Twitch, by using the picarto chat bot and OBS APIs. It's aimed to be simple to use and configure, and extendable. Pull requests are welcome!

# How does it work?
Users active in the chat will get awarded points in a specified frequency that can then be spent on 'rewards' such as animations, videos or sounds playing in the stream via OBS. The redemption works via chat commands and the current standings are pushed to a text field in OBS automatically.

A demonstration can be found here:
https://youtu.be/zOGortptFzo

# Installation
After downloading all files, you will have to make sure you have Python 3 installed on your system, alongside pip. Both are open source and free to use and what I used to make this tool.

## Dependencies
### Pip
To install all required modules in your python installation, open a terminal/console in the folder you put this project's files in and run:
```
pip install -r requirements.txt
```
### OBS
You also have to have the OBS Websocket Server active and configured in OBS itself. Also make sure to use OBS version 28 or newer. You should also have a text field called "Ticker" in your OBS setup to push point standings to. It does not need to be visible at all times however.

### Picarto
You need to have a Picarto account and a Chat Bot auth code. You can request one after logging in here:
https://oauth.picarto.tv/chat/bot

## Config

The configuraiton is stored in the config.ini. Below is a breakdown of all settings:

### OBS section:
*host* - The IP of the host your OBS installation is running on. Typically this is localhost or 172.0.0.1 if it's not a different computer than the one you're on.  
*port* - Same as above, but the port  
*password* - Password set for the OBS websocket server. Leave blank if authorization is not active in OBS  
*animation_scene* - Name of the Scene animations are to be spawned in.  
*canvas_width* - Width of the OBS canvas. Most times this will be 1920  
*canvas_height* - Height of the OBS canvas. Most times this will be 1080  

### Picarto section:
*channel_auth* - The Authorization for your Picarto Chat Bot  
*channel_owner* - The Name of your channel / your username

### Points section:
*base* - Base number of points earned by a user in your Picarto chat  
*boosted* - Number of points earned by a user in your Picarto chat if the user is present in the file *boosted_users.json*  
*frequency* - The Frequency in seconds those points are given out at

## Animations
Animation information is stored in the animations.json file. The fields have the following function:  

*name* (in the example file, this is 'bounce') - name of an animation  
*file* - path to the local file to be used by OBS as a media source. This can be a mp4, png, jpg, gif, animated png or gif, sound file and others.  
*coordinates* - two entry array of x and y coordinates the animation should be spawned at on the OBS canvas  
*scale* - two entry array of x and y scale values for the spawned object  
*trigger* - word a user will have to type into the chat to redeem the animation  
*price* - point cost for the animation  
*random_position* - if the position of the spawned animation should be randomized  
*random_rotation* - if the rotation of the spawned animation should be randomized  
*fade* - should the spawned animation fade away after 3 seconds?  
*static* - should the animation stop being displayed after one play or loop? (useful for static images in combination with fade)  

## Other files 
*boosted_users.json* - contains an array of usernames that will get awarded with the boosted amount defined in config.ini  
*redemptions.log* - contains a log of redemptions with time stamps  
*user_points.json* - contains users and their current point standings  

# Running
Make sure OBS is running and all needed data is set in the config.ini. Then go to the folder these files are located with your console or terminal and type:

```
python picartoBot.py
```
to start.

# Limitations
- The chat bot can only see channel join and leave events, so it should ideally be started before the stream is started. That said, there is a small check when a user writes something in the chat, to make sure they're still being tracked as 'active'  
- The user standings are saved with each update, such as gaining points and spending, but not continuously.

# Requests
Feel free to post requests for changes or make pull requests if you have a good idea on how to improve this tool
# Support
If you'd like to support my coding adventures, feel free to buy me a Ko-Fi!
https://ko-fi.com/meisterlitweet6607
