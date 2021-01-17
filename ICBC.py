import urllib.request
import re
import datetime
from time import time, sleep
import smtplib
from email.message import EmailMessage

access_points = open("access_points.txt").readlines()
locations = {}
dates = {}
credentials = open("gmailcredentials.txt").readlines()
gmail_user = re.sub("\n", "", credentials[0])
gmail_password = re.sub("\n", "", credentials[1])
sent_from = gmail_user
send_to = re.sub("\n", "", credentials[2])
appointment_date = {}
longaddress1 = "https://onlinebusiness.icbc.com/qmaticwebbooking/rest/schedule/branches/"
longaddress2 = "/dates;servicePublicId=da8488da9b5df26d32ca58c6d6a7973bedd5d98ad052d62b468d3b04b080ea25" \
               ";customSlotLength=15"
today = datetime.datetime.today()
body = ""
icbc_link = "https://onlinebusiness.icbc.com/qmaticwebbooking/"

def get_locations():
    for location in access_points:
        x = re.sub('\n', "", location)
        y = x.split(":")
        z = {y[0]:y[1]}
        locations.update(z)


def get_icbc_appoitments():
    global dates
    global locations
    x = locations.keys()

    try:
        for key in x:
            dts = []
            locurl = locations.get(key)
            url = longaddress1 + locurl + longaddress2
            webUrl = urllib.request.urlopen(url)
            resp = str(webUrl.read())
            resp = re.sub('"', '', resp)
            resp = re.sub("date:", "", resp)
            data = re.findall(r'{(.*?)}', resp)


            try:
                for y in data:
                    y = datetime.datetime.strptime(y, "%Y-%m-%d")
                    dts.append(y)
                dates.update({key:min(dts)})
            except:
                print("Cannot find the earliest date")

    except:
        print("Cannot connect to ICBC booking server")


def send_mail():
    msg = EmailMessage()
    msg.set_content(body)

    msg['From'] = gmail_user
    msg['To'] = send_to
    msg['Subject'] = "ICBC Appointment availability"

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
        server.send_message(msg)
        server.close()

        print("email sent")
    except:
        print("something's wrong")


def compare_dates():
    global dates
    global apav
    global appointment_date
    appointment_date.clear()
    dts = dates.keys()
    apav = 0

    for location in dts:
        x = dates[location]

        if x < today + datetime.timedelta(days=7):
            appointment_date.update({location: x})
            apav = 1


def email_appointments():
    global body
    if apav == 1:
        intr = "Appointments available: \n"
        adk = appointment_date.keys()
        dts = ""
        for ad in adk:
            apd = "in {} on {}. \n"
            apd = apd.format(ad, datetime.datetime.strftime(appointment_date[ad], "%Y-%m-%d"))
            dts = dts + apd

        body = intr + apd + "book here: \n" + icbc_link
        send_mail()


while True:
    get_locations()
    get_icbc_appoitments()
    compare_dates()
    email_appointments()
