'''
Created on 02/02/2011

@author: suomynonA
@contributor: toboe
'''

from __future__ import print_function
import os
import socket
import urllib, urllib2 
import xml.dom.minidom
import string
from hashlib import md5
from math import ceil


class Downloader (object):
    """
    Searches and downloads the files
    """

    def __init__(self, options, pool):
        """
        Creates and installs the opener to use
        """
        
        self.options = options
        
        self.poolID = pool
        self.downloaded = 0
        self.pos = 1
        self.md5OK = True
        self.temp = string.Template(self.options.temp)
        socket.setdefaulttimeout(self.options.timeout)
        
        #Create and install the opener
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
        self.opener.addheaders = [('User-agent', 'DanbooruPoolDL')]
        urllib2.install_opener(self.opener)
                
                
    def login(self):
        """
        Tries to log in to the booru site and prints if it was successful or not 
        """
        
        print('\nLogging in as ' + self.options.user + '...')
             
        params = urllib.urlencode([('user[name]', self.options.user), 
                                    ('user[password]', self.options.pwd),
                                    ('commit' , 'Login')])
        
        #Login
        urllib2.urlopen('http://e621.net/user/authenticate', params)
        
        #Check if login was done right    
        loginOK = self.checkLogin()
        
        if loginOK:
            print('You are now logged in.\n')
        
        else:
            print('Access denied.')
            raise urllib2.URLError('Access Denied.')
        
    
    def checkLogin(self):
        """
        Checks if the user was logged in correctly
        """
        
        import LoginHandler
                
        #Open the user page 
        page = urllib2.urlopen("http://e621.net/user/home")
        data = page.read()
        
        #Parse the page and check if the login was correct
        handler = LoginHandler.LoginHandler(data)
        return handler.check()
    
        
    def getPosts(self):
        """
        Looks for the tags in the database and stores the resulting posts in the download list 
        """ 
        
        postLimit = 24.0     #How many posts are displayed per page    
        
        #Search for the pool
        poolURL = 'http://e621.net/pool/show.xml?id=%s' % (self.poolID)
        
        connectionSuccess = False
        attempt = 1
        while (attempt <= int(self.options.c_retries)):
            try:
                results = urllib2.urlopen(poolURL)
                connectionSuccess = True
                break
            except Exception as e:
                print('could not connect to site: ', e, '.   Attempt ', attempt, ' of ', self.options.c_retries)
                attempt += 1
        
        if connectionSuccess == False:
            return
    
        #Parse the returned XML
        dom = xml.dom.minidom.parse(results)
        
        info = dom.getElementsByTagName('pool')
        for i in info:
            ats = dict(i.attributes.items())
        
        postCount = float(ats.get('post_count'))
        self.poolName = ats.get('name')
        
        #How many pages does the pool have
        totalPages = ceil(postCount / postLimit) 
        print ("postCount: " + str(postCount) + " , totalPages: " + str(totalPages))
        
        print('%d posts found in pool "%s"' % (postCount, self.poolName), end = '.\n\n')
        
        page = 1.0            #Position in the results
        
        #Get the posts from each page and move to the next one
        while True:
            
            #Get the posts in this page and parse them
            url = poolURL + '&page=%d' % (page)
            
            print("\n" + url);
            results = 0
            connectionSuccess = False
            attempt = 1
            while (attempt <= int(self.options.c_retries)):
                try:
                    results = urllib2.urlopen(url)
                    connectionSuccess = True
                    break
                except Exception as e:
                    print('could not connect to site: ', e, '.   Attempt ', attempt, ' of ', self.options.c_retries)
                    attempt += 1
            
            if connectionSuccess == False:
                print('could not connect to site.  Aborting.')
                return
            
            dom = xml.dom.minidom.parse(results)
            self.posts = dom.getElementsByTagName('post')
            
            #Download the posts in this page and move to the next
            self.downloadPosts()
            page += 1.0
            
            if page > totalPages:
                break
        
        print('\nDownload finished.')
    
    
    def downloadPosts(self):
        """
        Looks for the url of the file in each post and downloads it
        """
        
        destinationFolder = self.options.folder
        previousDir = os.getcwd();
        
        #Create the folder in which files will be downloaded if id does not exists and move to it 
        if not os.path.exists(destinationFolder):
            os.mkdir(destinationFolder)
        
        os.chdir(destinationFolder)
        self.poolName = self.getWindowsFriendlyFilename(self.poolName)
        poolFolder = os.path.join(os.getcwd(),self.poolName)
        
        if not os.path.exists(poolFolder):
            os.mkdir(poolFolder)
        os.chdir(poolFolder)
        
        #Download each file
        for post in self.posts:
            if self.md5OK:
                n = 0
            
            try:
                self.getFile(post)       
                
                if self.options.md5 and not self.md5OK:
                    print('File is corrupt. ', end = '')
                    while n < self.options.c_retries:
                        n+=1
                        print('downloading again.  attempt # ', n, ' of ', self.options.c_retries, '. \n', end = '')
                        self.getFile(post, True)
                    print('.')
            
            except KeyboardInterrupt:
                raise
        
        os.chdir(previousDir)
    
    def getFile(self, post, retry = False):
        """Gets the file from the post"""
        
        #Parse the API XML 
        urlNodes = post.getElementsByTagName('file_url') #Get the url to download the file from
        urlNode = urlNodes.item(0) 
        url = urlNode.firstChild.nodeValue
        print("url: " + str(url))
        
        md5 = post.getElementsByTagName('md5').item(0).firstChild.nodeValue
        rating = post.getElementsByTagName('rating').item(0).firstChild.nodeValue
        id = post.getElementsByTagName('id').item(0).firstChild.nodeValue
        tags = post.getElementsByTagName('tags').item(0).firstChild.nodeValue
        width = post.getElementsByTagName('width').item(0).firstChild.nodeValue
        height = post.getElementsByTagName('height').item(0).firstChild.nodeValue
        file_size = int(post.getElementsByTagName('file_size').item(0).firstChild.nodeValue)
        
        
        #Create the filename based on the settings template and open the file for writing
        if rating == 's':
            rating = 'safe'
        elif rating == 'q':
            rating = 'questionable'
        else:
            rating = 'explicit'
        
        name = self.temp.substitute(pos = self.pos, id = id, md5 = md5, 
                                    tags = tags, rating = rating,  
                                    w = width, h = height)
        
        extension = os.path.splitext(url)[1]
        fullName = name + extension
        
        if file_size > 1024:
            file_size = file_size/1024
            file_size = '%dKB' %file_size
        
        else:
            file_size = '%d B' %file_size
            
        print("Downloading " + url + ' (' + file_size +')... \n', end ='')
                 
        if retry == False:
            if os.path.exists(fullName):
                print ('File already exists.')
                self.pos += 1
                return 
        
        print("Saving to " + os.getcwd() + "\\" + fullName)
        
        outFile = open(fullName, 'wb')        
        
        try:
            file = urllib2.urlopen(url)
            dlFinished = False
            data = file.read()
            outFile.write(data)
            dlFinished = True
                
        except KeyboardInterrupt:
            #If download was aborted delete the incomplete file
            if not dlFinished:
                outFile.close()
                os.remove(fullName)
                self.downloaded -=1
            raise
            
        outFile.close()
        self.downloaded += 1
        
        #If checking is enabled in the settings get the file MD5 sum and compare it with the API's
        if self.options.md5:
            realMD5 = md5
            self.md5OK = self.checkMD5(fullName, realMD5)
            if not self.md5OK:
                outFile.close()
                os.remove(fullName)
                self.downloaded -= 1
                self.pos -= 1
        
        self.pos += 1
        print('Finished.')
    
    def checkMD5(self, filename, realMD5):
        """Calculates the md5 of the file and compares it with realMD5""" 
        
        #Open the file for reading
        f = open(filename, 'rb')
        fileMD5 = md5(f.read())
                
        if not fileMD5.hexdigest() == realMD5:
            return False
        
        return True
    
    
    def getWindowsFriendlyFilename(self, filename):
        print("old filename: ", filename)
        new_filename = filename
        new_filename = new_filename.replace('\\', "")
        new_filename = new_filename.replace('/', "")
        new_filename = new_filename.replace(':', "")
        new_filename = new_filename.replace('*', "")
        new_filename = new_filename.replace('?', "")
        new_filename = new_filename.replace('"', "")
        new_filename = new_filename.replace('<', "")
        new_filename = new_filename.replace('>', "")
        new_filename = new_filename.replace('|', "")
        print("new filename: ", new_filename)
        return new_filename
