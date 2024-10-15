import os
import zipfile
import shutil
import requests
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


# Funzione per ottenere l'URL dell'ultima versione del file .zip
def get_latest_release_zip_url():
    latest_url = "https://github.com/LukeYui/EldenRingSeamlessCoopRelease/releases/latest"
    response = requests.get(latest_url, allow_redirects=True)
    final_url = response.url
    zip_url = final_url.replace('/tag/', '/download/') + "/ersc.zip"
    return zip_url


# Funzione per mostrare la schermata di caricamento
def show_loading_screen():
    loading_screen = tk.Toplevel(root)
    loading_screen.title("Caricamento...")
    loading_label = tk.Label(loading_screen, text="Download in corso, attendere prego...")
    loading_label.pack(padx=20, pady=20)
    loading_screen.grab_set()  # Impedisce interazioni con la finestra principale
    return loading_screen


# Funzione per scaricare e estrarre i file, mantenendo la struttura delle cartelle
def download_and_extract():
    # Mostra la schermata di caricamento
    loading_screen = show_loading_screen()

    zip_url = get_latest_release_zip_url()
    zip_file_path = "repo_ersc.zip"

    print(f"Downloading {zip_url} ...")
    response = requests.get(zip_url)
    with open(zip_file_path, "wb") as file:
        file.write(response.content)
    print(f"Downloaded {zip_file_path}")

    extract_dir = "estratti"
    os.makedirs(extract_dir, exist_ok=True)

    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    print(f"Extracted files to {extract_dir}")

    # Aggiorna il menu a tendina delle lingue
    update_language_dropdown(extract_dir)

    # Elimina il file zip scaricato
    os.remove(zip_file_path)

    # Chiude la schermata di caricamento una volta finito il download
    loading_screen.destroy()

    return extract_dir


# Funzione per copiare i file nella directory di destinazione
def copy_files(extract_dir):
    destination_dir = filedialog.askdirectory(title="Scegli la cartella di destinazione")
    if not destination_dir:
        messagebox.showwarning("Nessuna cartella selezionata", "Devi selezionare una cartella di destinazione.")
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
                    ini_file.write(f"mod_language_override = {language_var.get()}\n")
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
        print(f"File {ini_file_path} non trovato!")

    shutil.rmtree(extract_dir)
    print("Cleaned up temporary files.")

    messagebox.showinfo("Completato", f"File estratti e copiati correttamente nella cartella: {destination_dir}")
    root.destroy()


# Funzione per gestire la chiusura della finestra
def on_close():
    if os.path.exists("estratti"):
        shutil.rmtree("estratti")
        print("Temporary folder removed.")
    root.destroy()


def toggle_advanced_settings():
    if install_type_var.get() == "avanzata":
        advanced_frame.pack(pady=10)
    else:
        advanced_frame.pack_forget()


def load_languages(locale_dir):
    languages = []
    for filename in os.listdir(locale_dir):
        if filename.endswith('.json'):
            language = os.path.splitext(filename)[0]  # Rimuove l'estensione .json
            languages.append(language)
    return languages


# Questa funzione aggiorna il menu a tendina delle lingue una volta che i file sono stati estratti nella cartella temporanea
def update_language_dropdown(extract_dir):
    locale_dir = os.path.join(extract_dir, "SeamlessCoop", "locale")
    if os.path.exists(locale_dir):
        languages = load_languages(locale_dir)
        if not languages:
            print("Nessun file di lingua trovato nella cartella locale.")
        else:
            print(f"Lingue trovate: {languages}")
        languages.insert(0, "")  # Aggiungi un'opzione vuota all'inizio della lista
        language_dropdown['values'] = languages
        language_dropdown.current(0)  # Seleziona il primo valore di default (vuoto)
    else:
        print(f"Directory {locale_dir} non trovata!")


# Funzione principale per gestire il processo completo
def start_process():
    extract_dir = download_and_extract()
    if extract_dir:
        # Abilita il bottone per copiare i file dopo che le lingue sono state aggiornate
        copy_button.config(state=tk.NORMAL)


# Creazione dell'interfaccia grafica con Tkinter
root = tk.Tk()
root.title("Downloader ed estrattore ZIP")

# Collega la funzione di chiusura alla finestra principale
root.protocol("WM_DELETE_WINDOW", on_close)

