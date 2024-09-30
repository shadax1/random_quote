import os, random, subprocess
from time import sleep
from threading import Thread
import tkinter as tk
from tkinter import ttk
from chat_downloader import ChatDownloader

script_path = os.path.dirname(os.path.abspath(__file__)) #path to script"s directory
quotes_folder = f"{script_path}{os.path.sep}audio{os.path.sep}"
quotes_file = f"{script_path}{os.path.sep}quote.txt"

thread = None
chat_loop = False

def quotes():
    if twitch_channel.get() != "" and ((selected_radio.get() == 0 and 1 <= percentage.get() <= 100) or (selected_radio.get() == 1 and command.get() != "")):
        channel = f"https://www.twitch.tv/{twitch_channel.get()}"
        try:
            chat = ChatDownloader().get_chat(channel)
            global chat_loop
            chat_loop = True
            disable_widgets()
            label_info.config(text="quotes are now ready", background="#00ff2d", anchor="center")

            for message in chat: #chat loop
                if selected_radio.get() == 0: #probability
                    rand = random.randint(1, 100)
                    bool_command_present = False #to invalidate the upcoming command-boolean check
                else: #command
                    bool_command_present = command.get() in message["message"] #boolean will say whether the command was present in the chat line
                    rand = 101 #to invalidate the upcoming random-chance check

                if rand <= percentage.get() or bool_command_present:
                    username = message["author"]["display_name"]
                    random_file = random.choice(os.listdir(quotes_folder)) #get random quote
                    label_info.config(text=f"{username} rolled for {random_file}", background="", anchor="center") #display message
                    with open(quotes_file, mode="wt", encoding="utf-8") as fp_quotes:
                        fp_quotes.write(f"{username} rolled for {random_file}")
                    #play random quote
                    if not check_chaos_state.get():
                        os.system(f'mpv --volume={volume.get()} "{quotes_folder}{random_file}"') #normal
                    else:
                        subprocess.Popen(f'mpv --volume={volume.get()} "{quotes_folder}{random_file}"', shell=True) #chaos
                if not chat_loop: #essentially checks if the Stop button has been pressed (switches chat_loop to False)
                    break #exit the loop
            sleep(0.1)
        except:
            button_start.config(state=tk.NORMAL)
            label_info.config(text="invalid URL or site not supported", background="#ff390f", anchor="center")
    else:
        button_start.config(state=tk.NORMAL)
        label_info.config(text="missing/invalid info", background="#ff390f", anchor="center")

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

def start_thread(thread):
    button_start.config(state=tk.DISABLED)
    thread = Thread(target=quotes, args=[])
    thread.start()

def stop_thread():
    global chat_loop
    chat_loop = False
    enable_widgets()
    label_info.config(text="quotes are now disabled", background="#0f69ff", anchor="center")

def on_radio_change():
    if selected_radio.get() == 0:
        text_percentage.config(state=tk.NORMAL)
        text_command.config(state=tk.DISABLED)
    else:
        text_command.config(state=tk.NORMAL)
        text_percentage.config(state=tk.DISABLED)

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
volume = tk.IntVar()
scale_volume = ttk.Scale(frame, from_=0, to=100, orient="horizontal", variable=volume, command=lambda value: label_volume.config(text=int(float(value))))
scale_volume.pack(side=tk.LEFT, fill=tk.X, expand=True)
scale_volume.set(100)
label_volume = ttk.Label(frame, text=100)
label_volume.pack(side=tk.RIGHT, padx=(10, 0))

ttk.Separator(root, orient="horizontal").pack(fill="x", pady=10)

button_start = ttk.Button(root, text="Start", command=lambda: start_thread(thread))
button_start.pack(anchor=tk.W, padx=10, pady=1, fill=tk.X)
button_stop = ttk.Button(root, text="Stop", command=lambda: stop_thread(), state=tk.DISABLED)
button_stop.pack(anchor=tk.W, padx=10, pady=1, fill=tk.X)

label_info = ttk.Label(root, font=("Consolas", 20), relief="sunken")
label_info.pack(anchor=tk.W, fill="x", padx=10, pady=10)

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop() #ensures the main window remains visible on the screen
