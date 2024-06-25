import os, random, subprocess
from time import sleep
from threading import Thread
import tkinter as tk
from tkinter import ttk

script_path = os.path.dirname(os.path.abspath(__file__)) #path to script"s directory
quotes_folder = f"{script_path}{os.path.sep}audio{os.path.sep}"
chatty_log_folder = f"{os.path.expanduser('~')}{os.path.sep}.chatty{os.path.sep}logs{os.path.sep}"
quotes_file = f"{script_path}{os.path.sep}quote.txt"

thread = None
infinite_loop = False

def get_last_line(file):
    with open(file, "rb") as f:
        try:  #catch OSError in case of a one line file 
            f.seek(-2, os.SEEK_END)
            while f.read(1) != b"\n":
                f.seek(-2, os.SEEK_CUR)
        except OSError:
            f.seek(0)
        return f.readline().decode()

def quotes():
    if twitch_channel.get() != "" and ((selected_radio.get() == 0 and 1 <= percentage.get() <= 100) or (selected_radio.get() == 1 and command.get() != "")):
        log_file = f"{chatty_log_folder}#{twitch_channel.get()}.log"
        try:
            line_amount = sum(1 for _ in open(log_file, mode="rt", encoding="utf-8"))
            global infinite_loop
            infinite_loop = True
            disable_widgets()
            label_info.config(text="quotes are now ready", background="#00ff2d", anchor="center")

            while infinite_loop:
                open(quotes_file, mode="wt", encoding="utf-8").close()
                if line_amount != sum(1 for _ in open(log_file, mode="rt", encoding="utf-8")):
                    last_line = get_last_line(log_file)

                    if selected_radio.get() == 0: #probability
                        rand = random.randint(1, 100)
                        bool_command_present = False #to invalidate the upcoming command-boolean check
                    else: #command
                        bool_command_present = command.get() in last_line #boolean will say whether the command was present in the chat line
                        rand = 101 #to invalidate the upcoming random-chance check

                    if rand <= percentage.get() or bool_command_present:
                        #get username
                        temp = last_line.split("] <")
                        temp = temp[-1].split(">")
                        username = temp[0]
                        while username[0] == "!" or username[0] == "+" or username[0] == "$" or username[0] == "@" or username[0] == "~" or username[0] == "%":
                            username = username[1:]
                        
                        random_file = random.choice(os.listdir(quotes_folder)) #get random quote
                        label_info.config(text=f"{username} rolled for {random_file}", background="", anchor="center") #display message
                        with open(quotes_file, mode="wt", encoding="utf-8") as fp_quotes:
                            fp_quotes.write(f"{username} rolled for {random_file}")
                        #play random quote
                        if not check_chaos_state.get():
                            os.system(f'mpv "{quotes_folder}{random_file}"') #normal
                        else:
                            subprocess.Popen(f'mpv "{quotes_folder}{random_file}"', shell=True) #chaos
                    line_amount += 1
                sleep(0.1)
        except FileNotFoundError:
            label_info.config(text="missing/invalid info", background="#ff390f", anchor="center")
    else:
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
    thread = Thread(target=quotes, args=[])
    thread.start()

def stop_thread():
    global infinite_loop
    infinite_loop = False
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
    if infinite_loop: #clean up the thread if closing while quotes are still enabled
        stop_thread()
    root.destroy() #close window

root = tk.Tk()
root.title("Random quotes")
root.geometry("1000x316+75+300") #widthxheight±x±y
#root.geometry("1000x303+75+300") #widthxheight±x±y
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
check_chaos.pack(anchor=tk.W, padx=10, pady=1, fill=tk.X)

ttk.Separator(root, orient="horizontal").pack(fill="x", pady=10)

button_start = ttk.Button(root, text="Start", command=lambda: start_thread(thread))
button_start.pack(anchor=tk.W, padx=10, pady=1, fill=tk.X)
button_stop = ttk.Button(root, text="Stop", command=lambda: stop_thread(), state=tk.DISABLED)
button_stop.pack(anchor=tk.W, padx=10, pady=1, fill=tk.X)
label_info = ttk.Label(root, font=("Consolas", 20), relief="sunken")
label_info.pack(anchor=tk.W, fill="x", padx=10, pady=5)
root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop() #ensures the main window remains visible on the screen
