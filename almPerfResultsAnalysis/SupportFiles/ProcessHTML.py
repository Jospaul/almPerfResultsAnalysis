#!/usr/bin/env python
# Author: Jospaul Mahajan Prakash
# Company: Infosys Limited
# Module handles all parsing of the report html file and collecting the transaction information from the report.

from bs4 import BeautifulSoup
import logging
from functools import reduce



class processHtml:

    def __init__(self, extractedHtml):
        self.extractedHtml = extractedHtml
        self.logger = logging.getLogger('rr.sf.processhtml')

    # Input Arguments: Object (processHtml)
    # Output Arguments: parsedHtml
    # Function: Reads the string data and parses it as a html
    def parseHtml(self):
        parsedHtml = BeautifulSoup(self.extractedHtml, "html.parser")
        if not parsedHtml:
            self.logger.error('Unable to parse html received. Please check report format.')
        else:
            self.logger.debug('Successfully parsed the html report.')
        return parsedHtml

    # Input Arguments: Object (processHtml)
    # Output Arguments: duration
    # Function: Fetch the duration of the test run.
    def durationOfTest(self):
        parsedHtml = self.parseHtml()
        return parsedHtml.find(class_="header_timerange").string

    # Input Arguments: Object (processHtml)
    # Output Arguments: hits per sec
    # Function: Fetch the hits per sec of the test run.
    def hitsPerSecInTest(self):
        parsedHtml = self.parseHtml()
        return parsedHtml.find(headers="LraAverageHitsPerSecond").string

    # Input Arguments: Object (processHtml)
    # Output Arguments: http 200 per sec
    # Function: Fetch the http 200 per sec of the test run.
    def http200InTest(self):
        parsedHtml = self.parseHtml()
        return parsedHtml.find(headers="LraPer second").span.string

    # Input Arguments: Object (processHtml)
    # Output Arguments: dictionary with response time details.
    # Function: Fetch the response time and volume data for transactions.
    def transactionsInTest(self):
        parsedHtml = self.parseHtml()
        res = {}
        temp = parsedHtml.findAll(headers="LraTransaction Name")
        res['transactionName'] = [i.span.string for i in temp]
        temp = parsedHtml.findAll(headers="LraAverage")
        res['avgResponseTime'] = [i.span.string for i in temp]
        temp = parsedHtml.findAll(headers="Lra95 Percent")
        res['95ResponseTime'] = [i.span.string for i in temp]
        temp = parsedHtml.findAll(headers="LraPass")
        res['passVolume'] = [i.span.string for i in temp]
        temp = parsedHtml.findAll(headers="LraFail")
        res['failVolume'] = [i.span.string for i in temp]
        return res

    # Input Arguments: Object (processHtml)
    # Output Arguments: transactions per sec
    # Function: Fetch the transactions per sec of the test run.
    def transactionPerSec(self):
        parsedHtml = self.parseHtml()
        temp = parsedHtml.find(class_="legendTable").findAll(class_="legendRow")
        return temp[1].findAll('td')[4].string

    # Input Arguments: String ( Report name to find)
    # Output Arguments: Name of the file containing the Report data.
    # Function: Fetch the file name of the report based on the name from contents in Summary report
    def fetchFileName(self, ReportName):
        parsedHtml = self.parseHtml()
        links = parsedHtml.findAll('a')
        fetchHref = lambda self, htmlTag: htmlTag if ReportName in str(htmlTag) else '<a>No Value</a>'
        fileSoup = reduce(fetchHref, links)
        return fileSoup['href']

