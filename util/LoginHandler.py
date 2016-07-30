'''
Created on 04/10/2010

@author: suomynonA
'''

from HTMLParser import HTMLParser

class LoginHandler(HTMLParser):
    """Parses the user page HTML to check if he's logged in"""

    def __init__(self, data):
        """Constructor"""
        
        HTMLParser.__init__(self)
        
        self.data= data
        
        self.resp=''
        self.inUser = False
      
        
    def handle_starttag(self, tag, attrs):
        if tag == 'div' and attrs[0][1] == 'user-index':
            self.inUser = True


    def handle_data(self, data):
        if self.inUser:
            self.resp = data

    
    def handle_endtag(self,tag):
        if tag == 'h2' and self.inUser:
            self.inUser = False
    
    def check(self):
        self.feed(self.data)
        
        if not self.resp == 'You are not logged in.':
            return True
        
        else: return False