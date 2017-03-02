# ============================================================================
#
# Copyright (c) 2007-2010 Integral Technology Solutions Pty Ltd,
# All Rights Reserved.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT OF THIRD PARTY RIGHTS.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR HOLDERS INCLUDED IN THIS NOTICE BE
# LIABLE FOR ANY CLAIM, OR ANY SPECIAL INDIRECT OR CONSEQUENTIAL DAMAGES, OR
# ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER
# IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT
# OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
#
# FOR FURTHER INFORMATION PLEASE SEE THE INTEGRAL TECHNOLOGY SOLUTIONS
# END USER LICENSE AGREEMENT (ELUA).
#
# ============================================================================

execfile('wlst/common.py')
#from sets import Set
import sys
import difflib
import java.io as javaio
import weblogic.management.NoAccessRuntimeException as NoAccessRuntimeException
from datetime import datetime, timedelta

checked_mbeans = []
output_content = []

current_config = ""
base_config = ""

def run(config):
    """Identifies Configuration Changes on OFM environments"""
    diff_type = config.getProperty('config.diff_type')

    if diff_type is None:
        log.error("You must provide a config.diff_type of either baseline, previous, date, relative or comparison")
        return
    elif diff_type in ["baseline,","previous","date","relative","comparison"]:
        log.info ("Diff type = " + diff_type)

        if (diff_type in ["baseline","previous"]):
            base_config = diff_type
            environment = config.getProperty('ConfigNOW.environment')
            diff_single_environment(config, environment, base_config)
        # Date diff looks for the difference in dates
        elif (diff_type in ["date","relative"]):
            # This field may be a date or constant
            # Date previous sets an absolute previous date
            if config.getProperty('config.date_previous') is not None:
                base_config = config.getProperty('config.date_previous')
                environment = config.getProperty('ConfigNOW.environment')
                diff_single_environment(config, environment, base_config)
            elif config.getProperty('config.date_diff') is not None:
                date_diff = int(config.getProperty('config.date_diff'))
                date_N_days_ago = datetime.now() - timedelta(days=date_diff)
                base_config = str(date_N_days_ago.year) + '-' + str(date_N_days_ago.month) + '-' + str(date_N_days_ago.day)
                diff_single_environment(config, environment, base_config)
        elif (diff_type in ["comparison"]):
                diff_multiple_environments(config)
    else:
        log.error("You must provide a config.diff_type of either baseline, previous, date, relative or comparison")
        return

def diff_multiple_environments(config):
    # Generate Report for Source
    log.info('diff_multiple_environments')
    environment = config.getProperty('ConfigNOW.environment')
    repodir = config.getProperty('ConfigNOW.home') + '/repository/'
    from_environment = config.getProperty('config.diff.environment.from')
    to_environment = config.getProperty('config.diff.environment.to')
    report_file = config.getProperty('config.diff.report.location') + '/' + config.getProperty('config.diff.report.filename')
    template_file = config.getProperty('ConfigNOW.home') + '/repository/template/report.html'
    current_config = repodir + from_environment + '/' + config.getProperty('config.diff.environment.from.propertyFile') + '/previous/MBeans.txt'
    base_config = repodir + to_environment + '/' + config.getProperty('config.diff.environment.to.propertyFile') + '/previous/MBeans.txt'
    configuration = config.getProperty('ConfigNOW.configuration')
    replaceString = config.getProperty('config.diff.report.replaceString')
    replaceWords = config.getProperty('config.diff.report.replaceWords').split(',')

    diff(current_config, base_config, report_file, template_file, environment, configuration, replaceWords, replaceString)

def diff_single_environment(config, environment, base_config):
    date_today = datetime.now()
    current_config_folder = str(date_today.year) + '-' + str(date_today.month) + '-' + str(date_today.day)
    configuration = config.getProperty('ConfigNOW.configuration')
    repodir = config.getProperty('ConfigNOW.home') + "/repository/" + environment + '/' + configuration + '/'
    template_file = config.getProperty('ConfigNOW.home') + "/repository/template/report.html"
    current_config = repodir + current_config_folder + '/MBeans.txt'
    base_config = repodir + base_config + '/MBeans.txt'
    report_file = repodir + "ConfigChanges.html"
    replaceWords = config.getProperty('config.diff.report.replaceWords')
    replaceString = config.getProperty('config.diff.report.replaceString')

    generate_mbean_file(config, current_config_folder, base_config, repodir)
    diff(current_config, base_config, report_file, template_file, environment, configuration, replaceWords, replaceString)
    write_to_file(repodir + 'previous/MBeans.txt', output_content)

