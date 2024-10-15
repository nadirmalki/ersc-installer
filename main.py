import os
import zipfile
import shutil
import requests
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


# Function to get the URL of the latest version of the .zip file
def get_latest_release_zip_url():
    latest_url = "https://github.com/LukeYui/EldenRingSeamlessCoopRelease/releases/latest"
    response = requests.get(latest_url, allow_redirects=True)
    final_url = response.url
    zip_url = final_url.replace('/tag/', '/download/') + "/ersc.zip"
    return zip_url


# Function to show the loading screen with a progress bar
def show_loading_screen():
    loading_screen = tk.Toplevel(root)
    loading_screen.title("Loading...")
    loading_screen.geometry("350x100")  # Size of the loading screen
    loading_label = tk.Label(loading_screen, text="Downloading, please wait...")
    loading_label.pack(padx=20, pady=10)

    progress_bar = ttk.Progressbar(loading_screen, orient="horizontal", mode="determinate", length=300)
    progress_bar.pack(padx=20, pady=10)

    loading_screen.grab_set()  # Prevent interaction with the main window
    loading_screen.transient(root)  # Keep the main window above
    return loading_screen, progress_bar


# Function to download and extract files, updating the progress bar
def download_and_extract():
    # Show the loading screen with progress bar
    loading_screen, progress_bar = show_loading_screen()

    zip_url = get_latest_release_zip_url()
    zip_file_path = "repo_ersc.zip"

    print(f"Downloading {zip_url} ...")

    # Download the file with progress management
    response = requests.get(zip_url, stream=True)
    total_length = int(response.headers.get('content-length'))

    with open(zip_file_path, "wb") as file:
        downloaded = 0
        for data in response.iter_content(chunk_size=4096):
            file.write(data)
            downloaded += len(data)
            progress_bar['value'] = (downloaded / total_length) * 100
            root.update_idletasks()  # Update the GUI
    print(f"Downloaded {zip_file_path}")

    # Extract the downloaded file
    extract_dir = "extracted"
    os.makedirs(extract_dir, exist_ok=True)

    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    print(f"Extracted files to {extract_dir}")

    # Update the language dropdown
    update_language_dropdown(extract_dir)

    # Delete the downloaded zip file
    os.remove(zip_file_path)

    # Close the loading screen once the download is finished
    loading_screen.destroy()

    return extract_dir


