import urllib.request
import re
import datetime
from time import time, sleep
import smtplib
from email.message import EmailMessage

credentials = open("gmailcredentials.txt").readlines()
gmail_user = re.sub("\n", "", credentials[0])
gmail_password = re.sub("\n", "", credentials[1])
sent_from = gmail_user
send_to = re.sub("\n", "", credentials[2])
appointment_date = ""
body = str("Appointment available on ") + str(appointment_date)
dates = []


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


url = "https://onlinebusiness.icbc.com/qmaticwebbooking/rest/schedule/branches/" \
      "d8225a23dd9830e9684fb00f8aea2fff279c892cb1065244aaa0ae05396a0fe2/dates;" \
      "servicePublicId=da8488da9b5df26d32ca58c6d6a7973bedd5d98ad052d62b468d3b04b080ea25" \
      ";customSlotLength=15"


def get_icbc_appoitments():
    global dates
    webUrl = urllib.request.urlopen(url)
    resp = str(webUrl.read())
    resp = re.sub('"', '', resp)
    data = re.findall(r'{(.*?)}', resp)

    dates.clear()
    for date in data:
        date = date.split(":")
        x = {date[0]: date[1]}
        dates.append(x)


def compare_dates():
    global dates
    global apav
    global appointment_date
    appointment_date = ""
    for instance in dates:
        x = instance['date']
        x = datetime.datetime.strptime(x, "%Y-%m-%d")

        if x < y + datetime.timedelta(days=7):
            appointment_date = x
            apav = 1
            send_mail()
            print(datetime.datetime.now(),
                  x)
            break
        else:
            apav = 0

    # if apav == 0:
    #     print("No appointments available in the next 7 days")
    # don't clutter the console


y = datetime.datetime.today()
print("today is ", y)

apav = 0

while True:
    get_icbc_appoitments()
    compare_dates()
    sleep(30)