def update_previous_file():
    if output_content is not None and len(output_content) > 0:
            # Also update the previous folder so that this is now counted as the previous run
            outputfw=javaio.FileWriter(repodir + 'previous/MBeans.txt')
            for line in output_content :
                outputfw.write(line + "\r\n")
            outputfw.close()

def generate_mbean_file(config, current_config_folder, base_config, repodir):
    __connectAdminServer(config)
    serverConfig()

    redirect(config.getProperty('java.io.tmpdir') + '/' + config.getProperty('ConfigNOW.environment') ,'false')
    log.info("Walking the configuration tree, depending on the size of your instance this may take some time")
    walkTree('/',0)
    redirect(config.getProperty('java.io.tmpdir') + '/' + config.getProperty('ConfigNOW.environment') ,'true')

    output_content.sort()

    create_repo(repodir,current_config_folder)

    # Output the findings from this pass
    write_to_file(repodir + '/' + current_config_folder + '/MBeans.txt', output_content)

    # Also update the previous and baseline as appropiate
    # If there is no previous file, write it now
    if os.path.isfile(repodir + 'previous/MBeans.txt') is False:
        write_to_file(repodir + 'previous/MBeans.txt', output_content)

    # If there is no baseline file, write it now
    if os.path.isfile(repodir + 'baseline/MBeans.txt') is False:
        write_to_file(repodir + 'baseline/MBeans.txt', output_content)

def write_to_file(filename, file_content):
    if file_content is not None and len(file_content) > 0:
        outputfw=javaio.FileWriter(filename)
        for line in file_content :
            outputfw.write(line + "\r\n")
        outputfw.close()

def create_repo(repodir,current_config_folder):
    d = os.path.dirname(repodir)
    if not os.path.exists(d):
        log.info("Creating the repository '" + d + "'")
        os.makedirs(d)

    if not os.path.exists(repodir + 'previous/'):
        log.info("Creating the previous log directory '" + repodir + "previous/" + "'")
        os.makedirs(repodir + 'previous/')

    if not os.path.exists(repodir + 'baseline/'):
        log.info("Creating the baseline log directory '" + repodir + "baseline/" + "'")
        os.makedirs(repodir + 'baseline/')

    if not os.path.exists(repodir + current_config_folder + '/'):
        log.info("Creating the current config directory '" + repodir + current_config_folder + '/' + "'")
        os.makedirs(repodir + current_config_folder + '/')

def get_file_directory(file):
    return os.path.dirname(os.path.abspath(file))

#to do not, yet working right
def cleanup_repo(days_to_keep):
    now = time.time()
    cutoff = now - (days_to_keep * 86400)

    log.info("Clearing configuration diff repository located at '" + repodir + "'")

    files = os.listdir(os.path.join(get_file_directory(config.getProperty('ConfigNOW.home')), "repository"))
    file_path = os.path.join(get_file_directory(config.getProperty('ConfigNOW.home')), "repository/")
    for xfile in files:
        if os.path.isfile(str(file_path) + xfile):
            t = os.stat(str(file_path) + xfile)
            c = t.st_ctime

            # delete file if older than 10 days
            if c < cutoff:
                log.info("Removing config file '" + xfile + "'")
                os.remove(str(file_path) + xfile)