# Function to copy files to the destination directory
def copy_files(extract_dir):
    destination_dir = filedialog.askdirectory(title="Choose the destination folder")
    if not destination_dir:
        messagebox.showwarning("No folder selected", "You must select a destination folder.")
        return

    for root_dir, dirs, files in os.walk(extract_dir):
        relative_path = os.path.relpath(root_dir, extract_dir)
        target_dir = os.path.join(destination_dir, relative_path)
        os.makedirs(target_dir, exist_ok=True)
        for file in files:
            file_path = os.path.join(root_dir, file)
            target_file_path = os.path.join(target_dir, file)
            if os.path.exists(target_file_path):
                os.remove(target_file_path)
            shutil.copy(file_path, target_file_path)

    print(f"Files and folders copied to {destination_dir}")

    seamless_coop_dir = os.path.join(destination_dir, "SeamlessCoop")
    ini_file_path = os.path.join(seamless_coop_dir, "ersc_settings.ini")

    if os.path.exists(ini_file_path):
        with open(ini_file_path, "r") as ini_file:
            lines = ini_file.readlines()

        with open(ini_file_path, "w") as ini_file:
            for line in lines:
                if line.startswith("cooppassword"):
                    ini_file.write(f"cooppassword = {password_entry.get()}\n")
                elif line.startswith("mod_language_override"):
                    # Only write the language if it's not "default"
                    if language_var.get() != "default":
                        ini_file.write(f"mod_language_override = {language_var.get()}\n")
                    else:
                        ini_file.write("mod_language_override = \n")
                elif line.startswith("allow_invaders"):
                    ini_file.write(f"allow_invaders = {1 if invaders_var.get() else 0}\n")
                elif line.startswith("death_debuffs"):
                    ini_file.write(f"death_debuffs = {1 if death_debuffs_var.get() else 0}\n")
                elif line.startswith("allow_summons"):
                    ini_file.write(f"allow_summons = {1 if summons_var.get() else 0}\n")
                elif line.startswith("skip_splash_screens"):
                    ini_file.write(f"skip_splash_screens = {1 if skip_splash_var.get() else 0}\n")
                elif line.startswith("default_boot_master_volume"):
                    ini_file.write(f"default_boot_master_volume = {master_volume_var.get()}\n")
                elif line.startswith("enemy_health_scaling"):
                    ini_file.write(f"enemy_health_scaling = {enemy_health_scaling_var.get()}\n")
                elif line.startswith("enemy_damage_scaling"):
                    ini_file.write(f"enemy_damage_scaling = {enemy_damage_scaling_var.get()}\n")
                elif line.startswith("enemy_posture_scaling"):
                    ini_file.write(f"enemy_posture_scaling = {enemy_posture_scaling_var.get()}\n")
                elif line.startswith("boss_health_scaling"):
                    ini_file.write(f"boss_health_scaling = {boss_health_scaling_var.get()}\n")
                elif line.startswith("boss_damage_scaling"):
                    ini_file.write(f"boss_damage_scaling = {boss_damage_scaling_var.get()}\n")
                elif line.startswith("boss_posture_scaling"):
                    ini_file.write(f"boss_posture_scaling = {boss_posture_scaling_var.get()}\n")
                else:
                    ini_file.write(line)
        print(f"Updated settings in {ini_file_path}")
    else:
        print(f"File {ini_file_path} not found!")

    shutil.rmtree(extract_dir)
    print("Cleaned up temporary files.")

    messagebox.showinfo("Completed", f"Files extracted and copied successfully to the folder: {destination_dir}")
    root.destroy()


# Function to handle the window close event
def on_close():
    if os.path.exists("extracted"):
        shutil.rmtree("extracted")
        print("Temporary folder removed.")
    root.destroy()


def toggle_advanced_settings():
    if install_type_var.get() == "advanced":
        advanced_frame.pack(pady=10)
    else:
        advanced_frame.pack_forget()


def load_languages(locale_dir):
    languages = ["default"]  # Add "default" as the first option
    for filename in os.listdir(locale_dir):
        if filename.endswith('.json'):
            language = os.path.splitext(filename)[0]  # Remove the .json extension
            languages.append(language)
    return languages


# This function updates the language dropdown once the files have been extracted to the temporary folder
def update_language_dropdown(extract_dir):
    locale_dir = os.path.join(extract_dir, "SeamlessCoop", "locale")
    if os.path.exists(locale_dir):
        languages = load_languages(locale_dir)
        if not languages:
            print("No language files found in the locale folder.")
        else:
            print(f"Languages found: {languages}")
        language_dropdown['values'] = languages
        language_dropdown.current(0)  # Select the first default value
    else:
        print(f"Directory {locale_dir} not found!")


# Main function to handle the complete process
def start_process():
    extract_dir = download_and_extract()
    if extract_dir:
        # Enable the button to copy files after languages have been updated
        copy_button.config(state=tk.NORMAL)


# Create the GUI with Tkinter
root = tk.Tk()
root.title("ersc installer")

# Bind the close function to the main window
root.protocol("WM_DELETE_WINDOW", on_close)

# Section for selecting the installation type
install_type_var = tk.StringVar(value="quick")
install_type_frame = tk.Frame(root)
install_type_frame.pack(pady=10)

tk.Label(install_type_frame, text="Installation type:").pack(side=tk.LEFT)

install_type_quick = tk.Radiobutton(install_type_frame, text="Quick", variable=install_type_var, value="quick",
                                    command=toggle_advanced_settings)
