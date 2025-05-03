import os
import yaml
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ---------------- CONFIG ----------------

# Der Ordner 'scraper' und Unterordner wie 'movies' werden automatisch erstellt
SCRAPER_DIR = "scraper"
MOVIES_DIR = os.path.join(SCRAPER_DIR, "movies")
CONFIG_FILE = os.path.join(SCRAPER_DIR, "config.yml")
LINK_FILE = os.path.join(MOVIES_DIR, "stream_links.txt")

# Standardwerte für die Konfiguration
DEFAULT_CONFIG = {
    'allowed_hosts': ['voe.sx', 'dood', 'streamtape.com'],
    'output_folder': 'movies',
    'link_file': 'stream_links.txt'
}

# Ordner erstellen, falls nicht vorhanden
os.makedirs(SCRAPER_DIR, exist_ok=True)  # 'scraper' Ordner erstellen
os.makedirs(MOVIES_DIR, exist_ok=True)  # 'movies' Ordner erstellen

# Funktion zum Laden oder Erstellen der config.yml
def load_config():
    # Wenn die Konfigurationsdatei existiert, lade sie
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
    else:
        # Wenn die Datei nicht existiert, erstelle sie mit den Standardwerten
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            yaml.dump(DEFAULT_CONFIG, f, default_flow_style=False, allow_unicode=True)
        config = DEFAULT_CONFIG
        print("config.yml wurde mit den Standardwerten im 'scraper' Ordner erstellt.")
    
    return config

# Funktion zum Speichern der Konfiguration (falls Änderungen vorgenommen werden)
def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

# Lade die Konfiguration
config = load_config()

# Beispiel für eine Änderung in der Konfiguration (z.B. Hinzufügen eines neuen Hosts)
def update_allowed_hosts(new_host):
    if new_host not in config['allowed_hosts']:
        config['allowed_hosts'].append(new_host)
        save_config(config)  # Speichere die Änderungen
        print(f"Neuer Host '{new_host}' wurde hinzugefügt und gespeichert.")
    else:
        print(f"Host '{new_host}' ist bereits vorhanden.")

# ---------------- HELFER ----------------

ALLOWED_HOSTS = config.get("allowed_hosts", [])
OUTPUT_FOLDER = MOVIES_DIR  # Der Ordner, in dem die Filme gespeichert werden
LINK_FILE = LINK_FILE  # Der Pfad zur stream_links.txt

def save_link(title, url):
    line = f"{title} | {url}\n"
    if os.path.exists(LINK_FILE):
        with open(LINK_FILE, "r", encoding="utf-8") as f:
            if line in f.readlines():
                return  # Bereits vorhanden
    with open(LINK_FILE, "a", encoding="utf-8") as f:
        f.write(line)

def list_saved():
    if not os.path.exists(LINK_FILE):
        print("Keine gespeicherten Links.")
        return
    with open(LINK_FILE, "r", encoding="utf-8") as f:
        print("Gespeicherte Filme:\n")
        print(f.read())

def search_title():
    term = input("Suchbegriff: ").lower()
    if not os.path.exists(LINK_FILE):
        print("Keine gespeicherten Links.")
        return
    with open(LINK_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
        found = [l for l in lines if term in l.lower()]
        if found:
            print("\nGefunden:")
            for l in found:
                print(l.strip())
        else:
            print("Keine Treffer.")

# ---------------- SELENIUM SETUP ----------------
options = webdriver.ChromeOptions()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")
options.add_argument("--enable-unsafe-swiftshader")
options.add_argument("--log-level=3")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# ---------------- FUNKTION: STREAM LINKS HOLEN ----------------
def get_stream_links():
    url = input("Gib die URL der Filmseite ein: ").strip()
    try:
        driver.get(url)
        WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located((By.TAG_NAME, "iframe")))

        iframes = driver.find_elements(By.TAG_NAME, "iframe")

        # Titel aus <title> Tag holen
        title = driver.title.strip()

        found = False
        for iframe in iframes:
            src = iframe.get_attribute("src")
            if any(host in src for host in ALLOWED_HOSTS):
                print(f"Gefunden: {src}")
                save_link(title, src)
                found = True

        if not found:
            print("Keine erlaubten iframe-Quellen gefunden.")
        else:
            print("Links gespeichert.")
    except Exception as e:
        print(f"Fehler: {e}")

# ---------------- MENÜ ----------------
def print_menu():
    """
    Funktion zum Drucken des Menüs mit Formatierung
    """
    os.system('cls' if os.name == 'nt' else 'clear')  # Bildschirm leeren
    print("="*40)
    print("             🖥️  Movie Stream Scraper  🖥️")
    print("="*40)
    print("1. Get Stream URL")
    print("2. Alle gespeicherten Filme anzeigen")
    print("3. Nach Titel suchen")
    print("4. Neuen Host hinzufügen")
    print("0. Beenden")
    print("="*40)

def menu():
    while True:
        print_menu()
        choice = input("Bitte wähle eine Option (0-4): ").strip()

        if choice == "1":
            get_stream_links()
        elif choice == "2":
            list_saved()
        elif choice == "3":
            search_title()
        elif choice == "4":
            new_host = input("Gib den neuen Host an: ").strip()
            update_allowed_hosts(new_host)
        elif choice == "0":
            print("\nDas Programm wird beendet... 👋")
            break
        else:
            print("Ungültige Auswahl. Bitte versuche es erneut.")

# ---------------- START ----------------
try:
    menu()
finally:
    driver.quit()
