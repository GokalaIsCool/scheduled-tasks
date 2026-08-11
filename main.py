
import datetime as dt
import pandas as pd
import os
hello=pd.read_csv("birthdays.csv")
now=dt.datetime.now()
day_now=now.day
month_now=now.month
print(hello,"\n")

password = os.environ.get("MY_PASSWORD")

for index,row in hello.iterrows():
    if month_now and day_now in [row["month"],row["day"]]:
        bday_person=row["name"]
        bday_email=row["email"]

with open("letter_templates\letter_1.txt",mode="r") as file:
    filedata=file.read()

filedata=filedata.replace("[NAME]",bday_person)

with open("letter_templates\letter_new.txt",mode="w") as file:
    file.write(filedata)

with open("letter_templates\letter_new.txt") as file:
    bday=file.read()
import smtplib
bday_email = os.environ.get("MY_EMAIL")


with smtplib.SMTP("smtp.gmail.com") as connection:
    connection.starttls()
    connection.login(user=bday_email,password=password)
    connection.sendmail(
        from_addr=bday_email,
        to_addrs=bday_email,
        msg=bday
    )
