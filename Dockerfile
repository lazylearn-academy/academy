FROM python:alpine
EXPOSE 5000
WORKDIR /app
COPY ./app/requirements.txt .
RUN pip3 install -r requirements.txt
COPY . .
RUN chmod a+x docker/*.sh
CMD python3 app.py