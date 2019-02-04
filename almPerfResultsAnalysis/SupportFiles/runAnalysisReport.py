#!/usr/bin/env python
# Author: Jospaul Mahajan Prakash
# Company: Infosys Limited
# The module encapsulates the functions written in all the other modules. This module primarily acts as the
# presentation layer. Generation of results and writing to the specified outputs and other operations required to
# achieve them are written in this module.

import SupportFiles.config as cnf
from SupportFiles.ALMOperations import almOperations
import logging
from SupportFiles.ProcessHTML import processHtml
import sys
from datetime import datetime
from SupportFiles.GenerateHTML import generateHtml
from threading import Thread


# Global Variable:
lrAnalyze = {'almUrl': '', 'domain': '', 'project': '','userName': '', 'password': '',
             'scanarioName': '', 'scenarioId': 0, 'outputLoc': '', 'runId': ''}
logger = logging.getLogger('rr.sf.runAnalysisReport')
# Input Arguments: argv
# Output Arguments: opts
# Function: Captures all the inputs that are provided through command line.
def processSysArgs(argv):
    opts = {}
    while argv:
        if argv[0][0] == '-':
            opts[argv[0]] = argv[1]
        argv = argv[1:]
    return opts


# Input Arguments: None
# Output Argument: None
# Function: Primary function that gets called by main that fetches the results and creates a
#           csv or output to teams or both.
def createLrAnalyzeReport():
    cnf.fetchfromconfig()
    lrAnalyze['almUrl'] = cnf.almUrl
    lrAnalyze['scenarioName'] = cnf.scenarioName
    lrAnalyze['scenarioId'] = cnf.scenarioId
    lrAnalyze['domain'] = cnf.domain
    lrAnalyze['project'] = cnf.project
    opts = processSysArgs(sys.argv)
    lrAnalyze['userName'] = opts['-u']
    lrAnalyze['password'] = opts['-p']
    lrAnalyze['outputLoc'] = opts['-o']
    execRun = False
    if '-r' in opts.keys():
        lrAnalyze['runId'] = opts['-r']
        execRun = True

    try:
        almObj = almOperations(lrAnalyze['almUrl'], lrAnalyze['userName'], lrAnalyze['password'], lrAnalyze['domain'],
                               lrAnalyze['project'])
        almSession = almObj.almLogin()
        almSession.almSession()

        if not lrAnalyze['scenarioId']:
            lrAnalyze['scenarioId'] = almSession.findTestIdByName(lrAnalyze['scanarioName'])
            logger.debug("Scenario Name not provided in the configuration")
        elif not lrAnalyze['scenarioName']:
            lrAnalyze['scenarioName'] = almSession.findTestNameById(lrAnalyze['scenarioId'])
            logger.debug("Scenario Id not provided in the configuration")
        elif not lrAnalyze['scenarioId'] and not lrAnalyze['scenarioName']:
            if not execRun:
                lrAnalyze['scenarioId'] = almSession.findTestIdByRunId(lrAnalyze['runId'])
                lrAnalyze['scenarioName'] = almSession.findTestNameById(lrAnalyze['scenarioId'])
                logger.debug("Scenario Name or Id should be provided in the ")
            else:
                logger.error("Scenario Name, scenario Id and run Id cannot be empty.")
                logger.error("Kindly add scenario name or id to the configuration or include the run id.")
                sys.exit(1)

        reportId=''
        if not execRun:
            almSession.almSession()
            lrAnalyze['runId'] = str(almSession.fetchLatestRunByTestId(str(lrAnalyze['scenarioId'])))
            if lrAnalyze['runId']:
                logger.debug("The run Id was successfully fetched. RunID: " + lrAnalyze['runId'])
                reportId = almSession.fetchReportIdByRunId(lrAnalyze['runId'])
                logger.debug("The report Id was successfully fetched. ReportID: " + reportId)
            else:
                logger.error("There is no recent runs in the last 30 days. Exiting.")
                html = "<html><H1 style=\"color:red;\">No tests in the past 30 days</H1></html>"
                htmObj = generateHtml({})
                htmObj.postQuickTeams(html)
                sys.exit(1)
        else:
            almSession.almSession()
            reportId = almSession.fetchReportIdByRunId(lrAnalyze['runId'])
            logger.debug("The report Id was successfully fetched. ReportID: " + reportId)

        analysisSummaryReport = almSession.fetchReportHtml(reportId, cnf.tempLoc)
        logger.debug("Fetched the summary report successfully.")
        contentHtml = processHtml(almSession.fetchHtmlFile(cnf.tempLoc, reportId, "contents.html"))
        if not contentHtml:
            logger.debug("Transactions report was found and file name fetched.")
            analysisTransactionReport = almSession.fetchHtmlFile(cnf.tempLoc, reportId,
                                                             contentHtml.fetchFileName('Total Transactions per Second'))
            logger.debug("Fetched the transaction report successfully.")
            logger.info("Html content of the summary report and transaction report is fetched.")
            reportData = compileResults(analysisSummaryReport, analysisTransactionReport)
            if lrAnalyze['outputLoc'] == "file":
                createResultFile(reportData)
            elif lrAnalyze['outputLoc'] == "teams":
                htmObj = generateHtml(reportData)
                htmObj.postTeams()
            elif lrAnalyze['outputLoc'] == "tf":
                Thread(target=createResultFile(reportData)).start()
                Thread(target=trigHtml(reportData)).start()
        else:
            logger.error('Transactions Report was not found. Please check the results.')
            sys.exit(1)

    except IOError:
        logger.error('Error in connection.' + IOError)
    except IndexError:
        logger.error('Error occurred while reading command line arguments.')
        logger.error('The following arguments are mandatory -\n'
                     '-u <almusername> -p <almpassword> -o (f)ile/(t)eams')
        logger.error('Please also check if the html report is available for the latest test.')

        sys.exit(1)
    except ValueError:
        logger.error('The command line arguments are not in the right format')
        logger.error('The following arguments are mandatory -\n'
                     '-u <string> -p <string> -o file/teams')
        sys.exit(1)
    except AttributeError:
        logger.error('The command line arguments are not in the right type')
        logger.error('The following arguments are mandatory -\n'
                     '-u <string> -p <string> -o file/teams')
        sys.exit(1)


