import webapp2 # To host the server as a web page
import cgi
import random # To designate Ts and Is
import smtplib # To send e-mails
from email.mime.text import MIMEText # To send text in e-mails
from datetime import datetime # To timestamp the current game

# Consider creating a class to represent the current game + details
# Allows us to customize kinds of games like different messages, sleeper agents, etc.
currentUsers = []
supportedProviders = []
currentTnames = []
currentGame = []
gameTime = datetime.now()

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
    now = gameTime
    preamble = 'For the game on ' + '/'.join([str(now.month), str(now.day), str(now.year)]) + ' starting at ' + ':'.join([str(now.hour), str(now.minute), str(now.second), str(now.microsecond)]) + '\n'
    if user != None:
        if user.status == 'T':
            msg = MIMEText(preamble + tMessage + ', '.join(currentTnames))
        else:
            msg = MIMEText(preamble + innocentMessage)
            
    msg['To'] = user.number + user.provider.gateway
    s.sendmail(emailUsername, msg['To'], msg.as_string())
    print 'Message sent to ' + user.name
    

def generateGame(curUsers):
    #consider making copy of curUsers for currentTnames
    #as is code still may text an innocent who are T

    global gameTime
    gameTime = datetime.now()
    
    for user in curUsers:
        user.status = ''
        
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
        
        
        global currentTnames
        currentTnames = []
        
        global currentGame
        if len(currentUsers): 
          currentGame = generateGame(currentUsers)
 
          for player in currentGame:
            sendMessage(player)
          self.response.out.write('Messages are now sent to each player.')

        else:
          self.response.out.write('No Players')


        self.response.out.write("""
              <html>
                  <body>
               <form action="/">
                <input type="submit" value="Homepage" />
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
                <div><input type="submit" name="Delete" value="Delete user"></div>
                <div><input type="submit" value="Resend recent text"></div
              </form>
            </body>
          </html>""")
        
class NewGuestbook(webapp2.RequestHandler):
    def post(self):

        index = self.request.get('User')
        print index
        
        global currentUsers
        
        
        if len(currentUsers):
          if self.request.get('Delete'):
            currentUsers.pop(int(index))
            self.response.out.write('User Deleted')
          else:
            if len(currentGame):
              sendMessage(currentGame[int(index)])
              self.response.out.write('Resent game to ' + currentGame[int(index)].name)
            else:
              self.response.out.write('No game to resend.')
        else:
          self.response.out.write('No user with which to do anything.')
          
        self.response.out.write("""
              <html>
                  <body>
               <form action="/">
                <input type="submit" value="Homepage" />
                </form>""")
        #global currentUsers
        #currentUsers = []
                                
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
                <input type="submit" value="Homepage" />
                </form>""")



class HelloWebapp2(webapp2.RequestHandler):
    def get(self):
        # for i in range(1,100):
            # self.response.write('Hi!<br />')

        self.response.write('Welcome to the TTT Server. Time for Darkness, Deception and Death. If you do not comply, KYS.' + '<br />' + '<br />')
        
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
            <input type="submit" value="Delete User / Resend Text" />
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
   # initializeUsers() # comment out later
    httpserver.serve(app, host='0.0.0.0', port='3000')

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        exitProgram()