install_type_quick.pack(side=tk.LEFT)

install_type_advanced = tk.Radiobutton(install_type_frame, text="Advanced", variable=install_type_var, value="advanced",
                                       command=toggle_advanced_settings)
install_type_advanced.pack(side=tk.LEFT)

# Add a label and an entry field to input the password
tk.Label(root, text="Enter the password for coop:").pack(pady=10)
password_entry = tk.Entry(root)
password_entry.pack(pady=10)

# Add a label and a dropdown menu to select the language
tk.Label(root, text="Select a language:").pack(pady=10)
language_var = tk.StringVar(value="default")  # Default to "default"
language_dropdown = ttk.Combobox(root, textvariable=language_var)
language_dropdown.pack(pady=10)

# Frame for advanced settings
advanced_frame = tk.Frame(root)

# Checkboxes for gameplay settings
invaders_var = tk.BooleanVar(value=True)
death_debuffs_var = tk.BooleanVar(value=True)
summons_var = tk.BooleanVar(value=True)
skip_splash_var = tk.BooleanVar(value=False)

tk.Checkbutton(advanced_frame, text="Allow invaders", variable=invaders_var).pack(anchor=tk.W)
tk.Checkbutton(advanced_frame, text="Death debuffs", variable=death_debuffs_var).pack(anchor=tk.W)
tk.Checkbutton(advanced_frame, text="Allow summons", variable=summons_var).pack(anchor=tk.W)
tk.Checkbutton(advanced_frame, text="Skip splash screens", variable=skip_splash_var).pack(anchor=tk.W)

# Advanced settings
master_volume_var = tk.IntVar(value=5)
enemy_health_scaling_var = tk.IntVar(value=35)
enemy_damage_scaling_var = tk.IntVar(value=0)
enemy_posture_scaling_var = tk.IntVar(value=15)
boss_health_scaling_var = tk.IntVar(value=100)
boss_damage_scaling_var = tk.IntVar(value=0)
boss_posture_scaling_var = tk.IntVar(value=20)

tk.Label(advanced_frame, text="Startup volume (0-10):").pack(anchor=tk.W)
tk.Scale(advanced_frame, from_=0, to=10, variable=master_volume_var, orient=tk.HORIZONTAL).pack(anchor=tk.W)

tk.Label(advanced_frame, text="Enemy health (% per player):").pack(anchor=tk.W)
tk.Entry(advanced_frame, textvariable=enemy_health_scaling_var).pack(anchor=tk.W)

tk.Label(advanced_frame, text="Enemy damage (% per player):").pack(anchor=tk.W)
tk.Entry(advanced_frame, textvariable=enemy_damage_scaling_var).pack(anchor=tk.W)

tk.Label(advanced_frame, text="Enemy posture absorption (% per player):").pack(anchor=tk.W)
tk.Entry(advanced_frame, textvariable=enemy_posture_scaling_var).pack(anchor=tk.W)

tk.Label(advanced_frame, text="Boss health (% per player):").pack(anchor=tk.W)
tk.Entry(advanced_frame, textvariable=boss_health_scaling_var).pack(anchor=tk.W)

tk.Label(advanced_frame, text="Boss damage (% per player):").pack(anchor=tk.W)
tk.Entry(advanced_frame, textvariable=boss_damage_scaling_var).pack(anchor=tk.W)

tk.Label(advanced_frame, text="Boss posture absorption (% per player):").pack(anchor=tk.W)
tk.Entry(advanced_frame, textvariable=boss_posture_scaling_var).pack(anchor=tk.W)

# Button to copy files to the destination folder
copy_button = tk.Button(root, text="Copy files to the destination folder",
                        command=lambda: copy_files("extracted"), state=tk.DISABLED)
copy_button.pack(pady=20)

# Automatically start the download and installation process
start_process()

# Keep the GUI window open
root.mainloop()
