# By Eyob Tefera and Alexander Chi 11/20/2016

import webapp2 # To host the server as a web page
import cgi
import random # To designate Ts and Is
import smtplib # To send e-mails
from email.mime.text import MIMEText # To send text in e-mails
from datetime import datetime # To timestamp the current game
from tinydb import TinyDB, Query # To handle persistent data like user info and wins

# Consider creating a class to represent the current game + details
# Allows us to customize kinds of games like different messages, sleeper agents, etc.
currentUsers = []
supportedProviders = []
currentTnames = []
currentGame = []
gameTime = datetime.now()
numberTs = 3
emailUsername = 'riprainen@gmail.com'
emailPassword = ''#private ask Alex or Eyob if required
##userDB = Database('/tmp/users') # change this somewhere more permanent
##gamesDB = Database('/tmp/games') # change this somewhere more permanent
userDB = TinyDB('Users.json')
gamesDB = TinyDB('Games.json')


### E-mail stuff
innocentMessage = 'You are innocent.'
tMessage = 'You are a Traitor. Fellow Ts are '
s = smtplib.SMTP('smtp.gmail.com:587')
s.starttls()
s.login(emailUsername, emailPassword)


### End e-mail stuff

class Provider(object):
    provider = ''
    gateway = ''

    def __init__(self, providerName, gatewaySuffix):
        self.provider = providerName
        self.gateway = gatewaySuffix


def sendMessage(user=None, msgStatus='start'):
#can also do case switch statements
    if msgStatus == 'start':
        now = gameTime
        preamble = 'For the game on ' + '/'.join([str(now.month), str(now.day), str(now.year)]) + ' starting at ' + ':'.join([str(now.hour), str(now.minute), str(now.second), str(now.microsecond)]) + '\n'
        if user != None:
            if user.status == 'T':
                msg = MIMEText(preamble + tMessage + ', '.join(currentTnames))
            else:
                msg = MIMEText(preamble + innocentMessage)

    if msgStatus == 'newPlayerTest':
        msg = MIMEText('WELCOME TO TTT.')

    if msgStatus == 'confirmCurrentPlayers':
        msg = MIMEText('You are enrolled for the next game session.')
        
    try:        
        msg['To'] = user.number + user.provider.gateway
        s.sendmail(emailUsername, msg['To'], msg.as_string())
        print 'Message sent to ' + user.name
    except:
        print 'Message failed'
    

def initializeDatabases():
    pass
##    try:
##        userDB.open()
##    except:
##        userDB.create()
##    try:
##        gamesDB.open()
##    except:
##        gamesDB.create()
    
    
        

def generateGame(curUsers):
    #consider making copy of curUsers for currentTnames
    #as is code still may text an innocent who are T

    global gameTime
    gameTime = datetime.now()
    
    for user in curUsers:
        user.status = ''

    global currentTnames  
    global numberTs
    
    for _ in range(numberTs):
        t = random.randrange(0,len(curUsers))
        curUsers[t].status = 'T'
        currentTnames.append(curUsers[t].name)

    currentTnames = list(set(currentTnames))
    
    return curUsers
    

class User(object):
    name = ''
    number = ''
    status = ''
    provider = Provider('', '')

    def __init__(self, name = '', number = '', status = '', provider = Provider('', '')):
        self.name = name
        self.number = number
        self.status = status
        self.provider = provider

    def asDict(self):
        return {'name' : self.name, 'number' : self.number, 'status' : self.status, 'provider' : self.provider.__dict__}

    def __eq__(self, other): 
        return self.asDict() == other.asDict()
    


def initializeUsers():
    pass
##    playerAlex = User()
##    playerAlex.name = 'Alex Chi'
##    playerAlex.number = '8184394582'
##    playerAlex.provider = supportedProviders[-1]
##    currentUsers.append(playerAlex)

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
       #if self.request.get('numTs') is not None: 
       # numberTs = int(self.request.get('numTs'))
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
    def post(self):
        global numberTs
        try:
          numberTs = int(self.request.get('numTs'))
          self.redirect("/startgame")
        except:
          self.response.out.write('Please enter a valid number.')
          
    
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

def commitUserToDatabase(player):
    # Don't forget to include this in a delete method that runs for every user @ exitProgram() time
    # Maybe consider two players on the same phone?
