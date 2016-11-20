import webapp2 # To host the server as a web page
import cgi
import random # To designate Ts and Is
import smtplib # To send e-mails
from email.mime.text import MIMEText # To send text in e-mails

currentUsers = []
supportedProviders = []
currentTs = []

emailUsername = 'riprainen@gmail.com'
emailPassword = 'rip connor'

### E-mail stuff
innocentMessage = 'You are innocent.'
tMessage = 'The Ts are '
s = smtplib.SMTP('smtp.gmail.com:587')
s.starttls()
s.login(emailUsername, emailPassword)


### End e-mail stuff

class Provider():
    provider = ''
    gateway = ''

    def __init__(self, providerName, gatewaySuffix):
        self.provider = providerName
        self.gateway = gatewaySuffix


def sendMessage(user);
    if user != None and user.status == 'T':
        msg = MIMEText(tMessage + ', '.join(currentTs))
    else:
        msg = MIMEText(innocentMessage)
    msg['To'] = user.number + user.provider.gateway
    s.sendmail(emailUsername, msg['To'], msg.as_string())
    print 'Message sent'
    

def generateGame(curUsers):
    t1 = random.randrange(0, len(curUsers))
    t2 = random.randrange(0, len(curUsers))
    t3 = random.randrange(0, len(curUsers))

    curUsers[t1].status = 'T'
    curUsers[t2].status = 'T'
    curUsers[t3].status = 'T'
    

class User():
    name = ''
    number = ''
    status = ''
    provider = Provider('', '')

def initializeProviders():
    supportedProviders.append(Provider('AT&T', '@txt.att.net'))
    supportedProviders.append(Provider('Boost Mobile', '@myboostmobile.com'))
    supportedProviders.append(Provider('Sprint', '@messaging.sprintpcs.com'))
    supportedProviders.append(Provider('T-Mobile', '@tmomail.net'))
    supportedProviders.append(Provider('US Cellular', '@email.uscc.net'))
    supportedProviders.append(Provider('Verizon', '@vtext.com'))
        
class AddUserPage(webapp2.RequestHandler):
    def get(self):
        self.response.out.write("""
          <html>
            <body>
              First form is player name; second form is phone number.
              <form action="/sign" method="post">
                <div><textarea name="Player" rows="1" cols="30"></textarea></div>
                <div><textarea name="Number" rows="1" cols="10"></textarea></div><select name="Provider">""")

        for provider in supportedProviders:
            self.response.out.write("""<option value=\""""
                                    + provider.provider.split()[0].lower()
                                    + """\">""" + provider.provider
                                    + """</option>""")
        
        self.response.out.write("""</select>
                <div><input type="submit" value="Add new user"></div>
              </form>
            </body>
          </html>""")

class Guestbook(webapp2.RequestHandler):
    def post(self):
        self.response.out.write('<html><body>You wrote:<pre>')
        self.response.out.write('<br />New player is ' + cgi.escape(self.request.get('Player')))
        self.response.out.write('<br />Player\'s phone number is ' + cgi.escape(self.request.get('Number')))
        self.response.out.write('</pre></body></html>')
        player = User()
        player.name = self.request.get('Player')
        player.number = self.request.get('Number')

        for provider in supportedProviders:
            if provider.provider.split()[0].lower() == self.request.get('Provider'):
                player.provider = provider
        
        self.response.out.write(player.name)
        currentUsers.append(player)

class HelloWebapp2(webapp2.RequestHandler):
    def get(self):
        # for i in range(1,100):
            # self.response.write('Hi!<br />')
        sendMessage(None)
        for user in currentUsers:
            self.response.write(user.name + ' has a number of ' + user.number + '<br />')
            self.response.write('Their provider is ' + user.provider.provider)

app = webapp2.WSGIApplication([
    ('/', HelloWebapp2),
    ('/chi', AddUserPage),
    ('/sign', Guestbook),
], debug=True)

def exitProgram():
    s.quit()

def main():
    from paste import httpserver
    initializeProviders()
    httpserver.serve(app, host='0.0.0.0', port='1885')

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        exitProgram()
