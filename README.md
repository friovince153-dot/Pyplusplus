# Py++

Py++ is a toy language. You write a little program, and the computer runs it.

## Run your first program in 5 tiny steps

### Step 1: Open the black window

This window is called the terminal.

- **Windows:** press the Windows key, type `PowerShell`, press Enter.
- **Mac:** press `Cmd + Space`, type `Terminal`, press Enter.

### Step 2: Go to the Py++ folder

Type this, but put your real folder name where it says `folder-name`:

```sh
cd folder-name
```

Now type `dir` (Windows) or `ls` (Mac).
You should see a file named `pylc.py`. If you see it, you are in the right place.

### Step 3: Make a file

Make a new file called `hello.pyl` in that same folder. Put this in it:

```pyl
print("Hello!")
```

Save it.

### Step 4: Run it

```sh
python pylc.py hello.pyl --run
```

### Step 5: Look!

You should see:

```text
Hello!
```

You made a program.

## If it does not work

- **It says `python not found`:** type `py` or `python3` instead of `python`.
- **It says `g++ not found`:** your computer needs a helper tool called g++.
  - Windows: install [MSYS2](https://www.msys2.org/), then run `pacman -S mingw-w64-ucrt-x86_64-gcc` in the MSYS2 UCRT64 window.
  - Mac: run `xcode-select --install`.
  - Ubuntu: run `sudo apt install g++`.
- **It says `file not found`:** you are in the wrong folder. Go back to Step 2.

## Check that everything works (optional)

In the Py++ folder, type:

```sh
python tests/run_tests.py
```

You should see `PASS` on every line.
