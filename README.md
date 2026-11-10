# Py++ | User Guide

Welcome to **Py++!**

Py++ is a simple programming language where you can write and run your own programs. Follow this guide to get started!

## 1. What You Need

Before using Py++, make sure you have:

- A computer (Windows, Mac, or Linux).
- Python installed on your computer.
- The Py++ project folder.

**Don't have Python yet?**

Download it here: https://www.python.org/downloads/

For Windows, remember to check **"Add Python to PATH"** during installation.

## 2. Open the Py++ Folder

1. Download the Py++ project.
2. Extract the ZIP file if you downloaded one.
3. Open the extracted folder.
4. Open the folder in Visual Studio Code.
5. Find the file named `pylc.py`.

Make sure you are in the correct folder before continuing.

## 3. Open the Terminal

In Visual Studio Code:

1. Click **Terminal** at the top.
2. Select **New Terminal**.
3. A terminal will appear at the bottom of your screen.

## 4. Run Your First Program

Let's try a simple program!

**Step 1:** Create a new file inside the Py++ folder.

Name it:

`hello.pyl`

**Step 2:** Copy this code into the file:

```python
print("Hello!")
```

**Step 3:** Save the file by pressing `Ctrl + S`.

**Step 4:** In the terminal, type:

```bash
python pylc.py hello.pyl --run
```

If that doesn't work, try:

```bash
py pylc.py hello.pyl --run
```

**Step 5:** Press Enter.

You should see:

```text
Hello!
```

<badge color="success">Success!</badge> You have just run your first Py++ program!

## 5. Try the Sample Programs

Want to explore more? Open the `tests` folder.

It contains sample programs you can try:

| Program | What It Does |
|---|---|
| Temperature Table | Works with temperatures |
| Shopping Cart | Calculates shopping costs |
| Prime Finder | Finds prime numbers |
| Word Counter | Counts words |
| Palindrome Check | Checks words and numbers |
| Star Pattern | Prints star patterns |
| Bank Account | Demonstrates bank account operations |
| Grades Report | Displays grades |
| Collatz Steps | Explores a number sequence |
| Bubble Sort | Arranges numbers in order |

To run a sample, type this in the terminal:

```bash
python pylc.py tests/s01_temperature_table.py --run
```

Replace the filename with the sample you want to try.

## 6. Having Problems?

Here are some quick fixes:

**Python not found?**

Try using `py` instead of `python`. If neither works, install Python.

**g++ not found?**

Py++ needs a C++ compiler to run programs. Install it using the instructions here:

https://www.msys2.org/

**File not found?**

Make sure:
- You opened the correct Py++ folder.
- The filename is correct.
- You saved your file.

**Program not running?**

Check your code and make sure you typed the command correctly.

## 7. Test Py++ (Optional)

You can also check if Py++ is working properly.

In the terminal, type:

```bash
python tests/run_tests.py
```

Press Enter.

If everything works, you should see `PASS` messages.

---

## You're All Set!

That's it! You can now write, save, and run your own Py++ programs.

**Thank you for trying Py++. Happy Coding!**
