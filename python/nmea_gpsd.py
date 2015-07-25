#!/usr/bin/env python
# vim: tabstop=4:softtabstop=4:shiftwidth=4:noexpandtab:
# -*- coding: utf-8 -*-
#
# Copyright 2015 Chris Kuethe <chris.kuethe@gmail.com>
#
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
#

import numpy
import socket
import pmt
from nmea_parser_core import nmea_parser_core

from datetime import datetime as dt
from datetime import date as dtdate
from gnuradio import gr

class nmea_gpsd(gr.sync_block):
	"""NMEA source block, fed by a gpsd instance"""

	def __init__(self, host='localhost', port=2947):
		"""Set up network socket for NMEA streaming"""
		gr.sync_block.__init__(self, name="nmea_gpsd", in_sig=None, out_sig=[numpy.uint8])

		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.serial = self.sock.makefile('r')
		self.sock.connect((host, port))
		junk = self.serial.readline() # skip the daemon banner
		self.sock.send('?WATCH={"enable":true,"nmea":true ,"json":false }\n\n')
		junk = self.serial.readline() # skip devices line
		junk = self.serial.readline() # skip the "WATCH" line

		self.valid = False
		self.nmea_time = self.host_time = dt.fromtimestamp(0)
		self.message_port_register_out(pmt.intern('gps_msg'))

	def work(self, input_items, output_items):
		"""Stream NMEA data for processing"""
		outbuf = output_items[0]
		outstr = self.serial.readline().strip()
		self.host_time = dt.now()

		outlen = len(outstr)
		outbuf[:outlen] = numpy.fromstring(outstr, dtype=numpy.byte)

		try:
			nmea_parser_core(self, outstr)
		except Exception:
			pass

		# bytes written to output buffer, messages and tags computed
		# if possible. let's go on our merry way...
		return outlen

if __name__ == '__main__':
	print "main()"
	from optparse import OptionParser
	from gnuradio import blocks

	parser = OptionParser(usage="%prog: [options]")
	parser.add_option("-h", "--host", dest="host", type="string", default="localhost",
		help="Set gpsd host [default=%default]")
	parser.add_option("-p", "--port", dest="port", type="int", default=2947,
		help="Set gpsd port [default=%default]")
	parser.add_option("-r", "--raw", dest="raw", action="store_true", default=False,
		help="emit raw NMEA [default=%default]")
	(options, args) = parser.parse_args()

	# create flowgraph
	tb = gr.top_block()

	# GPS that drives this all...
	gps_source = nmea_gpsd(options.host, options.port)

	# Definitely want message output
	message_sink = blocks.message_debug()
	tb.msg_connect((gps_source, 'gps_msg'), (message_sink, 'print'))

	# Most of the time we'll just chuck out the raw nmea bytes
	null_sink = blocks.null_sink(gr.sizeof_char*1)
	tb.connect((gps_source, 0), (null_sink, 0))

	if options.raw:
		stdout_sink = blocks.file_sink(gr.sizeof_char*1, "/dev/stdout")
		tb.connect((gps_source, 0), (stdout_sink, 0))

	# Kick out the jams!
	tb.start()

	try:
		raw_input('Press Enter to quit: ')
	except KeyboardInterrupt:
		print "\n"
	except EOFError:
		print "\n"

	tb.stop()
	tb.wait()
