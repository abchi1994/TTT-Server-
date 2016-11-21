import webapp2 # To host the server as a web page
import cgi
import random # To designate Ts and Is
import smtplib # To send e-mails
from email.mime.text import MIMEText # To send text in e-mails

currentUsers = []
supportedProviders = []
currentTnames = []

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


def sendMessage(user):
    if user != None and user.status == 'T':
        msg = MIMEText(tMessage + ', '.join(currentTnames))
    else:
        msg = MIMEText(innocentMessage)
    msg['To'] = user.number + user.provider.gateway
    s.sendmail(emailUsername, msg['To'], msg.as_string())
    print 'Message sent to ' + user.name
    

def generateGame(curUsers):
    
    t1 = random.randrange(0, len(curUsers))
    t2 = random.randrange(0, len(curUsers))
    t3 = random.randrange(0, len(curUsers))

    curUsers[t1].status = 'T'
    curUsers[t2].status = 'T'
    curUsers[t3].status = 'T'

    global currentTnames
    currentTnames.append(curUsers[t1].name)
    currentTnames.append(curUsers[t2].name)
    currentTnames.append(curUsers[t3].name)

    currentTnames = list(set(currentTnames))    
    
    return curUsers
    

class User():
    name = ''
    number = ''
    status = ''
    provider = Provider('', '')


def initializeUsers():
    playerAlex = User()
    playerAlex.name = 'Alex Chi'
    playerAlex.number = '8184394582'
    playerAlex.provider = supportedProviders[-1]
    currentUsers.append(playerAlex)

def initializeProviders():
    supportedProviders.append(Provider('AT&T', '@txt.att.net'))
    supportedProviders.append(Provider('Boost Mobile', '@myboostmobile.com'))
    supportedProviders.append(Provider('Metro PCS', '@mymetropcs.com'))
    supportedProviders.append(Provider('Sprint', '@messaging.sprintpcs.com'))
    supportedProviders.append(Provider('T-Mobile', '@tmomail.net'))
    supportedProviders.append(Provider('US Cellular', '@email.uscc.net'))
    supportedProviders.append(Provider('Verizon', '@vtext.com'))
        
class StartGame(webapp2.RequestHandler):
    def get(self):
        self.response.out.write('Messages are now sent to each player.')
        for player in generateGame(currentUsers):
            sendMessage(player)
        global currentTnames
        currentTnames = []

        self.response.out.write("""
              <html>
                  <body>
               <form action="/">
                <input type="submit" value="Player List" />
                </form>""") 
        
    
class AddUserPage(webapp2.RequestHandler):
    def get(self):
        self.response.out.write("""
          <html>
            <body>
              First form is player name; second form is phone number (10 Digit).
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

class DeleteUserPage(webapp2.RequestHandler):
     def get(self):
        self.response.out.write("""
          <html>
            <form action="/deleted" method="post">
               </div><select name="User">""")
        
        for user in currentUsers:            
            self.response.out.write("""<option value=\""""
                                    + str(currentUsers.index(user))
                                    + """\">""" + user.name
                                    + """</option>""")   
        
        
        self.response.out.write("""</select>
                <div><input type="submit" value="Delete user"></div>
              </form>
            </body>
          </html>""")            
        
class NewGuestbook(webapp2.RequestHandler):
    def post(self):
        self.response.out.write('User Deleted')
        
          if self.request.get('User') in currentUsers:
            currentUsers.remove(currentUsers.pop(user))     

        self.response.out.write("""
              <html>
                  <body>
               <form action="/">
                <input type="submit" value="Player List" />
                </form>""")
                                
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

        self.response.out.write("""
              <html>
                  <body>
               <form action="/">
                <input type="submit" value="Player List" />
                </form>""")



class HelloWebapp2(webapp2.RequestHandler):
    def get(self):
        # for i in range(1,100):
            # self.response.write('Hi!<br />')

        self.response.write('Welcome to the TTT Server. Time for Darkness, Deceipt or Death. If you do not comply, KYS.' + '<br />' + '<br />')
        
        for user in currentUsers:
            self.response.write(user.name + ' has a number of ' + user.number + '<br />')
            self.response.write('Their provider is ' + user.provider.provider + '<br />' + '<br />')

        self.response.out.write("""
          <html>
              <body>
           <form action="/chi">
            <input type="submit" value="Add New User" />
            </form>""")

        self.response.out.write("""
          <html>
              <body>
           <form action="/eyob">
            <input type="submit" value="Delete User" />
            </form>""")

        self.response.out.write("""
          <html>
              <body>
           <form action="/startgame">
            <input type="submit" value="Start Game" />
            </form>""")            

app = webapp2.WSGIApplication([
    ('/', HelloWebapp2),
    ('/chi', AddUserPage),
    ('/eyob', DeleteUserPage),
    ('/sign', Guestbook),
    ('/deleted', NewGuestbook),
    ('/startgame', StartGame),
], debug=True)

def exitProgram():
    s.quit()

def main():
    from paste import httpserver
    initializeProviders()
    initializeUsers() # comment out later
    httpserver.serve(app, host='0.0.0.0', port='3000')

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        exitProgram()
