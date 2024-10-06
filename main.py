from email.mime.text import MIMEText
import smtplib
from datetime import date, datetime, timedelta

from icalendar import Calendar

import requests

response = requests.get("https://ical.da.org/all_athletics.ics")

ical = response.content
calender = Calendar.from_ical(ical)

today = datetime.today()
monday = today + timedelta(days=1)
sunday = monday + timedelta(days=6)

games_list = {
    'Monday': [],
    'Tuesday': [],
    'Wednesday': [],
    'Thursday': [],
    'Friday': [],
    'Saturday': [],
    'Sunday': []
}

def create_list():
    global games_list

    for component in calender.walk():
        if component.name == "VEVENT":
            start = component.get('dtstart').dt

            # Check if the event starts within the desired range
            if isinstance(start, datetime):
                if monday <= start <= sunday:
                    summary = component.get('summary').replace('  ', ' ')
                    if summary[:13] == "Cross-Country" and summary[16:18] == "MS":
                        continue
                    elif summary[summary.find('-') + 2:summary.find('-') + 4] == "MS":
                        continue
                    games_list[start.strftime('%A')].append(summary + " " + start.strftime('%I:%M %p'))
            elif isinstance(start, date):
                if monday.date() <= start <= sunday.date():
                    summary = component.get('summary').replace('  ', ' ')
                    if summary[:13] == "Cross-Country" and summary[16:18] == "MS":
                        continue
                    elif summary[summary.find('-') + 2:summary.find('-') + 4] == "MS":
                        continue
                    games_list[start.strftime('%A')].append(summary + " " + start.strftime('%I:%M %p'))


def write_to_file():
    file = open("log.txt", 'r+')
    file.truncate(0)

    date_tracker = monday
    for day in games_list:
        file.write(day + ' - ' + date_tracker.strftime('%b %d') + '\n')
        if len(games_list[day]) == 0:
            file.write('No games!\n')
        else:
            for game in games_list[day]:
                file.write(game + '\n')
        file.write('\n')
        date_tracker += timedelta(days=1)


def send_email():
    # opens text file for info
    with open("gmail.txt", "r") as f:
        text = f.readlines()

    # input data for email
    subject = monday.strftime('%b %d') + " - " + sunday.strftime('%b %d') + " sports games"
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
    write_to_file()
    while True:
        x = input('Confirm? (Y)es (N)o: ')
        if x == 'Y':
            send_email()
            break
        elif x == 'N':
            break

if __name__ == '__main__':
    main()