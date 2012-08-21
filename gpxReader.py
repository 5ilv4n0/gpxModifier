#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xmltodict, json

with open('1.gpx','r') as f:
	buf = f.read()
	o = xmltodict.parse(buf)
	for e in o['gpx']['trk']['trkseg']['trkpt']:
		try:
			elevation = e['ele']
		except KeyError:
			e['ele'] = '0.0'
			
		print e
