from cx_Freeze import setup, Executable

# If the build fails with "ImportError: no module named _view",
# just put the import in the named module!
# import pygame._view
# This'll make cx_freeze notice that this module is needed

includes = []
excludes = ['_gtkagg', '_tkagg', 'bsddb', 'curses', 'email', 'pywin.debugger',
            'pywin.debugger.dbgcon', 'pywin.dialogs', 'tcl',
            'Tkconstants', 'Tkinter']
# External libraries or any other folders with py stuff go here
packages = ['libs']
path = []

# This part is only relevant if you have included shelve functionalities
for dbmodule in ['dbhash', 'gdbm', 'dbm', 'dumbdbm', 'anydbm']:
    try:
        __import__(dbmodule)
    except ImportError:
        pass
    else:
        # If we found the module, ensure it's copied to the build directory.
        packages.append(dbmodule)

GUI2Exe_Target_1 = Executable(
    # what to build
    script = "run.py",
    initScript = None,
    base = 'Win32GUI',
    targetDir = r"dist",
    targetName = "Clydes Fate.exe",
    compress = False,
    copyDependentFiles = False,
    appendScriptToExe = False,
    appendScriptToLibrary = False,
    icon = 'assets/graphics/_appicon.ico'
    )

setup(

    version = "1.0",
    description = "Indie Horror Game",
    author = "Marcel Schnelle",
    name = "Clyde's Fate",

    options = {"build_exe": {"includes": includes,
                             "excludes": excludes,
                             "packages": packages,
                             "path": path
                             }
               },

    executables = [GUI2Exe_Target_1]
    )