# Input Arguments: reportData
# Output Arguments: None
# Function: Makes the call to generate the output to teams.
def trigHtml(reportData):
    htmObj = generateHtml(reportData)
    htmObj.postTeams()


# Input Arguments: summaryHtml, transactionHtml
# Output Arguments: None
# Function: Orchestrates the processing of the data in the html report
def compileResults(summaryHtml, transactionHtml):
    durationOfTest = ''
    hitsPerSec = ''
    http200PerSec = ''
    transactionsInTest = ''
    transactionsPerSec = ''
    try:
        procObj = processHtml(summaryHtml)
        durationOfTest = procObj.durationOfTest()
        hitsPerSec = procObj.hitsPerSecInTest()
        http200PerSec = procObj.http200InTest()
        transactionsInTest = procObj.transactionsInTest()
        procObj = processHtml(transactionHtml)
        transactionsPerSec = procObj.transactionPerSec()
        return {'duration': durationOfTest, 'hitsPerSec': hitsPerSec, 'http200PerSec': http200PerSec,
                'transactionsInTest': transactionsInTest, 'transactionsPerSec': transactionsPerSec}
    except ValueError:
        logger.error('The Test Failed. Check the results for failure.')
    except AttributeError:
        logger.error('The Test Failed. Check the results for failure.')
    finally:
        return {'duration': durationOfTest, 'hitsPerSec': hitsPerSec, 'http200PerSec': http200PerSec,
                'transactionsInTest': transactionsInTest, 'transactionsPerSec': transactionsPerSec}


# Input Arguments: reportData
# Output Arguments: None
# Function: Takes in the dictionary containing the processed results and writes the contents to the output csv file.
def createResultFile(reportData):
    fileName = 'outResult_' + lrAnalyze['scenarioName'] + '_' + datetime.today().strftime('%Y_%m_%dT%H%M%S') +'.csv'
    try:
        csvFile = open(cnf.fileLoc + '\\' + fileName, 'a')
        logger.debug('Successfully created and opened the output file to write results.')
        if reportData['http200PerSec']:
            csvFile.write("Test Duration:," + reportData['duration'].split(": ")[1] + '\n')
            csvFile.write("Average Hits Per Sec:," + reportData['hitsPerSec'] + '\n')
            csvFile.write("Average Transactions Per Sec:," + reportData['transactionsPerSec'].replace("\n", "") + '\n')
            csvFile.write("Average HTTP 200s Per Sec:," + reportData['http200PerSec'] + '\n')
            csvFile.write("\n\n")
            csvFile.write("Transaction Name," + "SLA," + "Average Response Time," + "95th Percentile," + "Pass Count,"
                          + "Fail Count" + "\n")
            tempDat = reportData['transactionsInTest']
            iter = 0
            while iter < len(tempDat['transactionName']):
                csvFile.write(tempDat['transactionName'][iter] + "," +
                              str(cnf.transactions[tempDat['transactionName'][iter]]) +
                              "," + str(tempDat['avgResponseTime'][iter]) + "," +
                              str(tempDat['95ResponseTime'][iter]) + "," +
                              str(tempDat['passVolume'][iter]).replace(",", "") + "," +
                              str(tempDat["failVolume"][iter]) + "\n")
                iter = iter + 1
        else:
            csvFile.write("Test Duration:," + reportData['duration'].split(": ")[1] + '\n')
            csvFile.write("Test Failed, Check ALM Results")
        logger.info("Successfully completed writing the results to the output file.")

    except IOError:
        logger.error('An error occurred in writing the report to the csv.')
        sys.exit(1)
