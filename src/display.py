import tkinter as tk
from tkinter import filedialog
import json

from src.steamGifts import SteamGifts
from src.log_colors import *
import sys


class Display(tk.Tk):
    config = dict()
    log_counter = 0
    sg_bot = None

    # The profile session side-panel.
    current_session_username = None
    current_session_level = None
    current_session_points = None

    # The mining session side-panel.
    current_session_entries = None
    current_session_total_points = None
    current_session_entered = None

    # Settings side-panel.
    settings_start_startup = None
    settings_auto_quit = None

    def __init__(self):
        super().__init__()

        # Set the window defaults.
        self.title('SteamGifts Giveaway Enter Tool')
        self.minsize(640, 480)
        self.geometry("640x480")
        # First load the config files.
        self.load_config()

        self.main = tk.Frame(self)
        self.main.pack(fill=tk.BOTH, expand=1, padx=5, pady=5)

        # Create the import window.
        import_group = tk.LabelFrame(self.main, text="Import Settings", fg="steel blue")
        import_group.grid(row=0, column=0, columnspan=2, sticky=tk.NSEW, ipadx=5, ipady=5)
        tk.Grid.columnconfigure(import_group, 1, weight=1)

        # Create the PATH fill-in field.
        tk.Label(import_group, text="Google Chrome Profile Path:").grid(row=0, sticky=tk.NSEW)
        self.entry_chrome_profile_path = tk.Entry(import_group, text=self.config["chrome-profile-path"])
        self.entry_chrome_profile_path.grid(row=0, column=1, sticky=tk.NSEW, )
        self.entry_chrome_profile_path.insert(0, self.config["chrome-profile-path"])
        btn_browse_profile_directory = tk.Button(import_group, text="Browse", command=self.browse_button)
        btn_browse_profile_directory.grid(row=0, column=2, padx=(10, 5))

        # Make the grid expand.
        tk.Grid.rowconfigure(self.main, 4, weight=1)
        tk.Grid.columnconfigure(self.main, 1, weight=1)

        # Create the enter and  quit button
        tk.Button(self.main, text='Enter Giveaways', command=self.enter, bg="green yellow").grid(row=5, sticky=tk.NSEW)
        tk.Button(self.main, text='Quit', command=self.quit_application, bg="salmon").grid(row=6, sticky=tk.NSEW,
                                                                                           pady=4)

        # Create the scroll text field.
        text_container = tk.Frame(self.main, borderwidth=1, relief="sunken", background="white")
        self.log = tk.Listbox(text_container, width=24, height=13, borderwidth=0, highlightthickness=0)
        text_vsb = tk.Scrollbar(text_container, orient="vertical", command=self.log.yview)
        text_hsb = tk.Scrollbar(text_container, orient="horizontal", command=self.log.xview)
        self.log.configure(yscrollcommand=text_vsb.set, xscrollcommand=text_hsb.set)
        self.log.bindtags((self.log, self, "all"))

        self.log.grid(row=0, column=0, sticky=tk.NSEW, pady=10, padx=10)
        text_vsb.grid(row=0, column=1, sticky=tk.NS)
        text_hsb.grid(row=1, column=0, sticky=tk.EW)

        border_pixel = tk.Frame(text_container, background=self.cget("background"))
        border_pixel.grid(row=1, column=1, sticky=tk.NSEW)

        text_container.grid_rowconfigure(0, weight=1)
        text_container.grid_columnconfigure(0, weight=1)

        text_container.grid(column=1, row=1, rowspan=6, padx=(10, 0), sticky=tk.NSEW)

        # Create the profile display left navbar.
        self.create_profile_display()

        # Create the mining display left navbar.
        self.create_mining_display()

        # Create settings display.
        self.create_settings_display()

        # Add entry text to the console log.
        self.log_console_text("Welcome to the steamGifts auto enter bot!", log_verbose)
        self.log_console_text("To start, first select the custom Chrome profile at the top.")
        self.log_console_text("Make sure that the profile is already logged in to SteamGifts.")
        self.log_console_text("Simply press \"Enter Giveaways\" to enter giveaways automatically.")
        self.log_console_text("Good luck!")

        # Auto start giveaways if option is enabled
        if self.config["settings"]["auto_start"] == 1:
            self.enter()

        # Dirty load some steam app info
        tk.mainloop()

    def quit_application(self):
        self.quit()
        sys.exit()

    def create_profile_display(self):
        # Create the profile.
        import_group = tk.LabelFrame(self.main, text="Profile", fg="steel blue")
        import_group.grid(row=1, column=0, sticky=tk.NSEW, ipadx=5, ipady=5)

        self.current_session_username = tk.StringVar(value="<Not initialized>")
        self.current_session_level = tk.StringVar(value="<?>")
        self.current_session_points = tk.StringVar(value="<?>")

        # Create the labels
        tk.Label(import_group, textvariable=self.current_session_username, anchor=tk.CENTER) \
            .grid(row=0, column=0, columnspan=2)
        tk.Label(import_group, text="Level:", font='Helvetica 10 bold', anchor=tk.W) \
            .grid(row=1, column=0, sticky=tk.EW)
        tk.Label(import_group, textvariable=self.current_session_level, anchor=tk.W) \
            .grid(row=1, column=1, sticky=tk.EW)
        tk.Label(import_group, text="Points:", font='Helvetica 10 bold', anchor=tk.W) \
            .grid(row=2, column=0, sticky=tk.EW)
        tk.Label(import_group, textvariable=self.current_session_points, anchor=tk.W) \
            .grid(row=2, column=1, sticky=tk.EW)

    def update_profile_display(self, profile):
        self.current_session_username.set(profile["name"])
        self.current_session_level.set(str(profile["level"]))
        self.current_session_points.set(str(profile["points"]))

    def create_mining_display(self):
        # Create the profile.
        import_group = tk.LabelFrame(self.main, text="Mining Session", fg="steel blue")
        import_group.grid(row=2, column=0, sticky=tk.NSEW, ipadx=5, ipady=5)

        self.current_session_entries = tk.StringVar(value="0")
        self.current_session_total_points = tk.StringVar(value="0")
        self.current_session_entered = tk.StringVar(value="0")

        # Create the labels
        tk.Label(import_group, text="Giveaways:", font='Helvetica 10 bold', anchor=tk.W) \
            .grid(row=0, column=0, sticky=tk.EW)
        tk.Label(import_group, textvariable=self.current_session_entries, anchor=tk.W) \
            .grid(row=0, column=1, sticky=tk.EW)
        tk.Label(import_group, text="Total Points:", font='Helvetica 10 bold', anchor=tk.W) \
            .grid(row=1, column=0, sticky=tk.EW)
        tk.Label(import_group, textvariable=self.current_session_total_points, anchor=tk.W) \
            .grid(row=1, column=1, sticky=tk.EW)
        tk.Label(import_group, text="Entered:", font='Helvetica 10 bold', anchor=tk.W) \
            .grid(row=2, column=0, sticky=tk.EW)
        tk.Label(import_group, textvariable=self.current_session_entered, anchor=tk.W) \
            .grid(row=2, column=1, sticky=tk.EW)

    def update_current_mining_display(self, entries, points):
        self.current_session_entries.set(str(entries))
        self.current_session_total_points.set(str(points))

    def create_settings_display(self):
        import_group = tk.LabelFrame(self.main, text="Settings", fg="steel blue")
        import_group.grid(row=3, column=0, sticky=tk.NSEW, ipadx=5, ipady=5)

        self.settings_start_startup = tk.IntVar(value=self.config["settings"]["auto_start"])
        self.settings_auto_quit = tk.IntVar(value=self.config["settings"]["auto_quit"])
        tk.Checkbutton(import_group,
                       text="Enter on start",
                       variable=self.settings_start_startup,
                       command=self.on_settings_auto_start, anchor=tk.W).pack(side=tk.TOP, fill=tk.BOTH)
        tk.Checkbutton(import_group,
                       text="Quit on complete",
                       variable=self.settings_auto_quit,
                       command=self.on_settings_auto_quit, anchor=tk.W).pack(side=tk.TOP, fill=tk.BOTH)

    def on_settings_auto_start(self):
        self.config["settings"]["auto_start"] = self.settings_start_startup.get()
        self.store_config()

    def on_settings_auto_quit(self):
        self.config["settings"]["auto_quit"] = self.settings_auto_quit.get()
        self.store_config()

    def browse_button(self):
        # Get a directory.
        directory = tk.filedialog.askdirectory()

        # Check if there was a directory, user can still press cancel.
        if directory:
            # Store the config directory.
            self.config["chrome-profile-path"] = directory

            # Save the directory.
            self.store_config()

            # Make the entry change text.
            self.entry_chrome_profile_path.delete(0, tk.END)
            self.entry_chrome_profile_path.insert(0, self.config["chrome-profile-path"])

    def load_config(self):
        with open('config.json') as f:
            self.config = json.load(f)

    def store_config(self):
        with open('config.json', 'w') as f:
            json.dump(self.config, f)

    def log_console_text(self, text, config=None):
        # Split the lines.
        split_lines = str(text).split("\n")

        # Add each line separately to the log.
        for split_line in split_lines:
            # Normal console log.
            print(split_line)

            # Insert the line.
            self.log.insert(tk.END, split_line)

            # Set the coloring.
            if config is not None:
                self.log.itemconfig(self.log_counter, config)

            # Increment the counter.
            self.log_counter = self.log_counter + 1

            # Auto move the yview
            self.log.yview_moveto(1)
            self.update()

    def enter(self):
        self.log_console_text("\nStarting the SteamGifts enter bot.", config=log_verbose)

        # Start the bot TODO: Add multi-threading to allow functioning GUI.
        self.sg_bot = SteamGifts(self.config, self)

    def show_entry_fields(self):
        print("First Name: %s" % (self.entry_chrome_profile_path.get()))


Display()
