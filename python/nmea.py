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
import serial
import pynmea2
import datetime
import time
from gnuradio import gr
import pmt

class nmea(gr.sync_block):
	'''
	Simple NMEA to gnuradio async message converter. Doesn't do most of
	the fancy stuff that gpsd does, but it's pretty lightweight.
	'''
	def __init__(self, device='/dev/ttyUSB0', speed=4800):
		gr.sync_block.__init__(self,
			name="nmea",
			in_sig=None,
			out_sig=[numpy.byte])

		"""Initialize module by opening GPS and setting some state"""
		self.valid = False
		self.last_time = datetime.datetime.fromtimestamp(0)
		self.sys_time = 0
		self.device = device
		self.speed = speed
		self.serial = serial.Serial(self.device, self.speed, timeout=1) # XXX other serial options?


	def work(self, input_items, output_items):
		out = output_items[0]
		try:
			self.line = self.serial.readline()
			msg = pynmea2.parse(self.line)
			mtype = msg.sentence_type

			if mtype == 'ZDA':
				'''
				Some receivers start their report block with '$' in $GPZDA
				aligned to the top of the second; let's try parse it first
				'''
				curr_time = datetime.datetime.combine(datetime.date(msg.year, msg.month,msg.day), msg.timestamp)
				if curr_time > self.last_time:
					self.sys_time = time.gmtime()
					self.last_time = curr_time

			elif mtype == 'RMC':
				'''
				RMC contains at least latitude, longitude, and timestamp.
				It also contains a validity flag, but my stupid USB GPS
				sets the valid flag even indoors with no fix. Thus, not
				using this sentence to determine fix validity.
				'''
				curr_time = datetime.datetime.combine(msg.datestamp, msg.timestamp)
				if curr_time > self.last_time:
					self.sys_time = time.gmtime()
					self.last_time = curr_time
				#print "> %s %s %.4f %.4f %s\n" % (msg.datestamp, msg.timestamp, msg.latitude, msg.longitude, valid)

			elif mtype == 'GSA':
				'''
				Use either the fix mode or fix quality (nofix,2d,3d)
				to set validity
				'''
				v = True if msg.mode in [2, 3] else False;
				if v != self.valid:
					self.valid = v

			elif mtype == 'GGA':
				v = True if msg.gps_qual in [1, 2] else False;
				if v != self.valid:
					self.valid = v
			else:
				pass

			#idx = 0
			offset = self.nitems_written(0) # + idx
			k_msg = pmt.string_to_symbol("sentence")
			v_msg = pmt.string_to_symbol(mtype)
			self.add_item_tag(0, offset, k_msg, v_msg)
			k_time = pmt.string_to_symbol("sentence")
			v_time = pmt.string_to_symbol(mtype)
			self.add_item_tag(0, offset, k_time, v_time)

			s = str(msg) + '\n'
			l = len(s)
			out[:l] =  numpy.fromstring(s, dtype=numpy.byte)
			return l

		except pynmea2.nmea.ParseError:
			# there are a few non-exceptional reasons that a sentence
			# may fail to parse. pretent like nothing happened.
			return 0
"""
class gr_gps_demo(gr.top_block):
	def __init__(self, device="/dev/ttyUSB0", speed=4800):
		gr.top_block.__init__(self, "demonstrating the use of gr_gps")
		self.device = device
		self.speed = speed

		# Blocks
		self.gps_block = gr_gps(self.device, self.speed)
		self.stdout_sink = blocks.file_sink(gr.sizeof_char*1, "/dev/stdout")

		# Connections
		self.connect((self.gps_block, 0), (self.stdout_sink, 0)) 

if __name__ == '__main__':
	parser = OptionParser(usage="%prog: [options]")
	parser.add_option("-d", "--device", dest="device", type="string", default="/dev/ttyUSB0",
		help="Set filename [default=%default]")
	parser.add_option("-s", "--speed", dest="speed", type="int", default="4800",
		help="Set tty speed [default=%default]")
	(options, args) = parser.parse_args()
	tb = gr_gps_demo(device=options.device, speed=options.speed)

	tb.start()
	try:
		raw_input('Press Enter to quit: ')
	except EOFError:
		pass
 
	tb.stop()
	tb.wait()
"""