def diff(current_config, base_config, report_file, template_file, environment, configuration, replaceWords, replaceString):
    log.info('base_config: ' + base_config)
    log.info('current_config: ' + current_config)
    log.info('report_file: ' + report_file)
    log.info('template_file: ' + template_file)
    log.info('environment: ' + environment)
    log.info('configuration: ' + configuration)

    try:
        fromlines = open(base_config, 'r').readlines()
        if replaceWords is not None and len(replaceWords) > 0:
            for replaceWord in replaceWords:
                fromlines = [w.replace(replaceWord, replaceString) for w in fromlines]
        else:
            log.info('replaceWords are not provided. skipping')
    except:
        log.info("No file (base): " + base_config + " could be found, diff aborted")
        return

    try:
        tolines = open(current_config, 'r').readlines()
        if replaceWords is not None and len(replaceWords) > 0:
            for replaceWord in replaceWords:
                tolines = [w.replace(replaceWord, replaceString) for w in tolines]
        else:
            log.info('replaceWords are not provided. skipping')
    except:
        log.info("No file (current): " + current_config + " could be found, diff aborted")
        return

    log.info("")
    log.info("==================================================")
    log.info("ConfigNOW Configuration Comparison")
    log.info("")
    log.info("Base Config: " + base_config)
    log.info("Current Config: " + current_config)
    log.info("Base config file   : " + base_config )
    log.info("Current config file: " + current_config)
    log.info("")

    diff_html = "<table class='table table-striped'>\n"
    diff_html += "<thead>\n"
    diff_html += "<tr>\n"
    diff_html += "<th class='first'>[" + base_config + "]</th>\n"
    diff_html += "<th class='second'>[" + current_config + "]</th>\n"
    diff_html += "</tr>\n"
    diff_html += "</thead>\n"
    diff_html += "<tbody>\n"
    diff_text = ""
    currentHeader = ""
    theDiffs = difflib.ndiff(fromlines, tolines)
    previousValue = ""
    lastColumn = 0
    headerHtml = ""
    headerShown = false

    for eachDiff in theDiffs:
        newHeader = eachDiff[1:].strip().split('::')[0]
        thisValue = eachDiff[1:].strip().split('=')[0]

        if (eachDiff[0] == "-" or eachDiff[0] == "+" or eachDiff[0] == " "):
            if (thisValue != previousValue):
                newValue = true
                previousValue = thisValue
            else:
                newValue = false

            if (currentHeader != newHeader):
                currentHeader = newHeader
                headerHtml = "<td colspan='2' class='mbeanRow'><h4>" + newHeader + "</h4></td></tr>\n<tr valign='top'>\n"
                headerShown = false
                newValue = true

        if (eachDiff[0] == "-"):
            diff_text += "<<< %s\n" % eachDiff[1:].strip()

            # If we have a new value the previous column was 1, then we need to close off column two and end the line
            if (newValue):
                if (lastColumn == 0):
                    #Must be a brand new report
                    diff_html += "<tr valign='top'>\n"
                elif (lastColumn == 1):
                    diff_html += "<td class='col-md-6' mark1>\n"
                    diff_html += "<div style='display: inline-block; overflow-wrap: break-word; word-wrap: break-word; word-break: break-all; '></div>\n"
                    diff_html += "</td>\n"
                    diff_html += "</tr>\n"
                    diff_html += "<tr valign='top'>\n"
                else:
                    # Must be equal to 2
                    diff_html += "</tr>\n"
                    diff_html += "<tr valign='top'>\n"

            # Because this is where we are diffing from, any value will be a new line

            if (headerShown == false):
                diff_html += headerHtml
                headerShown = true

            diff_html += "<td class='col-md-6' mark2>\n"
            diff_html += "<div style='display: inline-block; overflow-wrap: break-word; word-wrap: break-word; word-break: break-all; '> %s </div>\n" % eachDiff[1:].strip().split('::')[1]
            diff_html += "</td>\n"
            lastColumn = 1

        elif (eachDiff[0] == "+"):
            diff_text += ">>> %s\n" % eachDiff[1:].strip()

            #If we have a new value and the previous column was 1, then we need to close off the line and then
            #a column to bring us to column two... If the previous column was 2 then it requires one less column
            if (newValue):
                if (lastColumn == 0):
                    #Must be a brand new report
                    diff_html += "<tr valign='top'>\n"
                    diff_html += "<td class='col-md-6' mark3>\n"
                    diff_html += "<div style='display: inline-block; overflow-wrap: break-word; word-wrap: break-word; word-break: break-all; '></div>\n"
                    diff_html += "</td>\n"
                elif (lastColumn == 1):
                    diff_html += "<td class='col-md-6' mark4>\n"
                    diff_html += "<div style='display: inline-block; overflow-wrap: break-word; word-wrap: break-word; word-break: break-all; '></div>\n"
                    diff_html += "</td>\n"
                    diff_html += "</tr>\n"
                    diff_html += "<tr valign='top'>\n"
                    if (headerShown == false):
                        diff_html += headerHtml
                        headerShown = true
                    diff_html += "<td class='col-md-6' mark5>\n"
                    diff_html += "<div style='display: inline-block; overflow-wrap: break-word; word-wrap: break-word; word-break: break-all; '></div>\n"
                    diff_html += "</td>\n"
                else:
                    # Must be equal to 2
                    diff_html += "</tr>\n"
                    diff_html += "<tr valign='top'>\n"
                    if (headerShown == false):
                        diff_html += headerHtml
                        headerShown = true
                    diff_html += "<td class='col-md-6' mark6>\n"
                    diff_html += "<div style='display: inline-block; overflow-wrap: break-word; word-wrap: break-word; word-break: break-all; '></div>\n"
                    diff_html += "</td>\n"

            if (headerShown == false):
                diff_html += headerHtml
                headerShown = true

            diff_html += "<td class='col-md-6' mark7>\n"
            diff_html += "<div style='display: inline-block; overflow-wrap: break-word; word-wrap: break-word; word-break: break-all; '> %s </div>\n" % eachDiff[1:].strip().split('::')[1]
            diff_html += "</td>\n"
            lastColumn = 2

    if diff_text is None or len(diff_text) == 0:
        diff_html += "<h1>No changes found</h1>"

    diff_html += "</tbody>\n</table>\n</body>"

    log.info("Found the following changes: \r\n\r\n" + diff_text)
    log.info("==================================================")

    # Now build the HTML report
    template = open(template_file ,'r')
    templateHtml = template.read()
    template.close()

    templateHtml = templateHtml.replace("<DIFF-CONTENT>",diff_html)
    templateHtml = templateHtml.replace("<BASE-CONFIG>",base_config)
    templateHtml = templateHtml.replace("<CURRENT-CONFIG>",current_config)
    templateHtml = templateHtml.replace("<CONFIGNOW-ENV>",environment)
    templateHtml = templateHtml.replace("<CONFIGNOW-CONFIGURATION>",configuration)

    report = open(report_file,'w')
    report.write(templateHtml)
    report.close()


