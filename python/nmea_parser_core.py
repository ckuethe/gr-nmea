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

import pynmea2
import pmt

from pmt import string_to_symbol as PSTR
from pmt import from_double as PDBL
from pmt import dict_add as PMT_ADD

from datetime import datetime as dt
from datetime import date as dtdate

def nmea_parser_core(self, nmea_str):
	fixobj = pynmea2.parse(nmea_str)
	nmea_id = fixobj.sentence_type

	if nmea_id not in ['GGA', 'GLL', 'RMC', 'VTG']:
		raise AttributeError("Unparsed Sentence")

	D = pmt.make_dict()
	D = PMT_ADD(D, PSTR("id"), PSTR(nmea_id))
	D = PMT_ADD(D, PSTR("host_time"), PSTR(str(self.host_time)))

	try:
		self.valid = fixobj.is_valid
		D = PMT_ADD(D, PSTR("valid"), pmt.from_bool(self.valid))
	except AttributeError:
		pass # not all sentences carry validity

	try:
		D = PMT_ADD(D, PSTR("latitude"), PDBL(fixobj.latitude))
		D = PMT_ADD(D, PSTR("longitude"), PDBL(fixobj.longitude))
	except AttributeError:
		pass

	try:
		if fixobj.altitude is not None:
			D = PMT_ADD(D, PSTR("altitude"), PDBL(fixobj.altitude))
	except AttributeError:
		pass

	try:
		D = PMT_ADD(D, PSTR("true_track"), PDBL(fixobj.true_track))
	except AttributeError:
		pass

	try:
		if fixobj.spd_over_grnd_kmph is not None:
			D = PMT_ADD(D, PSTR("speed_kmh"), PDBL(fixobj.spd_over_grnd_kmph))
	except AttributeError:
		pass

	try:
		self.nmea_time = dt.combine(fixobj.datestamp, fixobj.timestamp)
		D = PMT_ADD(D, PSTR("nmea_time"), PSTR(str(self.nmea_time)))
	except AttributeError:
		pass

	# Send the message
	if D:
		self.message_port_pub(pmt.intern('gps_msg'), pmt.cons(D, pmt.PMT_NIL))
	'''
	except pynmea2.nmea.ParseError:
		# nmea parse failure is forseeable, but is deemed to not be fatal
		pass
	except AttributeError:
		pass
	'''
