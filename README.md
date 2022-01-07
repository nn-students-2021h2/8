# Team №8

`Roman Burtsev` - Team Leader

`Roman Yezhov` - QA

`Konstantin Rumyantsev` - Code Reviewer

---
<div align="center">

# Function Explorer Bot

[![python](https://img.shields.io/badge/python-3.8%2B-green)]()
[![pylint](https://img.shields.io/badge/linter-pylint-blue)]()

**Function Explorer Telegram Bot** is a tool that allows you to analyse functions, get information about them and draw
graphs. This README.md will be added to as the project progresses.

[How to use](#how-to-use) •
[What is implemented](#what-is-implemented) •
[What is planned to be implemented](#what-is-planned-to-be-implemented) •
[Meme](#meme)

</div>

<a id="how-to-use"></a>

## How to use

Find our bot named "function explorer" in Telegram:

![none](https://i.ibb.co/m8jWZpJ/image.png)

Start a conversation with the bot to check if it is activated. If you want to use your bot token, then:

1) Clone this repository
2) Create Telegram bot following official [Telegram instructions](https://core.telegram.org/bots#6-botfather)
3) Put your token into `TOKEN` variable

About commands:

- `/graph arg1, arg2, ...` draws a graph of given functions. Functions should be in math format, e.g. _"x = 1",
  "y = x^2 + sin(x)", "x", "y = 1"_.<br>You can also add functions domain via argument "**from _ to _**", for instance,
  _"/graph x, from -10 to 5", "/graph from 0.5 to 1.5, x^2"_. It is possible to write several ranges, however last one
  be applied to all th functions.<br>The limit on the number of arguments is 15. All variables except 'x' and 'y' will
  be replaced by 'x' and 'y' intuitively

<a id="what-is-implemented"></a>

## What is implemented

- Plotting a graph and specifying the area of definition of a function

<a id="what-is-planned-to-be-implemented"></a>

## What is planned to be implemented

- Function analysis. Function domain, function range, derivatives, critical points, etc.
- Sample analysis. Drawing a graph from the data and subsequent analysis
- New and more user-friendly commands for interaction

<a id="meme"></a>

## Meme

![meme](https://i.ibb.co/tCp83JV/image.png)
