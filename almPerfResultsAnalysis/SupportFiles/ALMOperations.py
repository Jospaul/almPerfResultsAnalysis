#!/usr/bin/env python
# Author: Jospaul Mahajan Prakash
# Company: Infosys Limited
# Module handles all the integration with ALM, from logging in to fetching the html reports.

import json
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
from datetime import timedelta
import logging
import sys
import zipfile
import io
import os, shutil


class almOperations:
    almUrl = ""
    userName = ""
    pword = ""

    def __init__(self, almUrl, userName, pword, domain, project):
        self.logger = logging.getLogger('rr.sf.almoperation')
        self.almUrl = almUrl
        self.userName = userName
        self.pword = pword
        self.domain = domain
        self.project = project
        self.almSess = requests.session()
        self.logger.debug('Instance of almOperations created!')

    # Input Arguments: Object (almOperations)
    # Output Arguments: Object (almOperations)
    # Function: Initiate a connection to alm and login. Update the incoming object with the session information.
    def almLogin(self):
        almConn = requests.session()
        almResp = almConn.post(self.almUrl + '/authentication-point/authenticate',
                               auth=HTTPBasicAuth(self.userName, self.pword))
        if almResp.ok:
            self.almSess = almConn
            self.logger.info('Successfully logged in to ALM.')
            self.logger.debug('Session stored in object instance.')
        else:
            self.logger.error('ALM login failed, check credentials for user - ' + self.userName)
            sys.exit(1)
        return self

    # Input Arguments: Object (almOperations)
    # Output Arguments: Object (almOperations)
    # Function: Check whether the session is active.
    def almSession(self):
        almResp = self.almSess.post(self.almUrl + '/rest/site-session')
        if almResp.ok:
            self.logger.info('ALM Session successfully verified.')
        else:
            self.logger.error('ALM Session expired.')
        return self

    # Input Arguments: Object (almOperations)
    # Output Arguments: Object (almOperations)
    # Function: Fetches the project list of ALM. For future use.
    def almFetchProjects(self):
        almConn = self.almSess.get(self.almUrl + '/rest/domains/' + self.domain +
                                   '/projects', headers={'Accept': 'application/json'})
        if almConn.ok:
            self.logger.debug('Fetched ALM projects successfully.')
        else:
            self.logger.debug('ALM projects were not fetched successfully. Request returned a status '
                              + str(almConn.status_code))
        return self

    # Input Arguments: Object (almOperations), almProject
    # Output Arguments: Object (almOperations)
    # Function: Fetches all the execution runs of a project. For future use.
    def almFetchRuns(self):
        almConn = self.almSess.get(self.almUrl + '/rest/domains/' + self.domain +
                                   '/projects/' + self.project + '/runs',
                                   headers={'Accept': 'application/json'})
        if almConn.ok:
            self.logger.debug('Test Runs under the project ' + self.project + ' successfully retrieved.')
        else:
            self.logger.debug('Test Runs under the project ' + self.project + ' was not fetched. '
                                'The request failed with status code ' + str(almConn.status_code))
        return self

    # Input Arguments: runId, reportName
    # Output Arguments: reportId
    # Function: Fetch the report Id in ALM for the Report.html.
    def fetchReportIdByRunId(self, runId, reportName='Reports'):
        self.almSession()
        resp = self.almSess.get(self.almUrl + '/rest/domains/' + self.domain + '/projects/' + self.project +
                                '/results?query={run-id[' + runId + '];name[\'' + reportName +
                                '\']}&fields=id,run-id,name', headers={'Accept': 'application/json'})
        reportId = ''
        if resp.ok:
            self.logger.debug("Successfully fetched the report id")
            parsedResp = json.loads(resp.text)
            reportId = parsedResp["entities"][0]["Fields"][0]["values"][0]["value"]
        else:
            self.logger.debug("Unable to fetch the report id for the specified run id. Please check the run id " +
                              runId)
        return reportId

    # Input Arguments: reportId
    # Output Arguments: html
    # Function: Fetch the report zip from ALM, extract the zip and fetch the html report.
    def fetchReportHtml(self, reportId, tempdir):
        self.almSession()
        resp = self.almSess.get(self.almUrl + '/rest/domains/' + self.domain + '/projects/' + self.project +
                                '/results/' + reportId + '/logical-storage/',
                                headers={'Content-Type': 'text/html'},
                                stream=True)
        self.delFilesTemp(tempdir)

        if resp.ok:
            self.logger.debug("Successfully extracted the zip file from ALM.")
            zipF = zipfile.ZipFile(io.BytesIO(resp.content))
            zipF.extractall(tempdir)
            self.logger.info("The Report.html is unzipped and placed in the location " + tempdir)
        else:
            self.logger.debug("Return Code:" + str(resp.status_code) + " .Return Text:" + resp.text)
            self.logger.error("The report was not fetched successfully.")

        return self.fetchHtmlFile(tempdir, reportId)

    # Input Arguments: filename, location, reportId
    # Output Arguments: html file
    # Function: Fetch the html file from the folder location
    def fetchHtmlFile(self, filePath, reportId, htmlName="summary.html"):
        htmlFile = open(filePath + '\\result\\' +
                        reportId + '\\Report\\' + htmlName, mode='r')

        html = htmlFile.read()

        htmlFile.close()
        return html

    # Input Arguments: filepath
    # Output Arguments: None
    # Function: Cleanup files in the shared temp folder from previous execution
    def delFilesTemp(self, filePath):
        for thefile in os.listdir(filePath):
            fp = os.path.join(filePath, thefile)
            try:
                if os.path.isfile(fp):
                    os.unlink(fp)
                elif os.path.isdir(fp):
                    shutil.rmtree(fp)
                self.logger.debug("Successfully deleted the files in the temp folder " + filePath)
            except Exception as e:
                self.logger.error("An exception has occurred - \n" + e)

    # Input Arguments: testId
    # Output Arguments: runId
    # Function: Fetch the latest run of a particular test id.
    def fetchLatestRunByTestId(self, testId):
        self.almSession()
        resp = self.almSess.get(self.almUrl + '/rest/domains/' + self.domain + '/projects/' + self.project +
                                '/runs?query={test-id[' + testId +'];state["Finished"]}&'
                                                                  'fields=execution-date,pc-end-time,id,state' +
                                                                  '&order-by={execution-date[DESC];pc-end-time[DESC]}',
                                headers={'Accept': 'application/json'})
        runs = {}
        if resp.ok:
            self.logger.info('Successfully fetched all runs of the test id ' + testId)
            parsedJson = json.loads(resp.text)
            totalIter = parsedJson["TotalResults"]
            iter = 0
            while iter < totalIter:
                fetchDateOfRun = parsedJson["entities"][iter]["Fields"][1]["values"][0]["value"]
                fetchTimeOfRunCompletion = parsedJson["entities"][iter]["Fields"][3]["values"][0]["value"]
                runId = parsedJson["entities"][iter]["Fields"][0]["values"][0]["value"]
                runs[runId] = [fetchDateOfRun, fetchTimeOfRunCompletion]
                iter = iter + 1
            self.logger.debug('Successfully fetched all runs for the test id ' + testId)
        else:
            self.logger.error('Unable to fetch the details of the test run of test id ' + testId +
                              '. Please check the connection. The request failed with ' + str(resp.status_code))
        return self.findLatestRunFromDictionary(runs)

    # Input Arguments: {run dictionary}
    # Output Arguments: runId
    # Function: Scan through the runs captured in the dictionary and return the latest run id.
    def findLatestRunFromDictionary(self, testRuns):
        todaysDate = datetime.today()
        self.logger.debug('Todays date is ' + str(todaysDate))
        thirtydaysbefore = todaysDate + timedelta(days=-30)
        self.logger.debug('Date 30 days ago is ' + str(thirtydaysbefore))
        temp = todaysDate - thirtydaysbefore
        runId = ''
        self.logger.debug('Start fetching the latest run id from the list of test runs.')
        for key in testRuns.keys():
            diffDate = todaysDate - datetime.strptime(testRuns[key][1], '%Y-%m-%d %H:%M:%S')
            if temp > diffDate:
                temp = diffDate
                runId = key
        self.logger.info('Latest test run is fetched and the run Id is ' + runId)
        return runId

    # Input Arguments: scenarioName
    # Output Arguments: testId
    # Function: Identify the testId based on the scenarioName
    def findTestIdByName(self, scenarioName):
        self.almSession()
        resp = self.almSess.get(self.almUrl + '/rest/domains/' + self.domain + '/projects/' + self.project +
                                '/tests?query={name[\'' + scenarioName + '\']}&fields=name,id',
                                headers={'Accept': 'application/json'})
        testId=''
        if resp.ok:
            self.logger.info('Successfully identified test(s) with the given scenario - ' + scenarioName)
            parsedResp = json.loads(resp.text)
            totalResults = parsedResp["TotalResults"]
            if int(totalResults) > 1:
                self.logger.error('There are more than 1 scenarios with the given ' + scenarioName)
                sys.exit(1)
            else:
                self.logger.info('Successfully fetched the scenario Id')
                testId = parsedResp["entities"][0]["Fields"][0]["values"][0]["value"]
        return testId

    # Input Arguments: scenarioId
    # Output Arguments: scenarioName
    # Function: Identify the testId based on the scenarioName
    def findTestNameById(self, scenarioId):
        self.almSession()
        resp = self.almSess.get(self.almUrl + '/rest/domains/' + self.domain + '/projects/' + self.project +
                                '/tests?query={id[' + str(scenarioId) + ']}&fields=name,id',
                                headers={'Accept': 'application/json'})
        scenarioName=''
        if resp.ok:
            self.logger.info('Successfully identified test(s) with the given scenario - ' + str(scenarioId))
            parsedResp = json.loads(resp.text)
            self.logger.info('Successfully fetched the scenario Name')
            scenarioName = parsedResp["entities"][0]["Fields"][1]["values"][0]["value"]
        return scenarioName

    # Input Arguments: runId
    # Output Arguments: scenarioId
    # Function: Identify the testId based on the runId
    def findTestIdByRunId(self,runId):
        self.almSession()
        resp = self.almSess.get(self.almUrl + '/rest/domains/' + self.domain + '/projects/' + self.project +
                                '/runs?query={id[' + runId + '];state["Finished"]}&filters=test-id',
                                headers={'Accept': 'application/json'})
        scenarioId=''
        if resp.ok:
            self.logger.info('Successfully identified test(s) with the given scenario - ' + runId)
            parsedResp = json.loads(resp.text)
            self.logger.info('Successfully fetched the scenario Name')
            scenarioId = parsedResp["entities"][0]["Fields"][1]["values"][0]["value"]
        return scenarioId


