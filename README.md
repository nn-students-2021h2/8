# Team №8

`Roman Burtsev` - Team Leader

`Roman Yezhov` - QA

`Konstantin Rumyantsev` - Code Reviewer

---
<div align="center">

# Function Explorer Bot

[![python](https://img.shields.io/badge/python-3.10%2B-green)]()
[![pylint](https://img.shields.io/badge/linter-pylint-blueviolet)]()
[![Telegram](https://img.shields.io/badge/Telegram-@FunctionExplorerBot-red)]()
[![MongoDB](https://img.shields.io/badge/Database-MongoDB-yellow)]()
[![Docker](https://img.shields.io/badge/Docker-exist-blue)]()

**Function Explorer Telegram Bot** is a tool that allows you to analyse functions, get information about them and draw
graphs.

[What this bot can do](#what-this-bot-can-do) •
[How to find or run the bot](#how-to-find) •
[How to use](#how-to-use) •
[What is planned to be implemented](#what-is-planned-to-be-implemented) •
[Meme](#meme)

</div>


<a id="what-this-bot-can-do"></a>

## What this bot can do?

- Might exist
- Draw graphs with some options
- Analyse math functions (there are many options for this)
- **Send meme**
- Disappoint you

<a id="how-to-find"></a>

## How to run or find the bot?

### If you are a normal user...

Find our bot named "_Function Explorer_" in Telegram:

![none](https://i.ibb.co/C0SqP7B/function-explorer.png)

Then start a conversation with the bot to check if it is activated (`/start` command).

### If you are a normal host...

#### System dependencies briefly:

- Python 3.10+
- TeX Distribution
- MongoDB

1) Clone this repository. Make sure you have Python 3.10+ installed on your machine
2) Create Telegram bot following official [Telegram instructions](https://core.telegram.org/bots#6-botfather)
3) Put your token into `TOKEN` variable in `source/conf/default_config.json`
4) Install TeX distribution. For example, [MiKTeX](https://miktex.org/download) is recommended for Windows
   or [TeX Live](https://www.tug.org/texlive/) is ideal for Linux:
    - If you want to use MiKTeX, then after installing, open application 'MiKTeX Console', click 'Updates' - 'Check for
      updates' - 'Update now'. Install all packages. Then open your IDE, launch the Bot and type him next command: \
      `/analyse domain x` \
      IDE may ask you to install some dependencies of TeX (in popup window). Accept it and wait until installation is
      complete
    - If you want to use TeX Live, then you must also install `texlive-latex-extra` and `dvipng` (via apt-get or
      something else).
5) Install [MongoDB](https://www.mongodb.com/try/download/community) and start server (on Windows it starts
   automatically)
6) After that you can use the bot with your token. Maybe.

### If you are a superconductor...

#### System dependencies briefly:

- Docker
- Docker-compose

If you want to deploy the bot:

1. Find a suitable machine for your bot. For instance, your PC or [Azure](https://azure.microsoft.com/en-us/),
   or [AWS](https://aws.amazon.com/?nc1=h_ls)
2. Install [Docker](https://docs.docker.com/engine/install/)
   and [Docker Compose](https://docs.docker.com/compose/install/)
3. Do steps 1, 2 and 3 of the "If you are a normal host..." instruction above
4. Run command `docker-compose up --build` (you have not to type --build option further without updating the bot) in the
   working directory and wait until all dependencies installed

<a id="how-to-use"></a>

## About commands or how to use?

_The commands below are an alternative way to the handy buttons, so you have not to use or know them_

- `/start` to back to the main menu
- `/help` to... get a help? Here you can check examples of plotting and analysing and guides
- `/graph arg1, arg2, ..., option1, option2, ...` draws a graph of given functions with specified options
  (range / domain / aspect ratio). Options are... optional. See `/resources/graph_patterns.md` to see all (or almost)
  patterns. Functions should be in math format, e.g. _"x = 1",
  "y = x^2 + sin x", "x", "y = 1", "2 y sin x cos(x) = 0.5"_.<br> There are several options:
    - `Domain` - you can add functions domain via argument _"x from _ to \_"_ or _"x = [_, _]"_, for instance,
      _"/graph x, x from -10 to 5", "/graph x = [0.5, 1.5], x^2"_.
    - `Range` - you can also define y-limit by same syntax as domain: _"y from 10 to 20", "y in (-10, 10)"_.
    - `Aspect ratio` - the ratio of the width to the height of a result image: _"aspect ratio = 1", "ratio = 0.5"_

  The limit on the number of functions is 10. Options can override each other. All variables except 'x' and 'y' will be
  replaced by 'x' and 'y' intuitively.
- `/analyse request` tries to perform a user query on a function specified in the query. The function should be in math
  format, for example: _"/analyse domain of sqrt x", "/analyse derivative of the function y * x**2 by x", "period sin
  x"_. You can find sets of patterns in file `/resources/analysis_patterns.md`. Supported actions:
    - Derivative
    - Domain
    - Range
    - Zeros
    - Axes intersection
    - Periodicity
    - Convexity
    - Concavity
    - Vertical asymptotes
    - Horizontal asymptotes
    - Slant asymptotes (with horizontal as a special case of slant)
    - Asymptotes (vertical, horizontal and slant)
    - Evenness and oddness
    - Maximum value
    - Minimum value
    - Stationary points
    - Monotonicity

<a id="what-is-planned-to-be-implemented"></a>

## What is planned to be implemented?

- More actions for analysis
- Better function plotting. New features, functionality and customizable canvas
- Sample analysis. Statistics. Probability theory. Drawing a graph from the data and subsequent analysis
- New and more user-friendly commands for interaction with the bot

<a id="meme"></a>

## Meme

_**About C language**_
![meme](https://i.ibb.co/GFwYyps/Meme.png)
