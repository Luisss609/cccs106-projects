# Lab 1 Report: Environment Setup and Python Basics

**Student Name:** Luis Van Dirk B. Albano\
**Student ID:** 231002303\
**Section:** BSCS 3B\
**Date:** August 27, 2025

## Environment Setup

### Python Installation
- **Python Version:** Python 3.13.7
- **Installation Issues:** None
- **Virtual Environment Created:** ✅ cccs106_env_Albano

### VS Code Configuration
- **VS Code Version:** 1.103.2
- **Python Extension:** ✅ Installed and configured
- **Interpreter:** ✅ Set to cccs106_env_Albano/Scripts/python.exe

### Package Installation
- **Flet Version:** 0.28.3
- **Other Packages:** None

## Programs Created

### 1. hello_world.py
- **Status:** ✅ Completed
- **Features:** Student info display, age calculation, system info
- **Notes:** When developing a simple Hello, World! program, not many challenges are involved as it is the simplest way to test a programming language. One note, however, is that it allows beginners to ensure that their environment is properly configured, and it provides them with a basic introduction to the syntax of the language.

### 2. basic_calculator.py
- **Status:** ✅ Completed
- **Features:** Basic arithmetic, error handling, min/max calculation
- **Notes:** Simple operations such as addition, subtraction, multiplication, and division are introduced when a simple calculator is built. One of the pitfalls is to process invalid inputs (divide by zero, enter letters rather than numbers). One observation is that it allows beginners to exercise logic, conditionals, and user interaction.

## Challenges and Solutions

As I was writing the hello world.py program, my experience was not that difficult as it was simple. The only complication was that my Python setting and VS Code interpreter had to be configured in a way that allowed the program to be run without errors. I resolved this by checking the interpreter settings in VS Code twice and making sure that the right virtual environment was opened.

In the case of the basic calculator.py, unexpected inputs by the user (ie. typing letters rather than numbers or trying to divide by 0) were one of the key issues. These were my problems, and I had myself introduced errors, but I could get rid of these problems by using try-except blocks to trap invalid input and I had introduced a test to guard against division by a zero. Not only did this make the program more reliable, but also helped provide a more enjoyable user experience due to the conveniently informative error messages that it displays if it crashes.

## Learning Outcomes

During this laboratory, I learned the basics of Python program writing and execution (with a Hello world program and a basic calculator). I also understood that the syntax and indentation of Python are really important because minor errors can be made.

I also had more familiarity with development environment set-up. Setting up Python in VS Code, selecting the appropriate interpreter, and a virtual environment allowed me to understand how a correct setup allows easier coding and eliminates issues in the future. I learned that it is important to deal with errors through the calculator program. Trying try-except blocks and divide by zero made it obvious to me how to make programs easier and more reliable to use.

## Screenshots

![alt text](Lab1_ScreenShots/basic_calculator_output.png.png)
![alt text](Lab1_ScreenShots/environment_setup2.png.png)
![alt text](Lab1_ScreenShots/vscode_setup.png.png)
![alt text](Lab1_ScreenShots/hello_world_output.png.png)
![alt text](Lab1_ScreenShots/basic_calculator_output.png.png)

