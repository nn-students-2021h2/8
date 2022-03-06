# Team №8

`Roman Burtsev` - Team Leader

`Roman Yezhov` - QA

`Konstantin Rumyantsev` - Code Reviewer

---
<div align="center">

# Function Explorer Bot

[![python](https://img.shields.io/badge/python-3.10%2B-green)]()
[![pylint](https://img.shields.io/badge/linter-pylint-blue)]()
[![TeX](https://img.shields.io/badge/TeX_Distribution-MiKTeX-red)]()
[![MongoDB](https://img.shields.io/badge/Database-MongoDB-yellow)]()

**Function Explorer Telegram Bot** is a tool that allows you to analyse functions, get information about them and draw
graphs. This README.md will be added to as the project progresses.

[How to use](#how-to-use) •
[What is implemented](#what-is-implemented) •
[What is planned to be implemented](#what-is-planned-to-be-implemented) •
[Meme](#meme)

</div>

<br>

<a id="how-to-use"></a>

## How to use

Find our bot named "function explorer" in Telegram:

![none](https://i.ibb.co/yqPb8Xn/function-explorer.png)

Then start a conversation with the bot to check if it is activated.

If you want to use your bot token, then:

1) Clone this repository. Make sure you have Python 3.10+ installed on your machine
2) Create Telegram bot following official [Telegram instructions](https://core.telegram.org/bots#6-botfather)
3) Put your token into `TOKEN` variable in `source/conf/default_config.json`
4) Install TeX distribution [MiKTeX](https://miktex.org/download). It is required to display text in TeX view. After
   installing, open application 'MiKTeX Console', click 'Updates' - 'Check for updates' - 'Update now'. Install all
   packages. Then open your IDE, launch the Bot and type him next command: \
   `/analyse domain x` \
   IDE may ask you to install some dependencies of TeX (in popup window). Accept it and wait until installation is
   complete  
5) Install [MongoDB](https://www.mongodb.com/try/download/community) and start server 
6) After that you can use the bot with your token

About commands:

- `/graph arg1, arg2, ...` draws a graph of given functions. Functions should be in math format, e.g. _"x = 1",
  "y = x^2 + sin(x)", "x", "y = 1"_.<br>You can also add functions domain via argument "**from _ to _**", for instance,
  _"/graph x, from -10 to 5", "/graph from 0.5 to 1.5, x^2"_. It is possible to write several ranges, however last one
  be applied to all th functions.<br>The limit on the number of arguments is 15. All variables except 'x' and 'y' will
  be replaced by 'x' and 'y' intuitively
- `/analyse request1` tries to perform a user query on a function specified in the query. The function should be in math
  format. You can find sets of patterns in file `/resources/analysis_patterns.md`. Supported actions:
  - Derivative
  - Domain
  - Range
  - Zeros
  - Axes intersection
  - Periodicity
  - Convexity
  - Concavity
  - Continuity
  - Vertical asymptotes
  - Horizontal asymptotes
  - Slant asymptotes (with horizontal as a special case of slant)
  - Asymptotes (vertical, horizontal and slant)
  - Evenness and oddness
  - Maximum value
  - Minimum value
  - Stationary points

<br>

<a id="what-is-implemented"></a>

## What is implemented

- Plotting a graph and specifying the area of definition of a function
- Function analysis. Function domain, function range, derivatives, critical points, etc.

<br>

<a id="what-is-planned-to-be-implemented"></a>

## What is planned to be implemented

- More function for analysis
- Better function plotting. New features and functionality
- Sample analysis. Drawing a graph from the data and subsequent analysis
- New and more user-friendly commands for interaction

<br>

<a id="meme"></a>

## Meme

_**About C language**_
![meme](https://i.ibb.co/GFwYyps/Meme.png)
