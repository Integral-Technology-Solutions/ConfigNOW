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
    """Identifies Configuration Changes"""
    
    admin_name = config.getProperty('wls.admin.name')
    log.info("Admin server's name is '" + admin_name + "'")

    repodir = config.getProperty('ConfigNOW.home') + "/repository/" + config.getProperty('ConfigNOW.environment') + "/" + config.getProperty('ConfigNOW.configuration') + "/"

    # What is todays date
    date_today = datetime.now()
    current_config = str(date_today.year) + '-' + str(date_today.month) + '-' + str(date_today.day) 

    # This field may be a date or constant
    # Date previous sets an absolute previous date
    if config.getProperty('config.date_previous') is not None:
        base_config = config.getProperty('config.date_previous')
    
    # Date diff looks for the difference in dates
    if config.getProperty('config.date_diff') is not None:
        if config.getProperty('config.date_diff') is "previous" or "baseline":
            base_config = config.getProperty('config.date_diff')
        else:
            date_diff = int(config.getProperty('config.date_diff'))
            date_N_days_ago = datetime.now() - timedelta(days=date_diff)  
            base_config = str(date_N_days_ago.year) + '-' + str(date_N_days_ago.month) + '-' + str(date_N_days_ago.day)   


    __connectAdminServer(config)
    serverConfig()

    redirect(config.getProperty('java.io.tmpdir') ,'false')
    log.info("Walking the configuration tree, depending on the size of your instance this may take some time")
    walkTree('/',0)    
    redirect(config.getProperty('java.io.tmpdir') ,'true')

    output_content.sort()

    create_repo(repodir,current_config)

    # Output the findings from this pass
    if output_content is not None and len(output_content) > 0:
        outputfw=javaio.FileWriter(repodir + '/' + current_config + '/MBeans.txt') 
        for line in output_content :
            outputfw.write(line + "\r\n")       
        outputfw.close()
        
         # Also update the previous and baseline as appropiate
    if output_content is not None and len(output_content) > 0:
        # Also update the previous folder so that this is now counted as the previous run
        outputfw=javaio.FileWriter(repodir + '/previous/MBeans.txt') 
        for line in output_content :
            outputfw.write(line + "\r\n")       
        outputfw.close()

        # If there is no baseline file, write it now
    if os.path.isfile(repodir + 'baseline/MBeans.txt') is False:
        outputfw=javaio.FileWriter(repodir + 'baseline/MBeans.txt') 
        for line in output_content :
            outputfw.write(line + "\r\n")       
        outputfw.close()


    # Do the diff potentially against older releases
    diff(current_config, base_config, repodir, "ConfigChanges.html", config.getProperty('ConfigNOW.home') + "/repository/template/report.html", config.getProperty('ConfigNOW.environment'), config.getProperty('ConfigNOW.configuration'))

   

def create_repo(repodir,current_config):    
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

    if not os.path.exists(repodir + current_config + '/'):       
        log.info("Creating the current config directory '" + repodir + current_config + "/" + "'")
        os.makedirs(repodir + current_config + '/')

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



def diff(current_config, base_config, repodir, report_file, template_file,environment,configuration):

    current_config_file = repodir + current_config + '/MBeans.txt'
    base_config_file = repodir + base_config + '/MBeans.txt'
    report_file = repodir + report_file

    try:
        fromlines = open(base_config_file, 'r').readlines()
    except:
        log.info("No file: " + base_config_file + " could be found, diff aborted")
        return

    try:
        tolines = open(current_config_file, 'r').readlines()
    except:
        log.info("No file: " + current_config_file + " could be found, diff aborted")
        return

    log.info("")
    log.info("==================================================")
    log.info("ConfigNOW Configuration Comparison")
    log.info("")
    log.info("Base Config: " + base_config)
    log.info("Current Config: " + current_config)    
    log.info("Base config file   : " + base_config_file )
    log.info("Current config file: " + current_config_file)
    log.info("")
  
    diff_html = ""
    diff_text = ""
    theDiffs = difflib.ndiff(fromlines, tolines)
    
    for eachDiff in theDiffs:
        if (eachDiff[0] == "-"):
            diff_text += "<<< %s\n" % eachDiff[1:].strip()
            diff_html += "<li> <<< %s\n</li>" % eachDiff[1:].strip()
        elif (eachDiff[0] == "+"):
            diff_text += ">>> %s\n" % eachDiff[1:].strip()
            diff_html += "<li> >>> %s\n</li>" % eachDiff[1:].strip()
    
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

    # Do to add better checks for dealing with loops, currently we are using a recursion depth 
    # checking the bean name would be better but doesn't seem to be possible right now in WLST jython
    if currLevel >= 5:
        return

    # Check to see if we have already visited this mbean, this is designed to stop us
    # getting in to loops
#    if getMBI() in checked_mbeans:
        #return

    # Else add it to the list of beens we have checked
#    checked_mbeans.append(getMBI())

    cd (currentDir)
    currLevel=currLevel+1

    log.debug("DIR:LEVEL" + currentDir + " : Level = " +str(currLevel)+"\n")

    currentAttributes = ls(currentDir, returnMap='true', returnType='a')
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