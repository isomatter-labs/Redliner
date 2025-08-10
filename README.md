
# Redliner [0.0.2] - PDF (and more) Compare Tool

EARLY DEVELOPMENT! Expect bugs and missing features. No version checking / updating exists yet. <br><br>
Redliner allows for quickly identifying changes in text and visual documents by generating a per-pixel visual diff. <br> <br>
[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/cjett)

![Example Diff Screenshot](https://raw.githubusercontent.com/CJett/Redliner/refs/heads/main/example.png)

## Installing
- Grab the latest windows installer or portable EXE from [https://github.com/CJett/Redliner/releases](https://github.com/CJett/Redliner/releases)

## Building Locally
- install python 3.13
- (optional) install Inno Setup 6 for installer creation
- `git clone https://github.com/CJett/Redliner.git`
- `pip install -r requirements.txt`
- `scripts/build-all-windows.bat` (or just the debug / onefile versions)
- EXE's and installer are in /dist/

## Todo
- ### V1
- [X] Upload to GitHub
- [X] Develop installation / distribution procedure
- [X] Switch to OpenGL
- [X] Add update check button / built-in update installation
  - [ ] Make new version notif only pop up once
- [ ] Finish initial documentation
- [ ] Implement dynamic canvas
- [ ] Implement export document composition
- ### V2
- [ ] Implement annotation tools
- [ ] Implement text-aware search and PDF generation
- [ ] Set up Linux and MacOS build scripts
- [ ] Add background rasterization for faster page loads


## Extending Redliner for your company / workflow
While anything in Redliner can be modified through forking the repo, there are a few pieces that are architected to be easily extended:
* Document Fetchers
* Document Parsers
* Drawing Tools (Not implemented yet)
* Drawing Features (Not implemented yet)

### Extensions
#### Document Fetchers
These define the method by which a document is retrieved and used by Redliner. As an example, say your company uses a document control system (let's call it Agility) that requires authentication. Here's how you might implement that:
1. create a new python file, `extensions/fetcher/agility_fetcher.py`
2. import the template Fetcher class (`from redliner.extensions.fetcher import Fetcher`)
3. Subclass it
4. Implement `_pick(self)->target(str)`
   1. This method should pop up some dialog for the user to pick a file. Maybe it's an Agility search window.
   2. The target string follows no particular format - you just need to be able to parse it in your implemented `_fetch`.
5. Implement`_fetch(self, target:str) -> (name(str), local_path(str))`
   1. This method should take a target string and store the referenced document as a temporary file (see `TemporaryFileManager` later in this doc)
   2. In our example, maybe the target follows the form `documentnumber_versionnumber_doctype`. Take that target, parse it from the document control system, store it as a temporary file.
   3. After storing the file, return a name for the document along with the path to the temporary file.
6. Implement any other functions you need, such as authentication, user settings, and so on
   1. In our example, maybe an auth token is initialized empty in `__init__` and is  filled in when `def authenticate(self):...` is called.
   2. Register any functions in your `self.actions`, a dict mapping `button_text:str` to `method:callable`. Example: in your `__init__`, add `self.actions["🔓 Authenticate"] = self.authenticate`


### Convenience Classes And Helpers

#### PersistentDict
* PersistentDict is, as the name implies, a dictionary that persists between runs. 
* Subclassed features, fetchers, tools, and srcdocs have `self.pd` pointing to the global PersistentDict built-in.
* Define a default value by calling `self.pd.default(key:str, value)`
  * **NOTE:** values must be JSON-serializable
* Fetch values via `self.pd[key:str]`
* Set values via `self.pd[key:str] = X`
* Set multiple values via `self.pd.update(data:dict)`
* Reset a value to default by calling `self.pd.reset(key:str)`

#### TemporaryFileManager
* It's recommended, but not required, to store data using the TemporaryFileManager. This ensures proper cleanup at the end of the program. 
* Subclassed features, fetchers, tools, and srcdocs have `self.tfm` pointing to the global TemporaryFileManager built-in.
* `self.tfm.load(src:str)` can take either a path-like string (in which case `shutil.copy` is called) or bytes (in which case they're written directly to a temporary file). A path to the temporary file is returned as a string.
* `self.tfm.make_fp()` generates a new, safe temporary file path you can use. Returns the path as a string.
1. `self.tfm.get(path:str)` is a convenience function which reads and returns the binary data of the temporary file requested.