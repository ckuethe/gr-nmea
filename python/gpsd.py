#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=4:softtabstop=4:shiftwidth=4:noexpandtab:
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
import json
import socket
from gnuradio import gr
import pmt

class gpsd(gr.sync_block):
	"""
	docstring for block gpsd
	"""
	def __init__(self, host='localhost', port=2947):
		gr.sync_block.__init__(self,
			name="gpsd",
			in_sig=None,
			out_sig=[numpy.byte])

		self.sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM)
		self.fd = self.sock.makefile('rw')
		self.sock.connect((host, port))
		junk = self.fd.readline()
		self.sock.send('?WATCH={"enable":true,"json":true}\n\n')


	def work(self, input_items, output_items):
		out = output_items[0]
		try:
			buf = self.fd.readline()
			fixobj = json.loads(buf)
			buf += '\n'
			if fixobj['class'] == 'TPV':
				offset = self.nitems_written(0) # + idx
				self.add_item_tag(0, offset, pmt.string_to_symbol("latitude"), pmt.string_to_symbol(str(fixobj['lat'])))
				self.add_item_tag(0, offset, pmt.string_to_symbol("longitude"), pmt.string_to_symbol(str(fixobj['lon'])))
				self.add_item_tag(0, offset, pmt.string_to_symbol("altitude"), pmt.string_to_symbol(str(fixobj['alt'])))
				self.add_item_tag(0, offset, pmt.string_to_symbol("time"), pmt.string_to_symbol(str(fixobj['time'])))
			else:
				buf = ''
		except Exception as e:
			buf = ''

		l = len(buf)
		out[:l] = numpy.fromstring(buf, dtype=numpy.byte)
		return l
