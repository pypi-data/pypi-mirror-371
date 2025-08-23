### SOUNDFONT DOWNLOAD HELPERS

from __future__ import annotations
from pathlib import Path
from platformdirs import user_data_dir

APP = "CreativePython"
ORG = "CofC"

SOUNDFONT_NAME = "default.sf2"
CACHE_DIR = Path(user_data_dir(APP, ORG)) / "SoundFonts"
SOUNDFONT_PATH = CACHE_DIR / SOUNDFONT_NAME

SF2_URL = "https://www.dropbox.com/s/xixtvox70lna6m2/FluidR3%20GM2-2.SF2?dl=1"
SF2_SHA256 = "2ae766ab5c5deb6f7fffacd6316ec9f3699998cce821df3163e7b10a78a64066"

def find_soundfont(explicit: str | None = None) -> Path | None:
   """
   Finds a soundfont 'default.sf2' in the cache, and returns its location.
   explicit can be another path that may have the soundfont needed.
   """
   import os

   candidates = []
   if explicit:
      candidates.append(Path(explicit))
   env = os.getenv("CREATIVEPYTHON_SOUNDFONT")
   if env:
      candidates.append(Path(env))
   candidates += [SOUNDFONT_PATH, Path.home() / "SoundFonts" / SOUNDFONT_NAME]
   for c in candidates:
      if c and c.exists():
         return c
   return None

def download_soundfont(dest: Path = SOUNDFONT_PATH) -> Path:
   """Downloads a default soundfont and saves it to the user's cache."""
   from pooch import retrieve, Unzip
   dest.parent.mkdir(parents=True, exist_ok=True)
   p = retrieve(url=SF2_URL, known_hash=f"sha256:{SF2_SHA256}", progressbar=True, fname=dest.name, path=str(dest.parent))
   return Path(p)



### AUTOMATIC CHECK METHODS

def run():
   import shutil, sys, os
   missing = []

   # Check for soundfont file
   sf = find_soundfont()

   # Attempt to download missing soundfont
   if not sf:
      print("CreativePython setup warning: No soundfont found.")
      auto = os.getenv("CP_AUTO_DOWNLOAD") == "1"
      if auto or input("Download the default soundfont now? [Y/n] ").strip().lower() in ("", "y", "yes"):
         path = download_soundfont()
         print(f"Downloaded to: {path}")
      else:
         print(f"\nPlace your .sf2 soundfont at:\n   {SOUNDFONT_PATH}\nOr set CREATIVEPYTHON_SOUNDFONT to its location in your PATH.")
         print("\n(see https://pypi.org/project/CreativePython/ for more details)")


   # Check for required installations
   if not shutil.which("ffmpeg"):
      missing.append("ffmpeg")

   if not shutil.which("fluidsynth"):
      missing.append("FluidSynth")
   
   if not shutil.which("portaudio"):
      missing.append("PortAudio")

   # Warn user about missing requirements
   if missing:
      print("\nCreativePython setup warning:")
      for req in missing:
         print(f"   - {req} is not installed.")
      
      if sys.platform.startswith("darwin"):
         print("\nOn macOS, run:\n   brew install portaudio fluidsynth ffmpeg")
      elif sys.platform.startswith("win"):
         print("\nOn Windows, install missing packages from developers, or run windows_setup.bat")
      else:
         print("\nOn Linux, install missing packages with your package manager (apt, dnf, etc.)")

      print("\n(see https://pypi.org/project/CreativePython/ for more details)")

   return len(missing) == 0


def playNote():
   ready = run()  # check for installation dependencies

   if ready:
      from music import Note, Play, C4, HN  # can't use * within function, so naming needed pieces

      note = Note(C4, HN)        # create a middle C half note
      Play.midi(note)            # and play it!