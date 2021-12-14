FROM amd64/python:3.7-slim-buster

RUN useradd -ms /bin/sh newuser
USER newuser
WORKDIR /home/newuser

COPY --chown=newuser:newuser requirements.txt ./
RUN pip install -r requirements.txt
COPY --chown=newuser:newuser . .

CMD [ "python3", "-u", "./main.py" ]

