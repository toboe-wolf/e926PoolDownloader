#!/usr/bin/python

"""
== DanbooruPoolDL ==
    
    Created on 02/02/2011
    @author: suomynonA

    A simple, customizable tool for downloading files from pools
    in Danbooru (http://danbooru.donmai.us)

== System Requirements ==
    Python 2.6(http://python.org)
    or 
    PortablePython 1.1 based on Python 2.6.1 (http://www.portablepython.com/)
    
== Copyright ==
    This script is released under the GNU General Public License 
    (http://www.gnu.org/licenses/gpl.txt)

Check the README.txt file for usage information 
"""

import os
import optparse
import shelve
from util.Downloader import Downloader

__version__ = '0.1.2'
                            
def defaultSettings():
    """
    Reset the settings file to defaults
    """        
    
    settings['login'] = False 
    settings['user'] = ''
    settings['pass'] = ''
    settings['folder'] = r'.'
    settings['f_temp'] = r'[${pos}]${id}_$md5'
    settings['md5'] = True
    settings['retry_corrupt'] = False
    settings['c_retries'] = 2
    settings['timeout'] = 6

    
def changeSetings():
    """
    Show the current settings and ask which one to change
    """
    
    #Divide the settings into groups each setting is stored as (prompt, type, substitution, key)
    loginSets =[('Login', ('bool','%s'), repr(settings['login']),'login'),
                ('User', ('str','%s'), settings['user'],'user'),
                ('Password', ('str','%s'), settings['pass'],'pass')]

    folderSets =[('Destination folder', ('str','%s'), settings['folder'], 'folder'),
                ('Filename template (available keys: $pos $id, $md5, $tags, $rating, $w, $h)', ('str','%s'), settings['f_temp'], 'f_temp')]
    
    connSets =[('Timeout (seconds)', ('int','%d'), settings['timeout'], 'timeout')]
    
    genSets =[('Check files after download', ('bool','%s'), repr(settings['md5']), 'md5'),
              ('Retry corrupt files', ('bool','%s'), repr(settings['retry_corrupt']), 'retry_corrupt'),
              ('Maximum retries on corrupted files', ('int','%d'), settings['c_retries'], 'c_retries')]
    
    n = 0 
    
    #Print the settings
    print '\n--Login--'
    for s in loginSets:
        print  ('[%d]' % n) + ((s[0] + ': ' + s[1][1]) % s[2])
        n+=1
    
    print '\n--Destination folder--'
    for s in folderSets:
        print  ('[%d]' % n) + ((s[0] + ': ' + s[1][1]) % s[2])
        n+=1
    
    print '\n--Connection--'
    for s in connSets:
        print  ('[%d]' % n) + ((s[0] + ': ' + s[1][1]) % s[2])
        n+=1
    
    print '\n--Other--'
    for s in genSets:
        print  ('[%d] ' % n) + ((s[0] + ': ' + s[1][1]) % s[2])
        n+=1
    
    #Put the options in one tuple so the user can select it
    sets = (loginSets + folderSets + connSets + genSets)
    
    print '\n'
    print '[%d] Restore to defaults' % len(sets)
    
    choice = 0          #User choice
    
    #Keep prompting until the user selects exit
    while True:
        try:
            choice = input('\nSelect an option or press Enter to exit: ')
                
            if choice > (len(sets) + 1):
                raise IndexError
        
        except NameError:
            print 'Invalid choice.'
            continue    
        
        except IndexError:
            print 'Invalid choice.'
            continue
        
        except KeyboardInterrupt:
            return
        
        #Ignore the stuff that happens when the user presses enter    
        except Exception as e:
            if e.args[0] == 'unexpected EOF while parsing':
                return
            else :
                raise
        
        if choice < len(sets):
            while True:
                set = sets[choice]
                prompt = (set[0] + ' (' + (set[1][1] % set[2]) + '): ')
                newVal = raw_input(prompt)
                
                if set[1][0] == 'int':
                    try:
                        newVal = int(newVal)
                        break
                    except ValueError:
                            print newVal + " is not a valid number."
                            continue
                    
                if set[1][0] == 'bool':
                    if newVal.lower() == 'true':
                        newVal = True
                        break 
                    if newVal.lower()== 'false':
                        newVal = False
                        break
                    else:
                        print newVal + " is not a valid value."
                        continue
                break
            
            settings[(set[3])] = newVal
            settings.sync()
            print 'Settings updated.'
        
        elif choice == len(sets):
            rly = (raw_input('Are you sure you want to restore all the settings to default values? (Y/N) ')).lower()
            
            if rly == 'y':
                defaultSettings()
                print ('All settings restored to default.')
            else :
                continue
            
        else:
            break
    
    settings.close()


