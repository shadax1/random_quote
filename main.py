import os, random, subprocess
from threading import Thread
import tkinter as tk
from tkinter import ttk
from chat_downloader import ChatDownloader

#paths for the script and audio files
script_path = os.path.dirname(os.path.abspath(__file__)) #path to script"s directory
audio_folder = f"{script_path}{os.path.sep}audio{os.path.sep}"
audio_txt_file = f"{script_path}{os.path.sep}quote.txt"
leaderboard_file = f"{script_path}{os.path.sep}leaderboard.txt"

#globals
thread = None
chat_loop = False
leaderboard = {}

def init():
    #start processing quotes if the ui input is valid
    if twitch_channel.get() != "" and ((selected_radio.get() == 0 and 1 <= percentage.get() <= 100) or (selected_radio.get() == 1 and command.get() != "")):
        channel = f"https://www.twitch.tv/{twitch_channel.get()}"
        try:
            chat = ChatDownloader().get_chat(channel)
            global chat_loop
            chat_loop = True

            disable_widgets()
            load_leaderboard(leaderboard_file)
            root.after(0, update_label, "quotes are now ready", "#00ff2d")

            for message in chat: #chat loop
                process_message(message)

                if not chat_loop: #essentially checks if the Stop button has been pressed (switches chat_loop to False)
                    break #exit the loop

        except Exception:
            button_start.config(state=tk.NORMAL)
            root.after(0, update_label, "invalid URL or site not supported", "#ff390f")
    else:
        button_start.config(state=tk.NORMAL)
        root.after(0, update_label, "missing/invalid info", "#ff390f")

def process_message(message):
    if selected_radio.get() == 0: #probability mode
        rand = random.randint(1, 100)
        bool_command_present = False #to invalidate the upcoming command-boolean check
    else: #command mode
        bool_command_present = command.get() in message["message"] #boolean will say whether the command was present in the chat line
        rand = 101 #bypass random chance check

    if rand <= percentage.get() or bool_command_present:
        username = message["author"]["display_name"]
        random_file = random.choice(os.listdir(audio_folder)) #get a random audio file

        #handle potential search query if command
        if bool_command_present and " " in message["message"].strip():
            lst_search_query = message["message"].split(" ")
            if lst_search_query[-1] != command.get(): #if the command has strings after
                index = lst_search_query.index(command.get()) #get the index of the command
                search_query = ' '.join(lst_search_query[index + 1:])  #join strings after command
                matching_files = [file for file in os.listdir(audio_folder) 
                                    if search_query.lower() in file.lower()] #find matching files based on query
                if matching_files: #if the search yields something
                    random_file = random.choice(matching_files) #get a random audio file from matching files

        #update leaderboards
        leaderboard[username.lower()] = leaderboard.get(username.lower(), 0) + 1 #if doesn't exist, returns 0
        save_leaderboard(leaderboard_file)

        #get user's rank and count
        sorted_leaderboard = sorted(leaderboard.items(), key=lambda item: item[1], reverse=True)  #sort leaderboard
        user_rank = next((rank + 1 for rank, (user, count) in enumerate(sorted_leaderboard) if user == username.lower()), None)  #find user's rank
        user_count = leaderboard[username.lower()]  #get user's count
        rank_suffix = get_rank_suffix(user_rank) #get the appropriate suffix for the user's rank

        #display info
        info = f"{username} ({user_rank}{rank_suffix}/{user_count}) rolled for {random_file}"
        root.after(0, update_label, info, "")

        with open(audio_txt_file, mode="w", encoding="utf-8") as fp_audio_txt_file:
            fp_audio_txt_file.write(info)

        #play the audio file
        play_command = f'mpv --volume={volume.get()} "{audio_folder}{random_file}"'
        if not check_chaos_state.get():
            os.system(play_command) #normal
        else:
            subprocess.Popen(play_command, shell=True) #chaos

        open(audio_txt_file, mode="w").close() #empty audio text file

def load_leaderboard(file_path):
    if os.path.exists(file_path):
        with open(file_path, mode="r", encoding="utf-8") as f:
            for line in f:
                if len(line) > 1:
                    username, count = line.strip().split(": ")
                    leaderboard[username] = int(count)

def save_leaderboard(file_path):
    with open(file_path, mode="w", encoding="utf-8") as f:
        sorted_leaderboard = sorted(leaderboard.items(), key=lambda item: item[1], reverse=True) #sort the leaderboard by count in descending order
        for username, count in sorted_leaderboard:
            f.write(f"{username}: {count}\n")
        f.write("\n")

def get_rank_suffix(rank):
    if 10 <= rank % 100 <= 20:  #handle the special case for 11th, 12th, 13th
        return "th"
    else:
        suffixes = {1: "st", 2: "nd", 3: "rd"}
        return suffixes.get(rank % 10, "th")  #default to "th" for other ranks

