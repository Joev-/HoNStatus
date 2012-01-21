import time
import log, db

# Variable holding a count for how many times the total_online packet has been received.
# If it's a multiple of 3 then the total online is entered into the database.
# Used to throttle the data because there's simply too much at the moment.
total_online_count = 2

def on_event(packet_id, packet):
    """ Debug logging """
    #log.debug("<< 0x%x " % packet_id)

def on_ping():
    """ Logging..."""
    #log.debug("Pong")

def on_total_online(count, region_data):
    """
    Logs every third count into the database.
    """
    global total_online_count
    total_online_count += 1
    #log.debug("%s players online. - %s" % (count, region_data))

    # Equates to every 2 minutes a value is saved to the database.
    if total_online_count == 3:
        total_online_count = 0
        curtime = str(int(time.time()))
        #log.debug("Inserting into the database : %s players online at %s" % (count, curtime))
        db.execute("""INSERT INTO players (time, value) VALUES (%s, %s)""", [curtime, count])
