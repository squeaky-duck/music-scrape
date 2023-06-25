import requests
import selectorlib
import smtplib
import ssl
import os
import sqlite3

URL = "http://programmer100.pythonanywhere.com/tours/"


class Event:
    def scrape(self, url):
        """Scrape the page source from the URL"""
        response = requests.get(url)
        source = response.text
        return source

    def extract(self, source):
        extractor = selectorlib.Extractor.from_yaml_file("extract.yaml")
        value = extractor.extract(source)["tours"]
        return value


class Email:
    def __init__(self):
        self.host = "smtp.gmail.com"
        self.port = 465
        self.username = os.getenv("EMAILAPPUSERNAME")
        self.password = os.getenv("EMAILNEWSPASSWORD")

    def send(self, message):

        receiver = self.username
        context = ssl.create_default_context()

        with smtplib.SMTP_SSL(self.host, self.port, context=context) as server:
            server.login(self.username, self.password)
            server.sendmail(self.username, receiver, message)


class Database:
    def __init__(self, database_path):
        self.connection = sqlite3.connect(database_path)

    def store(self, extracted_local):
        row_local = extracted_local.split(",")
        row_local = [item.strip() for item in row_local]
        cursor = self.connection.cursor()
        cursor.execute("INSERT INTO events VALUES(?,?,?)", row_local)
        self.connection.commit()

    def read(self, extracted_local):
        row_local = extracted_local.split(",")
        row_local = [item.strip() for item in row_local]
        band, city, date = row_local
        cursor = self.connection.cursor()

        cursor.execute("SELECT * FROM events WHERE band=? AND city=? AND date=?", (band, city, date))
        rows = cursor.fetchall()
        print(rows)
        return rows


if __name__ == "__main__":
    event = Event()
    scraped = event.scrape(URL)
    extracted = event.extract(scraped)
    print(extracted)

    if extracted != "No upcoming tours":
        database = Database(database_path="data.db")
        row = database.read(extracted)
        if not row:
            database.store(extracted)
            email = Email()
            email.send(message="Hey, new event was found!")
