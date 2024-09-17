FROM python:alpine
WORKDIR /tg_bot
COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY . .
CMD python3 bot.py