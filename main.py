#!/usr/bin/env python
""" HoN Server monitor (HoNMonitor). """

import sys, threading, signal, re, time
from os import getpid, uname
from setproctitle import setproctitle
from daemon import Daemon
from honcore import * 
from core import *
import config

acc_config = {"username" : "", "password" : ""}
basic_config = {"masterserver" : None, "honver" : None}
down_count = 0

class HoNStatus:
    def __init__(self):
        self.client = client.HoNClient()

    def configure(self):
        """ 
        Sets up the data from the database so it can be used for setting...settings.
        The DB structure sucks, so some extra processing to get the correct datatypes.
        TODO: Clean up, I'm writing this at 2AM..
        """

        log.info("Loading configuration from the database...")
        settings = dict(db.query("""SELECT `key`, `value`  FROM settings"""))
    
        log.info("Config loaded")
        log.info("Account: %s     HoN Version: %s    Chat Port: %s    Protocol: %s" % (settings['username'], settings['honver'], settings['chatport'], settings['chatver']))
        if 'username' in settings:
            acc_config['username'] = settings['username']
            
        if 'password' in settings:
            acc_config['password'] = settings['password']
            
        if 'invis' in settings:
            settings['invis'] = True if settings['invis'] == "True" else False
            
        if 'chatport' in settings:
            settings['chatport'] = int(settings['chatport'])
            
        if 'chatver' in settings:
            settings['chatver'] = int(settings['chatver'])
            
        for key in settings:
            if key in basic_config:
                basic_config[key] = settings[key]
            
        self.client.configure(chatport=settings['chatport'], chatver=settings['chatver'], invis=settings['invis'],
                        masterserver=settings['masterserver'], basicserver=settings['basicserver'], honver=settings['honver'])

