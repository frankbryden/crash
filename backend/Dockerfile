FROM python:3.12

WORKDIR /app
COPY pyproject.toml .

COPY src src
RUN pip install .
ENV PATH="$PATH:$(which pytest)" 

CMD python -m fastapi run src/crash/main.py