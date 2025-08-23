    __    _                                ____  ____  ______
   / /   (_)___  ___  ____ _____ ____     / __ \/ __ \/ ____/
  / /   / / __ \/ _ \/ __ `/ __ `/ _ \   / /_/ / /_/ / / __  
 / /___/ / / / /  __/ /_/ / /_/ /  __/  / _, _/ ____/ /_/ /  
/_____/_/_/ /_/\___/\__,_/\__, /\___/  /_/ |_/_/    \____/   
                         /____/
An offline RPG that you can play right from your terminal. Follow the steps below to install and start playing!

---

## 📦 Requirements
* Python **3.8+** ([Download here](https://www.python.org/downloads/))
* Internet connection (for installation)

---

## 🚀 Installation

### Step 0: Install Python (if not already installed)

**Windows:**
1. Go to [Python Downloads](https://www.python.org/downloads/windows/).
2. Download the latest **Python 3.8+ installer**.
3. Run the installer and **make sure to check "Add Python to PATH"**.
4. Verify installation:  
   `python --version`

**macOS:**
1. Open Terminal.
2. Check if Python is installed:  
   `python3 --version`
3. If not installed, install via Homebrew (first install Homebrew if you don’t have it):  
   `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`  
   `brew install python`
4. Verify installation:  
   `python3 --version`

**Linux (Ubuntu/Debian):**
1. Open Terminal.
2. Check Python:  
   `python3 --version`
3. If not installed, run:  
   `sudo apt update`  
   `sudo apt install python3 python3-pip -y`
4. Verify installation:  
   `python3 --version`

---

### Step 1: Open your terminal or command prompt

**Windows:** Press `Windows + R`, type `cmd`, and hit Enter.  
**macOS/Linux:** Open Terminal from Applications or press `Ctrl+Alt+T`.

### Step 2: Install Lineage RPG

**Windows:**  
`pip install lineage-rpg`  

or if `pip` doesn’t work:  
`python -m pip install lineage-rpg`

**macOS/Linux:**  
`pip3 install lineage-rpg`  

or if needed:  
`python3 -m pip install lineage-rpg`

### Step 3: Upgrade to the latest version

`pip install --upgrade lineage-rpg`  

or  
`python -m pip install --upgrade lineage-rpg`

---

## 🕹️ How to Play

Once installed, launch the game from your terminal using:  
`lineage-rpg`

You'll see:  
`Welcome to Lineage RPG! Type 'exit' or CTRL+C to quit.`

Then, type `help` and press ENTER. You'll see a list of commands to start playing.

---

## ❓ Troubleshooting

### Installation Issues
* **"Command not found" or "'pip' is not recognized"**: Make sure Python and pip are correctly installed and added to your PATH. Try:  
  `python -m pip install lineage-rpg`
* **Permission denied**: Use:  
  `pip install --user lineage-rpg`  
  or run as administrator/sudo.

### Launch Issues
* **"lineage-rpg" command not found**: Try these alternatives:  
  `python -m lineage_rpg`  
  `python3 -m lineage_rpg`  
  `python -m lineage_rpg.main`

### Game Issues
* **Corrupted save file**: The game will automatically reset and start fresh if your save file is corrupted.  
* **Game doesn't respond**: Use `Ctrl+C` to safely exit and save your progress.

**Still having issues?** Make sure you're using Python 3.8+ and have sufficient disk space.