# def connectivity_test(url, port):
#   """ 
#   Since ICMP pings are blocked by the masterserver and chat server opening a basic socket 
#   connection is the best way to check their connectivity.
#   """

    def login_test(self):
        """ The aim of this test is to retrieve the cookie and auth has from the master server.
            First the master server should be checked for basic connectivity.
            A basic ping is likely not possible because the server would drop ICMP requests and can be seen
            in the results below.
            PING masterserver.hon.s2games.com (199.7.76.170) 56(84) bytes of data.

            --- masterserver.hon.s2games.com ping statistics ---
            3 packets transmitted, 0 received, 100% packet loss, time 2008ms
        """

        log.info("Testing login server...")
        status = ""
        note = ""

        try:
            response = self.client.login(acc_config['username'], acc_config['password'])
            status = "Up"
            note = "Login server is OK."
        except MasterServerError, e:
            status = "Down"
            note = e.error
        
        db.execute("""UPDATE servers SET status = %s, time = %s, note = %s WHERE id = 1 """, [1 if status == "Up" else 0, time.time(), note])
        return status, note

    def chat_test(self):
        log.info("Testing chat server...")
        status = ""
        note = ""

        if not self.client.is_logged_in():
            status = "Down"
            note = "Not logged in with an account. Is the login server down?"
        
        global down_count
        try:
            response = self.client.chat_connect()
            status = "Up"
            note = "Chat server is OK."
            down_count = 0
        except ChatServerError, e:
            status = "Down"
            note = e.error
            down_count += 1
        
        db.execute("""UPDATE servers SET status = %s, time = %s, note = %s WHERE id = 2 """, [1 if status == "Up" else 0, time.time(), note])
        return status, note

    def disconnect_logout(self):
        try:
            # TODO: Handle response from chat_disconnect
            if self.client.is_connected():
                log.info("Disconnecting from chat server")
                self.client.chat_disconnect()
            else:
                log.info("Not connected to the chat server")
        except ChatServerError, e:
            pass
        
        try:
            # TODO: Handle requester response for logging out
            if self.client.is_logged_in():
                log.info("Logging out")
                self.client.logout()
            else:
                log.info("Not logged in")
        except MasterServerError, e:
            if e.code == 106:
                log.error('Logout was forced, master server did receive the logout request.')


    def motd_parser(self):
        """ Retrieves the dictionary of message of the day(s(?)) 
            and replaces S2's colour formatting with html classes.
            Then places any new items into the database.
        """

        colour_map = ["00","1C","38","54","70","8C","A8","C4","E0","FF"]
        s2colours = lambda m: '<span style="color: #' + ''.join([colour_map[int(x)] for x in m.group(1)]) + '">'

        def urlfix(x):
            """ Replaces urls which only contain a 'www' with a 'http://wwww'. """
            if x.group(2) in ['http://', 'www']:
                colour = "y"
                url = x.group(1)
            else:
                colour = x.group(1)
                url = x.group(2)
            
            r = re.compile(r"(?<!http://)www")
            if r.match(url):
                url = 'http://' + ''.join(url)

            return '<a href=' + url + ' class=' + colour + ' target="_blank">' + url + '</a>'

        motd_list = self.client.motd_get()

        # Iterate over the list in reverse because entries are retrieved in order newest -> oldest
        # and must be entered into the database oldest -> newest.
        for motd in motd_list[::-1]:

            # First find any un-coloured hyperlinks and fill them with html tags.
            # This regex matches any hyperlink which is not preceeded by a ^g formatter for EG.
            # It is not very accurate at the moment as it will match a http which has a ^* at the end.
            # http://gskinner.com/RegExr/?2u79l
            r = re.compile(r"(?<=[^\^a-zA-Z])((http://|(?<!http://)www)[-a-zA-Z0-9@:%_\+.~#?&//=]+)[^\^\*]")
            motd['body'] = r.sub(urlfix, motd['body'])

            # Then find all hyperlinks that contain colour formatting and replace with HTML tags.
            r = re.compile(r"\^([a-zA-Z])((http://|(?<!http://)www)[-a-zA-Z0-9@:%_\+.~#?&//=]+)(\^\*)")
            motd['body'] = r.sub(urlfix, motd['body'])

            # Find all coded colours eg ^428 and replace with inline html styling
            # ''.join([color_map[int(x)] for x in r.search(msg).group(1)])
            r = re.compile(r"\^([0-9]{3})")
            motd['body'] = r.sub(s2colours, motd['body'])

            # Replace the colours with HTML classes
            # Replace ^* with </span>
            motd['body'] = motd['body'].replace("^*", "</span>")

            # Find all basic colour codes eg ^y or ^r or ^o and replace with inline html
            r = re.compile(r"\^([a-z]{1})")
            motd['body'] = r.sub(r"<span class='\1'>", motd['body'])

            # # Replace ^r with <span class="r"> - Red
            # motd['body'] = motd['body'].replace("^r", "<span class='r'>")

            # # Replace ^g with <span class="g"> - Green
            # motd['body'] = motd['body'].replace("^g", "<span class='g'>")

            # # Replace ^y with <span class="y"> - Yellow
            # motd['body'] = motd['body'].replace("^y", "<span class='y'>")

            # # Replace ^m with <span class="m"> - Magneta
            # motd['body'] = motd['body'].replace("^m", "<span class='m'>")

            # # Replace ^c with <span class="c"> - Cyan
            # motd['body'] = motd['body'].replace("^c", "<span class='c'>")

            # # Replace ^p with <span class="p"> - Pink
            # motd['body'] = motd['body'].replace("^p", "<span class='p'>")
            
            # Replace \r\n with <br />
            motd['body'] = motd['body'].replace("\r\n", "<br />")

            title_exists = db.query("""SELECT id FROM motds WHERE title = %s AND date = %s""", [motd['title'], motd['date']])
            msg_exists = db.query("""SELECT id, title FROM motds WHERE body = %s AND date = %s""", [motd['body'], motd['date']])

            if not title_exists:
                # Check if the message was simply updated by the staff.
                # If it's been changed then update it in the database automatically.
                # TODO: Is this level of comparison okay?
                if msg_exists:
                    # Title doesn't exist, but message body does, title changed.
                    db.execute("""UPDATE motds SET title=%s, author=%s, date=%s, body=%s WHERE id = %s""", [motd['title'], motd['author'], motd['date'], motd['body'], msg_exists[0][0]])
                    log.info("Updated motd #%s - %s. Title updated to %s" % (msg_exists[0][0], msg_exists[0][1], motd['title']))

            elif title_exists:
                log.debug("Duplicate title for motd id %s with title %s" % (title_exists[0][0], motd['title']))
                # This entry is already here, possibly it could have been updated.
                # Note: Seems they like to change the titles after publishing them.
                if not msg_exists:
                    # Title exists but the msg body doesn't, so it was likely updated.
                    db.execute("""UPDATE motds SET title=%s, author=%s, date=%s, body=%s WHERE id = %s""", [motd['title'], motd['author'], motd['date'], motd['body'], title_exists[0][0]])
                    log.info("Updated motd #%s - %s. Message updated" % (title_exists[0][0], motd['title']))

            if not msg_exists and not title_exists:
                    # Neither the title or message are there, either both are changed or this is a brand new motd
                    # Treat it as new for now.
                    # Add this motd to the database
                    db.execute("""INSERT INTO motds (title, author, date, body) VALUES(%s, %s, %s, %s)""", [motd['title'], motd['author'], motd['date'], motd['body']])
                    log.info("Added new message of the day - %s - %s" % (motd['title'], motd['date']))


