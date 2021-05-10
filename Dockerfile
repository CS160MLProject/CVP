FROM python:3

WORKDIR /usr/src/app
COPY . .

# import all requirements
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5000

# run
CMD ["python", "./app.py"]

