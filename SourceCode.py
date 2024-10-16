import os
import zipfile
import shutil
import requests
import threading 
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# Funzione per ottenere l'URL dell'ultima versione del file .zip
def get_latest_release_zip_url():
    latest_url = "https://github.com/LukeYui/EldenRingSeamlessCoopRelease/releases/latest"
    response = requests.get(latest_url, allow_redirects=True)
    final_url = response.url
    zip_url = final_url.replace('/tag/', '/download/') + "/ersc.zip"
    return zip_url

# Funzione per mostrare la schermata di caricamento con barra di progresso
def show_loading_screen():
    loading_screen = tk.Toplevel(root)
    loading_screen.title("Loading...")
    loading_screen.geometry("350x100")
    loading_label = tk.Label(loading_screen, text="Downloading, please wait...", font=("Arial", 12))
    loading_label.pack(padx=20, pady=10)

    progress_bar = ttk.Progressbar(loading_screen, orient="horizontal", mode="determinate", length=300)
    progress_bar.pack(padx=20, pady=10)

    # Forza l'aggiornamento della finestra per renderla visibile su tutte le piattaforme
    loading_screen.update_idletasks()

    loading_screen.grab_set()
    loading_screen.transient(root)
    return loading_screen, progress_bar

def download_and_extract():
    loading_screen, progress_bar = show_loading_screen()
    zip_url = get_latest_release_zip_url()
    zip_file_path = "repo_ersc.zip"

    print(f"Downloading {zip_url} ...")
    response = requests.get(zip_url, stream=True)
    total_length = int(response.headers.get('content-length'))

    with open(zip_file_path, "wb") as file:
        downloaded = 0
        for data in response.iter_content(chunk_size=4096):
            file.write(data)
            downloaded += len(data)
            progress_bar['value'] = (downloaded / total_length) * 100
            loading_screen.update_idletasks()  # Aggiorna la finestra di caricamento durante il download
            root.update_idletasks()
    print(f"Downloaded {zip_file_path}")

    extract_dir = "extracted"
    os.makedirs(extract_dir, exist_ok=True)
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    print(f"Extracted files to {extract_dir}")

    update_language_dropdown(extract_dir)
    os.remove(zip_file_path)
    loading_screen.destroy()

    # Nascondi il pulsante di download e mostra gli altri controlli
    download_button.pack_forget()
    install_type_frame.pack(pady=10)
    password_label.pack(pady=10)
    password_entry.pack(pady=10)
    language_label.pack(pady=10)
    language_dropdown.pack(pady=10)
    copy_button.pack(pady=20)

    # Nascondi il frame dei parametri avanzati di default
    advanced_frame.pack_forget()
    root.geometry("")  # Adatta la finestra

    copy_button.config(state=tk.NORMAL)
    return extract_dir

# Funzione per copiare file nella directory di destinazione
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
                    if language_var.get() != "system default":
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

# Funzione per gestire la chiusura della finestra
def on_close():
    if os.path.exists("extracted"):
        shutil.rmtree("extracted")
        print("Temporary folder removed.")
    root.destroy()

# Funzione per aggiornare la lista delle lingue
def update_language_dropdown(extract_dir):
    locale_dir = os.path.join(extract_dir, "SeamlessCoop", "locale")
    if os.path.exists(locale_dir):
        languages = load_languages(locale_dir)
        if not languages:
            print("No language files found in the locale folder.")
        else:
            print(f"Languages found: {languages}")
        language_dropdown['values'] = languages
        language_dropdown.current(0)
    else:
        print(f"Directory {locale_dir} not found!")

def load_languages(locale_dir):
    languages = []
    for filename in os.listdir(locale_dir):
        if filename.endswith('.json'):
            language = os.path.splitext(filename)[0]
            languages.append(language)
    languages = sorted(languages)
    languages.insert(0, "system default")
    return languages

def start_process():
    threading.Thread(target=download_and_extract).start()

# Funzione per adattare i controlli dell'installazione avanzata
def toggle_advanced_settings():
    if install_type_var.get() == "advanced":
        advanced_frame.pack(pady=10)
        root.geometry("")  # Reimposta la dimensione della finestra per adattarla
    else:
        advanced_frame.pack_forget()
        root.geometry("")  # Adatta di nuovo la finestra

# Creazione dell'interfaccia utente
root = tk.Tk()
root.title("ersc installer")
root.geometry("500x500")  # Dimensioni iniziali della finestra

root.protocol("WM_DELETE_WINDOW", on_close)

install_type_var = tk.StringVar(value="quick")

# Elementi che verranno mostrati dopo il download
install_type_frame = tk.Frame(root)
tk.Label(install_type_frame, text="Installation type:", font=("Arial", 12)).pack(side=tk.LEFT)
install_type_quick = tk.Radiobutton(install_type_frame, text="Quick", variable=install_type_var, value="quick",
                                    command=toggle_advanced_settings, font=("Arial", 12))
install_type_quick.pack(side=tk.LEFT)
install_type_advanced = tk.Radiobutton(install_type_frame, text="Advanced", variable=install_type_var, value="advanced",
                                       command=toggle_advanced_settings, font=("Arial", 12))
