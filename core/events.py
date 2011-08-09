import time
from honcore import client, handler
import log, db

# Variable holding a count for how many times the total_online packet has been received.
# If it's a multiple of 3 then the total online is entered into the database.
# Used to throttle the data because there's simply too much at the moment.
total_online_count = 0

@handler.event_handler('all')
def on_event(packet_id, packet):
	""" Debug logging """
	log.debug("<< 0x%x " % packet_id)

@handler.event_handler('ping')
def on_ping():
	""" Logging..."""
	log.debug("Pong")

@handler.event_handler('total_online')
def on_total_online(players_online):
	"""Logs every fifth count into the database"""
	global total_online_count
	total_online_count += 1
	log.info(str(players_online) + " players online.")

	# Equates to every 2 minutes a value is saved to the database.
	if total_online_count % 3 is 0:
		curtime = str(int(time.time()))
		log.debug("Inserting into the database : %s players online at %s" % (players_online, curtime))
		db.execute("""INSERT INTO players (time, value) VALUES (%s, %s)""", [curtime, players_online])