def main():
    db.connect(config.dbhost, config.dbuser, config.dbpass, config.dbname)
    
    hon_monitor = HoNStatus()
    
    test_count = 1
    while True:
        try:
            log.info("Running test #" + str(test_count))
            
            hon_monitor.configure()
            
            login_status, login_reason = hon_monitor.login_test()
            log.info("Login server: " + login_status + " - " + login_reason)
            chat_status, chat_reason = hon_monitor.chat_test()
            log.info("Chat server:  " + chat_status + " - " + chat_reason)
            
            # Parse motd data each test
            try:
                hon_monitor.motd_parser()
            except MasterServerError, e:
                if e.code == 108:
                    log.error('Could not obtain motd data from the master server, not parsing.')

            if login_status == "Up" and chat_status == "Up" and hon_monitor.client.is_logged_in():
                # Keep the main thread busy until logged out.
                timer = 0
                while hon_monitor.client.is_connected():
                    timer += 1
                    if timer >= 300:
                        hon_monitor.disconnect_logout()
                    else:
                        time.sleep(1)

                # Client disconnected, let it cool down.
                time.sleep(2)
            else:
                # Start dropping the players online to zero once it's been determined that the servers are down.
                if down_count > 5:
                    db.execute("""INSERT INTO players (time, value) VALUES (%s, %s)""", [str(int(time.time())), 0])
                time.sleep(90)
        except ChatServerError, e:
            log.error("%s New test in 30 seconds." % e.error)
            hon_monitor.disconnect_logout()
            time.sleep(30)
        test_count += 1
    
class HSDaemon(Daemon):
    def run(self):
        print "Starting HoN monitor daemon"
        log.info("Starting up...")
        print "Monitor started %s" % pname
        log.info("Monitor started: %s" % pname)
        main()
    
    def stop(self):
        # Get the pid from the pidfile
        try:
            pf = file(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None
            
        if pid:
            print "Stopping HoN monitor daemon..."
            log.info("Stopping HoN monitor daemon...")
            super(HSDaemon, self).stop()
            print "Monitor stopped"
            log.info("Monitor stopped")
        else:
            print "pidfile %s does not exist. Is the daemon running?" % self.pidfile

#def sigint_handler(signum,  frame):
    #"""Handles SIGINT signal (<C-c>). Quits program."""
    #disconnect_logout()
    #log.info("Quitting...")
    #sys.exit(0)
    
if __name__ == "__main__":
    # Set up some global stuff.
    #signal.signal(signal.SIGINT, sigint_handler)
    log.add_logger('/var/python/HoNStatus/honstatus_mon.log', 'INFO', False)
    pname = "hon_monitor:%s:%s" % (uname()[1], getpid())
    setproctitle(pname)

    # Daemonise the program.
    daemon = HSDaemon('/tmp/hon_monitor:%s' % uname()[1])
    if len(sys.argv) == 2:
        if sys.argv[1] == 'start':
            daemon.start()
        elif sys.argv[1] == 'stop':
            daemon.stop()
        elif sys.argv[1] == 'restart':
            daemon.restart()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "Usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)
