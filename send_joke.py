import time, json, random, operator
from webbot import Browser
from collections import defaultdict

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class Joker():
  def __init__(self):
    self.url = 'https://appli.loveboxlove.fr/'
    self.message_signature = '\n\n/Olof'
    # self.box_name = 'Farmor'
    self.box_name = 'Sonjany'

    with open('cred.json') as infile:
      self.login_info = json.load(infile)

  def get_joke(self):
    with open('sent_jokes.json') as f:
      sent_jokes = json.load(f)

    sent_jokes = defaultdict(int, sent_jokes)
    jokes = sorted(sent_jokes.items(), key=operator.itemgetter(1))

    joke_to_send = jokes[0][0]
    return joke_to_send, sent_jokes
    
  def add_to_seen_joke(self, sent_jokes, joke):
    ''' Keep track of which jokes has been sent '''
    sent_jokes[joke] += 1
    with open('sent_jokes.json', 'w') as outfile:
      json.dump(sent_jokes, outfile)

  def send_joke(self, joke):
    self.web = Browser(showWindow=True)
    # self.web = Browser(showWindow=False)
    self.log_in()
    # self.switch_box()
    message = self.send_message(joke)
    self.send_email(message)

  def log_in(self):
    web = self.web
    web.go_to(self.url)
    time.sleep(5)
    web.click('Start!')
    web.type(self.login_info['user'], into='Email')
    web.press(web.Key.ENTER)
    time.sleep(1)
    web.type(self.login_info['passw'], into='Email')
    web.press(web.Key.ENTER)

  def switch_box(self):
    web = self.web
    time.sleep(1)
    web.click(id='select-6-0') # Select lovebox dropdown
    time.sleep(1)

    web_ele = web.find_elements(tag='ion-label', text=self.box_name)[0]
    web_ele_id = web_ele.get_attribute('id')
    id_int = int(''.join(filter(str.isdigit, web_ele_id)))
    button_id = 'rb-{}-0'.format(id_int)

    web.click(id=button_id) # Switch lovebox

  def close_extra_windows(self):
    # Close their two stupid extra windows that gets opened
    web = self.web
    time.sleep(1)
    web.press(web.Key.ESCAPE)
    time.sleep(1)
    web.press(web.Key.ESCAPE)

  def send_message(self, joke):
    self.close_extra_windows()
    web = self.web
    time.sleep(1)
    web.click('Send message')

    time.sleep(1)
    web.click(id='message')

    message = joke + self.message_signature
    max_message_length = 168
    assert len(message) < max_message_length
    time.sleep(1)
    web.type(message)

    # Find send-message button
    inner_send = web.find_elements(tag='ion-icon', classname='send-ico')[0]
    get_parent = lambda x: x.find_element_by_xpath('..')

    time.sleep(1)
    parent = get_parent(inner_send)
    grand_parent = get_parent(parent)
    # grand_parent.click() # Send message
    print("Message Sent!")
    return message


  def send_email(self, message):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    usr = self.login_info['email_user']
    pwd = self.login_info['email_passw']
    server.login(usr, pwd)

    fromaddr = "olof.apartment.afb@gmail.com"
    toaddr = self.login_info['user']
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = 'Joke to Grandma!'

    body = message
    msg.attach(MIMEText(body, 'plain'))
     
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()
    print("Email sent!")

  def close_down(self):
    time.sleep(5)
    self.web.quit()


def reset_sent_jokes_counter():
  with open('jokes.txt') as f:
    all_jokes = f.read().split('\n\n')

  sent_jokes = defaultdict(int)
  for joke in all_jokes:
    sent_jokes[joke] = 0

  with open('sent_jokes.json', 'w') as outfile:
    json.dump(sent_jokes, outfile)

# reset_sent_jokes_counter()

message_timer_low = mtl = 1 * 24 * 60 * 60 # One day
message_timer_high = mth = 2 * 24 * 60 * 60 # Two days

# message_timer_low = mtl = 13 * 60 # minutes
# message_timer_high = mth = 45 * 60 # minutes
joker = Joker()
while True:
  time_until_next_message = random.randint(mtl, mth)
  try:
    joke, sent_jokes = joker.get_joke()
    joker.send_joke(joke)
    joker.close_down()
    joker.add_to_seen_joke(sent_jokes, joke)
    time.sleep(time_until_next_message)
  except Exception as e:
    joker.close_down()
    e_msg = str(e)
    print(e_msg)
    email_msg = 'Some error occured while sending grandmas joke. '
    joker.send_email(email_msg + e_msg)
  # time.sleep(60) # Sleep for one minute
  time.sleep(1000) # Sleep