def getOptions():
    """
    Parses the arguments from the command line
    """
    
    #Create the options list
    usage = '%prog POOL_NUMBER [-h] [-s] [-u USER] [-p PASS] [-f FOLDER] [-n TEMPLATE] [--no_md5] [-c RETRIES_ON_CORRUPT_FILE] [-t TIMEOUT]'
    desc = 'A simple, customizable tool for downloading files from pools in Danbooru' 
    
    parser = optparse.OptionParser(usage, description =  desc, version = '%prog ' + __version__, epilog = 'See the README.txt file for more information.')
    
    parser.add_option('-s','--settings', action = 'store_true', dest = 'sets',  
                      help = "Show/Change settings")
    
    parser.add_option('-u','--user', action = 'store', dest ='user')
    
    parser.add_option('-p','--pwd', action = 'store', dest ='pwd',  
                      help = "Overrides use the user and password in the settings file (blank by default)")
    
    parser.add_option('-f','--folder', action = 'store', dest ='folder',  
                      help = "Overrides the destination folder (default is the same folder as the script)")
    
    parser.add_option('-n','--name', action = 'store', dest ='temp',  
                      help = "Overrides the filename tamplate (default is $ID - $md5), available keys are: $pos(post position in the pool) $ID, $md5, $tags, $rating, $w(width), $h(height)")    
    
    parser.add_option('--no_md5', action = 'store_false', dest ='md5',  
                      help = "Overrides whether the md5 of each downloaded file is calculed and checked against the official one (default is to check)")
    
    parser.add_option('-c','--corrupt_retries', action = 'store', dest ='c_retries',  
                      help = "Overrides how many times corrupt files will be retried if checking is enabled(default is 2)")
    
    parser.add_option('-t','--timeout', action = 'store', dest ='timeout',  
                      help = "Overrides the connection timeout in seconds (default is 5)")
    
    #Parse the arguments
    (options, args) = parser.parse_args()
    
    #Check what options are missing and get them from the settings file
    if options.user == None:
        if settings['login']:
            options.user = settings['user']
            options.login = True
        else:
            options.login = False
    else:
        options.login = True
        
    if options.pwd == None:
        options.pwd = settings['pass']
        
    if options.folder == None:
        options.folder = settings['folder']
        
    if options.temp == None:
        options.temp = settings['f_temp']
    
    if options.md5 == None:
        options.md5 = settings['md5']
    
    if options.c_retries == None:
        if options.md5:    
            options.c_retries = settings['c_retries']
        else:
            options.c_retries = 0
              
    if options.timeout == None:
        options.timeout = settings['timeout']
        
    return (options, args)
        

def main():
    """Gets the console options and starts the download"""
    
    options,args = getOptions()
    
    if options.sets:
        changeSetings()
        return
    
    if len(args) == 0 and not options.sets:
        print 'You must write a pool ID.'
        return
    
    downloader = Downloader(options, args[0])
    
    if options.login:
        downloader.login()
    
    downloader.getPosts()
    

if __name__ == '__main__':
    #Check if the settings file exists
    if not os.path.exists('settings'):
        print '\nWARNING: Settings file could not be found, creating default one\n'
        settings = shelve.open('settings', writeback = True)
        defaultSettings()
        settings.close
    
    settings = shelve.open('settings', writeback = True)
    
    try:
        main()
    
    except KeyboardInterrupt:
        print "Stopped."
    
    finally:
        settings.close()

    