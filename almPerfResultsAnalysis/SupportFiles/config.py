#!/usr/bin/env python
# Author: Jospaul Mahajan Prakash
# Company: Infosys Limited
# Module handles reading the configuration file

from yaml import load
import os
import logging

# Global variables accessed by other modules
# ALM
almUrl = ""

# Domain Name
domain = ""

# Project Name
project = ""

# Transaction Details and SLA
transactions = {}

# Scenario Name to fetch details
scenarioName = ""

# Scenario ID to fetch details
scenarioId = ""

# Teams Connection
teamsUrl = ""

# Teams result long/short
teamsResult = ""

# Output File Location
fileLoc = ""

# Temporary File Location
tempLoc = ""

# Log File Location
logLoc = ""

# Log level
logLevel = ""

logger = logging.getLogger('rr.sf.config')


# Input Arguments: None
# Output Arguments: None
# Function: Reads the yaml formatted configuration and assigns the appropriate values to the global variables.
def fetchfromconfig():
    global almUrl, transactions, scenarioName, scenarioId, teamsUrl, fileLoc, tempLoc, logLoc, logLevel, domain, \
        project, teamsResult
    currdir = os.getcwd()
    with open(currdir + "\\rrconfig.yml", "r") as ymlfile:
        cfg = load(ymlfile)

    if not cfg:
        logger.error('Config file not present or not parsed. Check config location.')
    else:
        logger.debug('Config file parsed successfully')
        almUrl = cfg['almurl']
        transactions = cfg['transactions']
        scenarioName = cfg['scenarioName']
        scenarioId = cfg['scenarioId']
        teamsUrl = cfg['teamsurl']
        teamsResult = cfg['teamsResult']
        fileLoc = cfg['fileloc']
        tempLoc = cfg['tempLoc']
        logLoc = cfg['logLoc']
        logLevel = cfg['logLevel']
        domain = cfg['domain']
        project = cfg['project']


