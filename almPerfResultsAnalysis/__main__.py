# Author: Jospaul Mahajan Prakash
# Company: Infosys Limited
#
# The application helps in fetching the load runner performance test results from ALM and compiling the data in to
# a csv file or also pushes the content to teams for inclusion in to CI pipelines.
#
# The final table can currently be output in 2 ways -
#   * as a csv file to the folder location specified
#   * directly to a teams channel
#
# The application does SLA analysis if it is output to teams.
#

from SupportFiles.runAnalysisReport import createLrAnalyzeReport
import SupportFiles.logconfig as lcf
import SupportFiles.config as cnf
import logging

if __name__ == "__main__":
    cnf.fetchfromconfig()
    lcf.enablelog()
    logger = logging.getLogger('rr.main')
    logger.info('Start Report Generation.')
    createLrAnalyzeReport()
