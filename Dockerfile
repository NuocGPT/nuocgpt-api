FROM python:3.9
WORKDIR /app

ADD requirements.txt /app/requirements.txt

RUN pip install -r requirements.txt
RUN pip install chromadb==0.4.8

EXPOSE 8080

COPY ./ /app

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
