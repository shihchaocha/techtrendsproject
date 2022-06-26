FROM python:3.8
LABEL maintainer="Shi-Cho Cha"

WORKDIR /home/myuser

COPY ./techtrends/. .

RUN pip install -r requirements.txt
RUN python init_db.py

CMD [ "python", "app.py" ]