def disable_widgets():
    text_twitch_channel.config(state=tk.DISABLED)
    radio_percentage.config(state=tk.DISABLED)
    text_percentage.config(state=tk.DISABLED)
    radio_command.config(state=tk.DISABLED)
    text_command.config(state=tk.DISABLED)
    check_chaos.config(state=tk.DISABLED)
    button_start.config(state=tk.DISABLED)
    button_stop.config(state=tk.NORMAL)

def enable_widgets():
    text_twitch_channel.config(state=tk.NORMAL)
    radio_percentage.config(state=tk.NORMAL)
    radio_command.config(state=tk.NORMAL)
    check_chaos.config(state=tk.NORMAL)
    button_start.config(state=tk.NORMAL)
    button_stop.config(state=tk.DISABLED)
    if selected_radio.get() == 0:
        text_percentage.config(state=tk.NORMAL)
        text_command.config(state=tk.DISABLED)
    else:
        text_command.config(state=tk.NORMAL)
        text_percentage.config(state=tk.DISABLED)

def on_radio_change():
    if selected_radio.get() == 0:
        text_percentage.config(state=tk.NORMAL)
        text_command.config(state=tk.DISABLED)
    else:
        text_command.config(state=tk.NORMAL)
        text_percentage.config(state=tk.DISABLED)

def update_label(info, background_color=""):
    label_info.config(text=info, background=background_color, anchor="center")

def start_thread():
    global thread
    button_start.config(state=tk.DISABLED)
    thread = Thread(target=init)
    thread.start()

def stop_thread():
    global chat_loop
    chat_loop = False
    enable_widgets()
    root.after(0, update_label, "quotes are now disabled", "#0f69ff")

def on_closing():
    if chat_loop: #clean up the thread if closing while quotes are still enabled
        stop_thread()
    root.destroy() #close window

root = tk.Tk()
root.title("Random quotes")
root.resizable(True, False) #width,height

ttk.Label(root, text="Twitch channel:").pack(anchor=tk.W, padx=10, pady=1)
twitch_channel = tk.StringVar()
text_twitch_channel = ttk.Entry(root, textvariable=twitch_channel)
text_twitch_channel.pack(anchor=tk.W, padx=10, pady=1)

ttk.Separator(root, orient="horizontal").pack(fill="x", pady=10)

selected_radio = tk.IntVar()
radio_percentage = ttk.Radiobutton(root, text="All messages have the following probability to trigger a random quote (1 to 100%): ", value=0, variable=selected_radio, command=on_radio_change)
radio_percentage.pack(anchor=tk.W, padx=10, pady=1, fill=tk.X)
percentage = tk.IntVar()
percentage.set(25)
text_percentage = ttk.Entry(root, textvariable=percentage)
text_percentage.pack(anchor=tk.W, padx=10, pady=1)

radio_command = ttk.Radiobutton(root, text="The following command triggers a random quote: ", value=1, variable=selected_radio, command=on_radio_change)
radio_command.pack(anchor=tk.W, padx=10, pady=1, fill=tk.X)
command = tk.StringVar()
command.set("!quote")
text_command = ttk.Entry(root, textvariable=command, state=tk.DISABLED)
text_command.pack(anchor=tk.W, padx=10, pady=1)
selected_radio.set(0)

check_chaos_state = tk.BooleanVar()
check_chaos = ttk.Checkbutton(root, text="Chaos mode (quotes can overlap)", variable=check_chaos_state, onvalue=True, offvalue=False)
check_chaos.pack(anchor=tk.W, padx=10, pady=2, fill=tk.X)

frame = ttk.Frame(root)
frame.pack(fill=tk.BOTH, expand=True, padx=10)

ttk.Label(frame, text="Volume").pack(side=tk.LEFT, padx=(0, 5), pady=(0, 5))
label_volume = ttk.Label(frame, text=100)
label_volume.pack(side=tk.RIGHT, padx=(10, 0))
volume = tk.IntVar()
scale_volume = ttk.Scale(frame, from_=0, to=100, orient="horizontal", variable=volume, command=lambda value: label_volume.config(text=int(float(value))))
scale_volume.pack(side=tk.LEFT, fill=tk.X, expand=True)
scale_volume.set(100)

ttk.Separator(root, orient="horizontal").pack(fill="x", pady=10)

button_start = ttk.Button(root, text="Start", command=lambda: start_thread())
button_start.pack(anchor=tk.W, padx=10, pady=1, fill=tk.X)
button_stop = ttk.Button(root, text="Stop", command=lambda: stop_thread(), state=tk.DISABLED)
button_stop.pack(anchor=tk.W, padx=10, pady=1, fill=tk.X)

label_info = ttk.Label(root, font=("Consolas", 20), relief="sunken")
label_info.pack(anchor=tk.W, fill="x", padx=10, pady=10)

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop() #ensures the main window remains visible on the screen