install_type_advanced.pack(side=tk.LEFT)

password_label = tk.Label(root, text="Enter the password for coop:", font=("Arial", 12))
password_entry = tk.Entry(root, font=("Arial", 12))

language_label = tk.Label(root, text="Select a language:", font=("Arial", 12))
language_var = tk.StringVar(value="system default")
language_dropdown = ttk.Combobox(root, textvariable=language_var, state="readonly", font=("Arial", 12))

# Parametri avanzati (visibili solo se l'utente seleziona l'opzione "Advanced")
advanced_frame = tk.Frame(root)
invaders_var = tk.BooleanVar(value=True)
death_debuffs_var = tk.BooleanVar(value=True)
summons_var = tk.BooleanVar(value=True)
skip_splash_var = tk.BooleanVar(value=False)

# Inserimento dei checkbutton avanzati
tk.Checkbutton(advanced_frame, text="Allow invaders", variable=invaders_var, font=("Arial", 12)).grid(row=0, column=0, sticky=tk.W)
tk.Checkbutton(advanced_frame, text="Apply death debuffs", variable=death_debuffs_var, font=("Arial", 12)).grid(row=1, column=0, sticky=tk.W)
tk.Checkbutton(advanced_frame, text="Allow summoning of spirits", variable=summons_var, font=("Arial", 12)).grid(row=2, column=0, sticky=tk.W)
tk.Checkbutton(advanced_frame, text="Skip splash screens", variable=skip_splash_var, font=("Arial", 12)).grid(row=3, column=0, sticky=tk.W)

# Advanced settings
master_volume_var = tk.IntVar(value=5)
enemy_health_scaling_var = tk.IntVar(value=35)
enemy_damage_scaling_var = tk.IntVar(value=0)
enemy_posture_scaling_var = tk.IntVar(value=15)
boss_health_scaling_var = tk.IntVar(value=100)
boss_damage_scaling_var = tk.IntVar(value=0)
boss_posture_scaling_var = tk.IntVar(value=20)

# Funzione di validazione che consente solo numeri
def validate_numeric_input(char):
    return char.isdigit() or char == ""

# Registriamo la funzione di validazione
validate_command = root.register(validate_numeric_input)

# Parametri avanzati (etichetta a sinistra, input a destra)
tk.Label(advanced_frame, text="Startup volume (0-10):", font=("Arial", 12)).grid(row=4, column=0, sticky=tk.W)
tk.Scale(advanced_frame, from_=0, to=10, variable=master_volume_var, orient=tk.HORIZONTAL).grid(row=4, column=1, sticky=tk.W)

tk.Label(advanced_frame, text="Enemy health (% per player):", font=("Arial", 12)).grid(row=5, column=0, sticky=tk.W)
tk.Entry(advanced_frame, textvariable=enemy_health_scaling_var, font=("Arial", 12),
         validate="key", validatecommand=(validate_command, '%S')).grid(row=5, column=1, sticky=tk.W)

tk.Label(advanced_frame, text="Enemy damage (% per player):", font=("Arial", 12)).grid(row=6, column=0, sticky=tk.W)
tk.Entry(advanced_frame, textvariable=enemy_damage_scaling_var, font=("Arial", 12),
         validate="key", validatecommand=(validate_command, '%S')).grid(row=6, column=1, sticky=tk.W)

tk.Label(advanced_frame, text="Enemy posture absorption (% per player):", font=("Arial", 12)).grid(row=7, column=0, sticky=tk.W)
tk.Entry(advanced_frame, textvariable=enemy_posture_scaling_var, font=("Arial", 12),
         validate="key", validatecommand=(validate_command, '%S')).grid(row=7, column=1, sticky=tk.W)

tk.Label(advanced_frame, text="Boss health (% per player):", font=("Arial", 12)).grid(row=8, column=0, sticky=tk.W)
tk.Entry(advanced_frame, textvariable=boss_health_scaling_var, font=("Arial", 12),
         validate="key", validatecommand=(validate_command, '%S')).grid(row=8, column=1, sticky=tk.W)

tk.Label(advanced_frame, text="Boss damage (% per player):", font=("Arial", 12)).grid(row=9, column=0, sticky=tk.W)
tk.Entry(advanced_frame, textvariable=boss_damage_scaling_var, font=("Arial", 12),
         validate="key", validatecommand=(validate_command, '%S')).grid(row=9, column=1, sticky=tk.W)

tk.Label(advanced_frame, text="Boss posture absorption (% per player):", font=("Arial", 12)).grid(row=10, column=0, sticky=tk.W)
tk.Entry(advanced_frame, textvariable=boss_posture_scaling_var, font=("Arial", 12),
         validate="key", validatecommand=(validate_command, '%S')).grid(row=10, column=1, sticky=tk.W)


# Pulsante per copiare i file, inizialmente disabilitato
copy_button = tk.Button(root, text="Copy files in the Elden Ring folder", command=lambda: copy_files("extracted"), state=tk.DISABLED, font=("Arial", 12))

# Pulsante di download, centrato
download_button = tk.Button(root, text="Download", command=start_process, font=("Arial", 12))
download_button.pack(pady=100)  # Centra con padding verticale maggiore

root.mainloop()
