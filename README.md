# Py++ – Getting Started Guide

Welcome to **Py++!**

Py++ is a simple toy programming language that allows you to write and run small programs. This project is designed to help beginners understand how programming languages work through simple examples and exercises.

This guide will help you install the required tools, set up Py++, write your first program, and run the available tests.

---

## 1. Requirements

Before using Py++, make sure you have the following:

- A computer running Windows, macOS, or Linux.
- Python 3 installed.
- A C++ compiler (`g++`).
- A code editor, such as Visual Studio Code.
- The Py++ project files.

### Check if Python is installed

Open your terminal and type:

```sh
python --version
```

If that does not work, try:

```sh
py --version
```

Or:

```sh
python3 --version
```

You should see your installed Python version.

### Install a C++ compiler

Py++ requires `g++` to compile its generated C++ programs.

**Windows:**
1. Download and install [MSYS2](https://www.msys2.org/).
2. Open the MSYS2 UCRT64 terminal.
3. Run:

```sh
pacman -S mingw-w64-ucrt-x86_64-gcc
```

4. Add the following folder to your Windows PATH:

```text
C:\msys64\ucrt64\bin
```

**macOS:**

```sh
xcode-select --install
```

**Ubuntu/Linux:**

```sh
sudo apt install g++
```

Check your compiler installation:

```sh
g++ --version
```

---

## 2. Download or Open the Py++ Project

Get the Py++ project files from the project repository or the provided project folder.

If you are using GitHub:

1. Open the Py++ repository.
2. Click the green **Code** button.
3. Select **Download ZIP**.
4. Extract the downloaded ZIP file.
5. Open the extracted Py++ folder in Visual Studio Code.

Make sure you can see the main file:

```text
pylc.py
```

This is the file used to run Py++ programs.

---

## 3. Create Your First Py++ Program

Let's create a simple program.

**Step 1:** Open your Py++ project folder.

**Step 2:** Create a new file named:

```text
hello.pyl
```

**Step 3:** Write the following code:

```pyl
print("Hello!")
```

**Step 4:** Save your file.

Your project should now contain:

```text
Py++/
│
├── pylc.py
├── hello.pyl
└── tests/
```

---

## 4. Run Your First Program

Open the terminal inside your Py++ project folder.

Run this command:

```sh
python pylc.py hello.pyl --run
```

If your computer uses the `py` command, use:

```sh
py pylc.py hello.pyl --run
```

If you are using macOS or Linux and need `python3`, use:

```sh
python3 pylc.py hello.pyl --run
```

**Expected output:**

```text
Hello!
```

Congratulations! You have successfully run your first Py++ program.

---

## 5. Explore the Sample Programs

Py++ includes sample programming exercises inside the `tests` folder.

Here are some of the available examples:

| File | Description |
|---|---|
| `s01_temperature_table.pyl` | Temperature conversion and tables |
| `s02_shopping_cart.pyl` | Shopping cart calculations |
| `s03_prime_finder.pyl` | Finding prime numbers |
| `s04_word_counter.pyl` | Counting words |
| `s05_palindrome_check.pyl` | Checking palindromes |
| `s06_star_pattern.pyl` | Printing star patterns |
| `s07_bank_account.pyl` | Bank account operations |
| `s08_grades_report.pyl` | Generating grade reports |
| `s09_collatz_steps.pyl` | Collatz sequence |
| `s10_bubble_sort.pyl` | Sorting numbers using Bubble Sort |

To run a sample program, use:

```sh
python pylc.py tests/s01_temperature_table.pyl --run
```

**Note:** Make sure the sample files use the `.pyl` extension and that you are running the command from the main Py++ project folder.

---

## 6. Run the Automated Tests

Py++ also includes automated tests to check whether its features are working correctly.

To run the tests, open your terminal in the main project folder and type:

```sh
python tests/run_tests.py
```

If you are using Windows and `python` does not work:

```sh
py tests/run_tests.py
```

**Expected result:**

You should see `PASS` messages for successfully completed tests.

If a test fails, check the error message and make sure Python, g++, and the project files are properly installed.

---

## 7. Troubleshooting

Here are some common problems and their solutions.

**Problem: `python is not recognized`**

Solution:
- Check whether Python is installed.
- Try using `py` or `python3`.
- Make sure Python is added to your system PATH.

**Problem: `g++ not found`**

Solution:
- Install the appropriate C++ compiler for your operating system.
- Make sure the compiler's installation folder is added to PATH.
- Restart your terminal after updating PATH.

**Problem: `file not found`**

Solution:
- Make sure you are inside the main Py++ project folder.
- Check that the filename and extension are correct.
- Make sure the file exists in the specified location.

**Problem: A program does not run**

Solution:
- Check your program for syntax errors.
- Make sure you saved your changes.
- Verify that you are using the correct command.
- Read the error message displayed in the terminal.

---

## 8. Important Notes

- Always open your terminal in the main Py++ project folder.
- Do not rename or delete `pylc.py`.
- Keep the `tests` folder and its required files together.
- Use the `.pyl` extension for Py++ source programs.
- Make sure Python and g++ are properly installed before running programs.

---

## 9. You're Ready to Use Py++!

You can now create your own `.pyl` programs, explore the sample exercises, and test the functionality of Py++.

Have fun learning and experimenting with Py++!

**Happy Coding!**
