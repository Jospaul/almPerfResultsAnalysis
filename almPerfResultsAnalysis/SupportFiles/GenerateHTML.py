#!/usr/bin/env python
# Author: Jospaul Mahajan Prakash
# Company: Infosys Limited
# The module handles generating the output as an HTML and sending to integrations.

import datetime
import requests
import SupportFiles.config as cnf
import logging


class generateHtml:

    def __init__(self, dataList):
        self.logger = logging.getLogger('rr.sf.generatehtml')
        self.dataList = dataList

    def createRow(self, resSize):
        tempDat = self.dataList['transactionsInTest']
        iter = 0
        allRows=''
        while iter < len(tempDat['transactionName']):
            if float(tempDat['avgResponseTime'][iter]) > float(cnf.transactions[tempDat['transactionName'][iter]]):
                row = "<tr><td>" + tempDat['transactionName'][iter] + "</td><td>" + \
                      str(cnf.transactions[tempDat['transactionName'][iter]]) + "</td><td bgcolor=#FF0000>" + \
                      str(tempDat['avgResponseTime'][iter]) + "</td><td>" + str(tempDat['95ResponseTime'][iter]) + \
                      "</td><td>" + str(tempDat['passVolume'][iter]).replace(",", "") + "</td><td>" + \
                      str(tempDat["failVolume"][iter]) + "</td></tr>"
                if float(tempDat['95ResponseTime'][iter]) > float(cnf.transactions[tempDat['transactionName'][iter]]):
                    row = "<tr><td>" + tempDat['transactionName'][iter] + "</td><td>" + \
                          str(cnf.transactions[tempDat['transactionName'][iter]]) + "</td><td bgcolor=#FF0000>" + \
                          str(tempDat['avgResponseTime'][iter]) + "</td><td bgcolor=#FF0000>" + \
                          str(tempDat['95ResponseTime'][iter]) + \
                          "</td><td>" + str(tempDat['passVolume'][iter]).replace(",", "") + "</td><td>" + \
                          str(tempDat["failVolume"][iter]) + "</td></tr>"
                slaRow = row
            elif float(tempDat['95ResponseTime'][iter]) > float(cnf.transactions[tempDat['transactionName'][iter]]):
                row = "<tr><td>" + tempDat['transactionName'][iter] + "</td><td>" + \
                      str(cnf.transactions[tempDat['transactionName'][iter]]) + "</td><td>" + \
                      str(tempDat['avgResponseTime'][iter]) + "</td><td bgcolor=#FF0000>" + \
                      str(tempDat['95ResponseTime'][iter]) + \
                      "</td><td>" + str(tempDat['passVolume'][iter]).replace(",", "") + "</td><td>" + \
                      str(tempDat["failVolume"][iter]) + "</td></tr>"
                slaRow = row
            else:
                row = "<tr><td>" + tempDat['transactionName'][iter] + "</td><td>" + \
                      str(cnf.transactions[tempDat['transactionName'][iter]]) + "</td><td>" + \
                      str(tempDat['avgResponseTime'][iter]) + "</td><td>" + \
                      str(tempDat['95ResponseTime'][iter]) + \
                      "</td><td>" + str(tempDat['passVolume'][iter]).replace(",", "") + "</td><td>" + \
                      str(tempDat["failVolume"][iter]) + "</td></tr>"
                slaRow = ''
            iter = iter + 1
            if resSize:
                allRows = allRows + row
            else:
                allRows = allRows + slaRow
        return allRows

    def createHtml(self):
        html = ''
        if cnf.teamsResult.lower() == "long":
            html = "<html><table style=\\\"width:50%\\\"><tr><th>Test Duration:</th><td>" + \
                    self.dataList['duration'].split(": ")[1] + "</td></tr><tr><th>Average Hits Per Sec:</th><td>" + \
                    self.dataList['hitsPerSec'] + "</td></tr><tr><th>Average Transactions Per Sec:</th><td>" + \
                    self.dataList['transactionsPerSec'] + "</td></tr><tr><th>Average HTTP 200s Per Sec:</th><td>" + \
                    self.dataList['http200PerSec'] + "</td></tr></tr><tr><th>Transaction Name</th><th>SLA</th><th>" \
                    "Average Response Time</th><th>95th Percentile</th><th>Pass Count</th><th>Fail Count</th></tr>" +\
                    self.createRow(True) + "</table></html>"
        elif cnf.teamsResult.lower() == "short":
            html = "<html><table style=\\\"width:50%\\\"><tr><th>Test Duration:</th><td>" + \
                   self.dataList['duration'].split(": ")[1] + "</td></tr><tr><th>Average Hits Per Sec:</th><td>" + \
                   self.dataList['hitsPerSec'] + "</td></tr><tr><th>Average Transactions Per Sec:</th><td>" + \
                   self.dataList['transactionsPerSec'] + "</td></tr><tr><th>Average HTTP 200s Per Sec:</th><td>" + \
                   self.dataList['http200PerSec'] + "</td></tr></tr><tr><th>Transaction Name</th><th>SLA</th><th>" \
                                                    "Average Response Time</th><th>95th Percentile</th><th>Pass Count</th><th>Fail Count</th></tr>" + \
                   self.createRow(False) + "</table></html>"

        return html

    def postTeams(self):
        if self.dataList['http200PerSec']:
            html = self.createHtml()
            teamsLink = cnf.teamsUrl
            resultstopost = {"title": cnf.project + " Results - " + str(datetime.date.today()), "text": html}

            try:
                sess = requests.session()
                resp = sess.post(teamsLink, data=str(resultstopost), headers={'Content-type': 'text/json'})
                if resp.ok:
                    self.logger.info("Successfully posted results to teams")
                else:
                    self.logger.error("Unable to post results to team. Please check the url to teams "
                                      "channel in configuration file.")
            except IOError:
                self.logger.error("Unable to connect to teams channel")
        else:
            html = "<html><H1 style=\"color:red;\">Test Failed, Check ALM Results</H1></html>"
            teamsLink = cnf.teamsUrl
            resultstopost = {"title": cnf.project + " Results - " + str(datetime.date.today()), "text": html}

            try:
                sess = requests.session()
                resp = sess.post(teamsLink, data=str(resultstopost), headers={'Content-type': 'text/json'})
                if resp.ok:
                    self.logger.info("Successfully posted results to teams")
                else:
                    self.logger.error("Unable to post results to team. Please check the url to teams "
                                      "channel in configuration file.")
            except IOError:
                self.logger.error("Unable to connect to teams channel")

    def postQuickTeams(self, html):
        teamsLink = cnf.teamsUrl
        resultstopost = {"title": cnf.project + " Results - " + str(datetime.date.today()), "text": html}

        try:
            sess = requests.session()
            resp = sess.post(teamsLink, data=str(resultstopost), headers={'Content-type': 'text/json'})
            if resp.ok:
                self.logger.info("Successfully posted results to teams")
            else:
                self.logger.error("Unable to post results to team. Please check the url to teams "
                                  "channel in configuration file.")
        except IOError:
            self.logger.error("Unable to connect to teams channel")
