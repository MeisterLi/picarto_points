# Picarto channel points

This project aims to replicate a feature called "Channel points", as they are known on Twitch, by using the picarto chat bot and OBS APIs. It's aimed to be simple to use and configure, and extendable. Pull requests are welcome!

# How does it work?
Users active in the chat will get awarded points in a specified frequency that can then be spent on 'rewards' such as animations, videos or sounds playing in the stream via OBS. The redemption works via chat commands and the current standings are pushed to a text field in OBS automatically.

A demonstration can be found here:  
https://youtu.be/zOGortptFzo

A video detailing added functions since the video is here:  
https://youtu.be/BkP37RF6LFc  

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
*friends_scene* - Name of the Scene friends are set up in (see 'friends' section in picarto)  
*ticker_scene* - Name of the Scene the Ticker is set up in  
*canvas_width* - Width of the OBS canvas. Most times this will be 1920  
*canvas_height* - Height of the OBS canvas. Most times this will be 1080  
*points_display_time* - if fade_text_field is "True", this will determined how long we will display the ticker  
*points_display_interval* - if fade_text_field is "True", this will determined how long we will hide the ticker  
*fade_text_field* - Should we hide/show the Ticker in a loop?

### Picarto section:
*channel_auth* - The Authorization for your Picarto Chat Bot  
*channel_owner* - The Name of your channel / your username  
*granter* - a user that is able to use !grant in the chat to grant points manually, such as:  
```
!grant 300 Maniko
```
This uses the channel name, not the account name!  
*friends* - an array of usernames that are set up in OBS as friends. Upon joining, the scene item in the scene defined in friends_scene matching their name will be activated and disabled on leaving

### Points section:
*base* - Base number of points earned by a user in your Picarto chat  
*boosted* - Number of points earned by a user in your Picarto chat if the user is present in the file *boosted_users.json*  
*frequency* - The Frequency in seconds those points are given out at

### Web section:
*url* - Url to push updates to.
*key* - key setup to authenticate legitimate pushes

## Animations
Animation information is stored in the animations.json file. The fields have the following function:  

*name* (in the example file, this is 'bounce') - name of an animation  
*file* - path to the local file to be used by OBS as a media source. This can be a mp4, png, jpg, gif, animated png or gif, sound file and others. This can also be an array to spawn multiple items. Note that sound files by default will only be played once.  
*coordinates* - two entry array of x and y coordinates the animation should be spawned at on the OBS canvas  
*scale* - two entry array of x and y scale values for the spawned object  
*trigger* - word a user will have to type into the chat to redeem the animation  
*price* - point cost for the animation  
*random_position* - if the position of the spawned animation should be randomized  
*random_rotation* - if the rotation of the spawned animation should be randomized  
*random_scale* - an array of two scales to randomize between - set to [1.0, 1.0] for no variation  
*fade* - should the spawned animation fade away after 3 seconds?  
*static* - should the animation stop being displayed after one play or loop? (useful for static images in combination with fade)  
*fade_time* - Time before we fade the item  
*volume* - Volume in dB to spawn the media item at (such as video or music)  
*rare_file* - Alternative "rare" file to chose if rare_chance is hit  
*rare_chance* - Chance for the "rare" file to be chosen

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

# Chat commands
There are some universal chat commands that can be performed:  
*!points* - will send a whisper to the user with their current point standing  
*!grant 'X' 'user'* - if the sender of this message is the granter as defined in the config, this will grant the X amount of points to the mentioned user. An example would be *!grant 30 Maniko*  

# Website display
You might want to set up a website with a list of current standings, which I have some examples for in web_app, using a very basic site template using socket-io to update the page and a flask app written in python. Make sure to edit the 'web' section in the config if you'd like.

*/clear* - requires pw  - The endpoint /clear is used to clear the current list
*/new_data* - requires pw and array of lists - The endpoint /new_data is used to update the list with all current standings
*/update* - requires no data - forces an update of the list via websocket to bring the page up to date


# Limitations
- The chat bot can only see channel join and leave events, so it should ideally be started before the stream is started. That said, there is a small check when a user writes something in the chat, to make sure they're still being tracked as 'active'  
- The user standings are saved with each update, such as gaining points and spending, but not continuously.

# Requests
Feel free to post requests for changes or make pull requests if you have a good idea on how to improve this tool
# Support
If you'd like to support my coding adventures, feel free to buy me a Ko-Fi!
https://ko-fi.com/meisterlitweet6607
