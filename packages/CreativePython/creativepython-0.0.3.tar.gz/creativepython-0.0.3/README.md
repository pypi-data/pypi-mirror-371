# CreativePython

CreativePython is a Python-based software environment for developing algorithmic art projects.  It mirrors the [JythonMusic API](https://jythonmusic.me/api-reference/).

This package is still under development.

---

## Quick Install

The CreativePython Install Scripts [(Download)](https://www.dropbox.com/scl/fo/7cwxayca38ajcc533bpgs/AGP4pnP-xhb-5LH_7YPsgyk?rlkey=2led17m6h0ku9y3hzbsnvsio1&dl=1) install CreativePython and all its required software, including Python3, FluidSynth, PortAudio, ffmpeg, Homebrew (on Mac), and Windows Build Kit (on Windows).

### Windows 
  1. Open `win-scripts.tgz`.  Right-click `windows_setup.bat`, and **Run as Administrator** (it will open PowerShell and run).  
  2. Follow any prompts and let it finish.
    - If you do not have Windows Build Kit installed, it will be installed as part of this process.  This may take some time to complete.

### macOS 
  1. Open `mac-scripts.tgz`.  Control-click `mac_setup.command`, and **Open** (it will open Terminal and run).
  2. Follow any prompts and let it finish.
    - If you do not have Command Line Tools for XCode installed, it will be installed as part of this process.  This may take some time to complete.

---

## Custom Install

---

### 1. Install Python 3 + pip

#### Windows
1. Download the [Python 3 installer](https://www.python.org/downloads/).  
2. Run the installer. **Check the box that says “Add Python to PATH”** before clicking *Install Now*.  
3. Open Command Prompt (search for "cmd" in the Start menu).
4. Verify your installation.

   ```$ python --version```

   You should see something like "Python 3.12.4"

#### MacOS
1. Open Terminal (press Command + Space, type "Terminal", and hit Enter).
2. Install **Homebrew** if you don't have it.

   ```$ /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"```

3. Install Python 3.

   ```$ brew install python```

4. Verify your installation.

   ```$ python3 --version```

   You should see something like "Python 3.12.4"

---

### 2. Install System Libraries

#### Windows
- **PortAudio**:
   On Windows, PortAudio is installed automatically with CreativePython, however you need Microsoft Build Tools installed first.
   1. Download [the latest Windows build](https://visualstudio.microsoft.com/visual-cpp-build-tools/).
   2. Run the installer.  When prompted, select **C++ build tools**.
   3. Click **Install**.  This may take several minutes.

- **FluidSynth**:
   1. Download [the latest Windows build](https://github.com/FluidSynth/fluidsynth/releases).
   2. Unzip it, and add the folder's location to your PATH.

- **ffmpeg**:
   1. Download [the latest Windows build](ffmpeg.org/download.html).
   2. Unzip it, and move the folder to `C:\ffmpeg`.
   3. Add `C:\ffmpeg\bin` to your PATH.

#### Mac
- **All Libraries**:
   1. Open Terminal.
   2. Install PortAudio, FluidSynth, and ffmpeg.

      ```$ brew install portaudio fluidsynth ffmpeg```

---

### 3. Install CreativePython

#### Any OS
1. Open Command Prompt/Terminal.

   ```$ pip install CreativePython```

   ```$ cp-setup```

2. When prompted, download the default soundfont.  (It's FluidR3 GM2-2, by the way)

   - If you choose not to download the soundfont, you will need to provide your own.

3. Verify your installation.

   ```$ cp-test```

   You should hear a single MIDI note played at C4.  If so, you're all set!