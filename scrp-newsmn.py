#!/usr/bin/env python3

from datetime import date, timedelta

startDate = date(2011, 12, 1)
endDate = date(2011, 12, 31)


def main(startDate, endDate):
	for (url, title) in getUrls(startDate, endDate):
		print("%s: %s" % (url, title))

main(startDate, endDate)
