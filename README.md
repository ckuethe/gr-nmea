gr-nmea
=======

This module includes a couple of blocks to connect to either a NMEA0183 GPS or a gpsd instance (for shared receivers or non NMEA protocols. This can be used to inject position, velocity, and time information into flowgraphs or recordings.

Usage
-----
Instantiate an `nmea_gpsd` or `nmea_serial` block in your flowgraph. The raw NMEA output is available on the `out` port and can probably be safely discarded; asynchronous messages resulting from the parsing of the NMEA stream is available on the `gps_msg` port.

Both `nmea_gpsd.py` and `nmea_serial.py` can be run as standalone programs to demonstrate their functionality.

<img src="https://raw.githubusercontent.com/ckuethe/gr-nmea/master/examples/nmea_source_demo.grc.png"/></br>

Dependencies
------------
<a href="https://github.com/Knio/pynmea2" target="_blank">pynmea2</a> is required for NMEA0183 parsing

<a href="http://www.catb.org/gpsd/" target="_blank">gpsd</a> is useful for multiplexed device access, though not required for these modules