FROM python:3.10

RUN mkdir -p /usr/src/
WORKDIR /usr/src/

COPY . /usr/src/

ENV PYTHONPATH="$PYTHONPATH:/usr/src/"

RUN pip install -r requirements.txt

CMD [ "python", "source/core/bot.py" ]