import time, json, random, operator
from webbot import Browser
from collections import defaultdict

class Joker():
  def __init__(self):
    self.url = 'https://appli.loveboxlove.fr/'
    # self.web = Browser(showWindow=True)
    self.web = Browser(showWindow=False)
    self.message_signature = '\n\n/Olof'

    with open('cred.json') as infile:
      self.login_info = json.load(infile)

  def get_joke(self):
    with open('sent_jokes.json') as f:
      sent_jokes = json.load(f)

    sent_jokes = defaultdict(int, sent_jokes)
    jokes = sorted(sent_jokes.items(), key=operator.itemgetter(1))

    joke_to_send = jokes[0][0]
    self.add_to_seen_joke(sent_jokes, joke_to_send)
    # self.reset_sent_jokes_counter()

    return joke_to_send
    
  def add_to_seen_joke(self, sent_jokes, joke):
    sent_jokes[joke] += 1
    with open('sent_jokes.json', 'w') as outfile:
      json.dump(sent_jokes, outfile)


  def reset_sent_jokes_counter(self):
    with open('jokes.txt') as f:
      all_jokes = f.read().split('\n\n')

    sent_jokes = defaultdict(int)
    for joke in all_jokes:
      sent_jokes[joke] = 0

    with open('sent_jokes.json', 'w') as outfile:
      json.dump(sent_jokes, outfile)

  def send_joke(self, joke):
    self.log_in()
    self.switch_box()
    self.send_message(joke)
    self.close_down()

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
    web_ele = web.find_elements(tag='ion-label', text='Farmor')[0]
    web_ele_id = web_ele.get_attribute('id')
    id_int = int(''.join(filter(str.isdigit, web_ele_id)))
    button_id = 'rb-{}-0'.format(id_int)

    web.click(id=button_id) # Switch lovebox

  def send_message(self, joke):
    web = self.web
    time.sleep(1)
    web.click('Send message')

    time.sleep(1)
    web.click(id='message')

    message = joke + self.message_signature
    max_message_length = 168
    assert len(message) < max_message_length
    web.type(message)

    # Find send-message button
    inner_send = web.find_elements(tag='ion-icon', classname='send-ico')[0]
    get_parent = lambda x: x.find_element_by_xpath('..')

    parent = get_parent(inner_send)
    grand_parent = get_parent(parent)
    # grand_parent.click() # Send message
    print("Message Sent!")


  def close_down(self):
    time.sleep(5)
    self.web.quit()


message_timer_low = mtl = 1 * 24 * 60 * 60 # One day
message_timer_high = mth = 2 * 24 * 60 * 60 # Two days
joker = Joker()
while True:
  time_until_next_message = random.randint(mtl, mth)
  try:
    joke = joker.get_joke()
    joker.send_joke(joke)
    time.sleep(time_until_next_message)
  except Exception as e:
    print(str(e))
    time.sleep(60) # Sleep for one minute