def walkTree(currentDir,currLevel):

    # Longer term look to do to add better checks for dealing with loops, currently we are using a recursion depth
    # checking the bean name would be better but doesn't seem to be possible right now in WLST jython
    # so we are using recursion depth as an approach to stop us looping back on ourselves
    if currLevel >= 5:
        return

    try:
        cd (currentDir)
    except:
        return

    currLevel=currLevel+1

    log.debug("DIR:LEVEL" + currentDir + " : Level = " +str(currLevel)+"\n")

    currentAttributes = []

    try:
        currentAttributes = ls(currentDir, returnMap='true', returnType='a')
    except:
        log.info("Issue trying to get attributes on mbean " + currentDir)

    childDirs = ls(currentDir, returnMap='true', returnType='c')

    #   Output information on the children
    log.debug("Children: ")
    for child in childDirs :
        log.debug(child)

#   Atrributes
    for attribute in currentAttributes :
        try:
            value = get(attribute)
            pass
        # Probably an attribute protected by security
        except:
            value = "******"

        if value is not None :
            output_content.append(currentDir+"::"+attribute+"="+str(value))

    # Drop down to the next level
    if len(childDirs) <= 0 :
        return
    for child in childDirs :
        if currentDir == '/':
            childDirectory = '/' + child
        else:
            childDirectory = currentDir + '/' + child

        # We don't follow things that can be targeted as they can lead to recursion
        if "Targets" not in child:
            walkTree(childDirectory,currLevel)