# Sezione per la selezione del tipo di installazione
install_type_var = tk.StringVar(value="rapida")
install_type_frame = tk.Frame(root)
install_type_frame.pack(pady=10)

tk.Radiobutton(install_type_frame, text="Installazione Rapida", variable=install_type_var, value="rapida",
               command=toggle_advanced_settings).pack(side=tk.LEFT)
tk.Radiobutton(install_type_frame, text="Installazione Avanzata", variable=install_type_var, value="avanzata",
               command=toggle_advanced_settings).pack(side=tk.LEFT)

# Aggiungi una label e un campo di testo per inserire la password
tk.Label(root, text="Inserisci la password per cooppassword:").pack(pady=10)
password_entry = tk.Entry(root)
password_entry.pack(pady=10)

# Aggiungi una label e un menu a tendina per selezionare la lingua
tk.Label(root, text="Seleziona la lingua:").pack(pady=10)
language_var = tk.StringVar(value="")  # Campo vuoto di default
language_dropdown = ttk.Combobox(root, textvariable=language_var)
language_dropdown.pack(pady=10)

# Frame per le impostazioni avanzate
advanced_frame = tk.Frame(root)

# Checkbox per le impostazioni di gameplay
invaders_var = tk.BooleanVar(value=True)
death_debuffs_var = tk.BooleanVar(value=True)
summons_var = tk.BooleanVar(value=True)
skip_splash_var = tk.BooleanVar(value=False)

tk.Checkbutton(advanced_frame, text="Permetti invasori", variable=invaders_var).pack(anchor=tk.W)
tk.Checkbutton(advanced_frame, text="Debuffs alla morte", variable=death_debuffs_var).pack(anchor=tk.W)
tk.Checkbutton(advanced_frame, text="Permetti evocazioni", variable=summons_var).pack(anchor=tk.W)
tk.Checkbutton(advanced_frame, text="Salta schermate di avvio", variable=skip_splash_var).pack(anchor=tk.W)

# Impostazioni avanzate
master_volume_var = tk.IntVar(value=5)
enemy_health_scaling_var = tk.IntVar(value=35)
enemy_damage_scaling_var = tk.IntVar(value=0)
enemy_posture_scaling_var = tk.IntVar(value=15)
boss_health_scaling_var = tk.IntVar(value=100)
boss_damage_scaling_var = tk.IntVar(value=0)
boss_posture_scaling_var = tk.IntVar(value=20)

tk.Label(advanced_frame, text="Volume di avvio (0-10):").pack(anchor=tk.W)
tk.Scale(advanced_frame, from_=0, to=10, variable=master_volume_var, orient=tk.HORIZONTAL).pack(anchor=tk.W)

tk.Label(advanced_frame, text="Salute nemici (% per giocatore):").pack(anchor=tk.W)
tk.Entry(advanced_frame, textvariable=enemy_health_scaling_var).pack(anchor=tk.W)

tk.Label(advanced_frame, text="Danno nemici (% per giocatore):").pack(anchor=tk.W)
tk.Entry(advanced_frame, textvariable=enemy_damage_scaling_var).pack(anchor=tk.W)

tk.Label(advanced_frame, text="Assorbimento postura nemici (% per giocatore):").pack(anchor=tk.W)
tk.Entry(advanced_frame, textvariable=enemy_posture_scaling_var).pack(anchor=tk.W)

tk.Label(advanced_frame, text="Salute boss (% per giocatore):").pack(anchor=tk.W)
tk.Entry(advanced_frame, textvariable=boss_health_scaling_var).pack(anchor=tk.W)

tk.Label(advanced_frame, text="Danno boss (% per giocatore):").pack(anchor=tk.W)
tk.Entry(advanced_frame, textvariable=boss_damage_scaling_var).pack(anchor=tk.W)

tk.Label(advanced_frame, text="Assorbimento postura boss (% per giocatore):").pack(anchor=tk.W)
tk.Entry(advanced_frame, textvariable=boss_posture_scaling_var).pack(anchor=tk.W)

# Bottone per copiare i file nella cartella di destinazione
copy_button = tk.Button(root, text="Copia i file nella cartella di destinazione",
                         command=lambda: copy_files("estratti"), state=tk.DISABLED)
copy_button.pack(pady=20)

# Avvia automaticamente il processo di download e installazione
start_process()

# Mantieni aperta la finestra della GUI
root.mainloop()
