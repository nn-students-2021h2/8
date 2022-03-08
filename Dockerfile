FROM python:3.10

# Set a time zone (can't be done automatically, lol)
ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Pull newest versions of packages
RUN apt-get update && apt-get upgrade -y

# Install latex-distribution and its dependencies
RUN apt-get install texlive -y
RUN apt-get install texlive-latex-extra -y
RUN apt-get install dvipng -y

# Create working directory
RUN mkdir -p /usr/src/app/
WORKDIR /usr/src/app/
ENV PYTHONPATH="$PYTHONPATH:/usr/src/app/"

# Install project requirements
ADD ./requirements.txt /usr/src/app/
RUN pip install -r requirements.txt
ADD . /usr/src/app/
RUN rm ~/.cache/matplotlib -fr

# Run bot
CMD [ "python", "source/core/bot.py" ]