##    player_dict = player.__dict__
##    userDB.add_index(player.number)
##    print userDB.insert(player_dict)
##    print player_dict
##    tester = {'name': player.name, 'number': player.number, 'provider' : player.provider.provider}
    if not userDB.get(Query().number == player.number):
      userDB.insert(player.asDict())
    else:
      userDB.update(player.asDict(), Query().number == player.number) # This updates things including those that aren't updated often (name, number). Maybe add a function to user for the stats worth updating (score, etc.)
##    print tester
##    print player.__dict__
##    print player.asDict()
    print userDB.all()
        
class NewGuestbook(webapp2.RequestHandler):
    def post(self):

        index = self.request.get('User')
        print index
        
        global currentUsers
        
        
        if len(currentUsers):
          if self.request.get('Delete'):
            removePlayerFromSession(currentUsers[int(index)])
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

def addPlayerToSystem(player):
        commitUserToDatabase(player)
        currentUsers.append(player)
        sendMessage(player, 'newPlayerTest')

class ResendToAll(webapp2.RequestHandler):
    def get(self):
        for player in currentUsers:
            sendMessage(player, 'confirmCurrentPlayers')
        self.redirect('/')
    
                                
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
        addPlayerToSystem(player)

        self.response.out.write("""
              <html>
                  <body>
               <form action="/">
                <input type="submit" value="Homepage" />
                </form>""")

class PlayerList(webapp2.RequestHandler):
    def get(self):
        u = Query()
        self.response.out.write('<form action="/playerlist" method="post">')
        for user in userDB.all():
            #self.response.out.write('<br />' + user['name'] + '\t\t\t' + user['number'])
            self.response.out.write('<input type="checkbox" name="' + user['number'] + '" value="test"' + (' checked="true"' if buildUserFromDict(user) in currentUsers else '') +'>' + user['name'] + '\t\t\t' + user['number'] + '</input><br />')
        self.response.out.write('<br /><input type="submit" value="Submit" /></form><br />')
       # print userDB.get(u.name=='Alex')['number']

        if len(currentUsers):
            self.response.out.write('Current Players are: <br />')
        
        for user in currentUsers:
            self.response.write(user.name + '<br />')

        self.response.out.write("""
              <html>
                  <body>
               <form action="/">
                <input type="submit" value="Homepage" />
                </form>""")


    def post(self):
        player = User()
        # Currently O(n^2), maybe can fix with a try{}expect for the else
        for user in userDB.all():
            if self.request.get(user['number']):
                currentPlayer = buildUserFromDict(user)
                if currentPlayer not in currentUsers:
                    currentUsers.append(currentPlayer)
            else:
                currentPlayer = buildUserFromDict(user)
                if currentPlayer in currentUsers:
                    removePlayerFromSession(currentPlayer)
                
        self.get()
        
        
        
def buildUserFromDict(userDict):
    return User(name=userDict['name'], number = userDict['number'], provider = Provider(userDict['provider']['provider'], userDict['provider']['gateway']))

def removePlayerFromSession(userObj):
    commitUserToDatabase(userObj)
    currentUsers.remove(userObj)
                                


class HelloWebapp2(webapp2.RequestHandler):
    def get(self):
        # for i in range(1,100):
            # self.response.write('Hi!<br />')

        self.response.write('Welcome to the TTT Server. Time for Darkness, Deception and Death. If you do not comply, KYS.' + '<br />' + '<br />')

        self.response.write('Set Max Number of T\'s, Current set to ' + str(numberTs) + '<br />')
        
        self.response.write("""
          <html>
              <body>
           <form action="/startgame" method="post"><div><textarea name="numTs" rows="1" cols="2"></textarea>
            <input type="submit" value="Change and Start" /></div></form>""")

        
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
           <form action="/playerlist">
            <input type="submit" value="Add Players from List" />
            </form>""")

        self.response.out.write("""
          <html>
              <body>
           <form action="/resendtoall">
            <input type="submit" value="Text to Confirm CurrentPlayers" />
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
    ('/playerlist', PlayerList),
    ('/resendtoall', ResendToAll),
], debug=True)

def exitProgram():
    userDB.close()
    gamesDB.close()
    s.quit()

def main():
    from paste import httpserver
    initializeProviders()
    #initializeUsers() # comment out later
    httpserver.serve(app, host='0.0.0.0', port='3000')

if __name__ == '__main__':
    initializeDatabases()
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        exitProgram()
