from email.mime.text import MIMEText
import smtplib
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup

response = requests.get("https://www.da.org/fs/elements/2244/")
soup = BeautifulSoup(response.text, 'html.parser')

file = open("log.txt", 'r+')
file.truncate(0)

def create_list():
    now = datetime.now()

    for i in range(7):
        now += timedelta(days=1)
        file.write(now.strftime('%A') + " - " + now.strftime("%b %d") + "\n")
        stuff = soup.find('div', attrs={"class": "fsCalendarDate", "data-day": now.strftime('%#d'), "data-month": str(int(now.strftime("%#m"))-1)})
        if stuff is None:
            file.write("Something went wrong.")
        elif(len(stuff.parent['class']) == 2 and stuff.parent['class'][1] == "fsStateHasEvents"):
            a = stuff.find_next_siblings()
            for game in a:
                bruh_momento = " ".join(game.text.replace("*", "").split())[20:]
                if(bruh_momento[:13] == "Cross-Country" and bruh_momento[16:18] == "MS"):
                    continue
                elif(bruh_momento[bruh_momento.find('-')+2:bruh_momento.find('-')+4] == "MS"):
                    continue    
                file.write(bruh_momento + "\n")
        else:
            file.write("No games!\n")
        file.write("\n")
    file.close()

def send_email():
    # opens text file for info
    now = datetime.now()
    day = now.strftime("%b %d")
    week_end = (now + timedelta(days=6)).strftime("%b %d")
    with open("gmail.txt", "r") as f:
        text = f.readlines()

    # input data for email
    subject = day + " - " + week_end + " sports games"
    body = open("log.txt", 'r').read()
    sender = text[0].strip()[17:]
    recipients = []
    p = text[1].strip()[5:]
    for i in range(len(text)-4):
        recipients.append(text[i+4].strip())
    f.close()

    # creates actual email and sends it
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
       smtp_server.login(sender, p)
       smtp_server.sendmail(sender, recipients, msg.as_string())
    print("send email!")

def main():
    create_list()
    send_email()

if __name__ == '__main__':
    main()