import os
# ============================================================================
#
# Copyright (c) 2007-2012 Integral Technology Solutions Pty Ltd,
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

import common.assertions as assertions
import sys
import tempfile

try:
    from confignow import InputPrompter
except Exception, error:
    raise Exception("Could not load confignow - setenv file for ConfigNOW may be missing")

execfile('wlst/common.py')
execfile('wlst/apps.py')

PROPERTY_DROP_RCU_SCHEMAS = "drop.rcu.schemas"
PROPERTY_GENERATE_RCU_SCRIPTS="generate.rcu.scripts"

def run(cfg):
    """Runs Repository Creation Utility"""
    # assertions.sanityCheckInstall(cfg)
    run_rcu(cfg)

def run_rcu(cfg):
    log.info("Executing RCU")

    log.debug("..checking for availability of RCU files")
    rcuHome = cfg.getProperty('rcu.home')
    if (not os.path.exists(rcuHome)):
        raise Exception("RCU Home '" + rcuHome + "' does not appear to exist")

    log.debug("..getting sys password")
    sysPassword = cfg.getProperty('rcu.db.sys.password')
    if sysPassword is None:
        disablePrompting = cfg.getProperty(PROPERTY_DISABLE_PROMPTING)
        if not disablePrompting:
            log.debug("..prompting for sys password interactively")
            prompter = InputPrompter()
            sysPassword = prompter.readPassword('Enter the sys database password')
        else:
            raise ScriptError, "SYS password not set, and prompting for password is disabled via property '" + PROPERTY_DISABLE_PROMPTING + "'"

    log.debug("..building command string")
    commandString = buildCommandString(cfg)
    log.debug("..built following command string\n" + commandString)

    log.debug("..generating temporary password file")
    tempFile = createTemporaryPasswordFile(cfg, sysPassword)
    log.debug("..generated temporary password file '" + tempFile + "'")

    commandString += " -f < " + tempFile

    # FIXME - remove this
    print "I got this:\n" + commandString

    returnCode = os.system(commandString)
    #os.remove(tempFile)
    log.info(returnCode)
    
    if  returnCode != 0:
        raise ScriptError, "Received error return code from invoking rcu: " + str(returnCode)

#==============================================================================
# createTemporaryPasswordFile
#
# Creates a secure temporary file containing passwords as an input to RCU
#==============================================================================
def createTemporaryPasswordFile(cfg, sysPassword):

    if sysPassword is None:
        raise ScriptError, "Cannot create temporary password file without sys password - None was supplied"

    fileName = tempfile.mktemp()
    log.debug("Generated temporary filename '" + fileName + "'")
    passwordFile = open(fileName, 'w')
    passwordFile.write(sysPassword + "\n")

    # create entry for each component defined in properties file
    dbComponentList = cfg.getProperty('rcu.db.components')
    dbComponents = dbComponentList.split(',')
    for component in dbComponents:
        propertyKey = 'rcu.db.component.' + component + '.password'
        log.debug("..checking for password at key '" + propertyKey +"'")
        log.debug("..checking for password at key '" + cfg.getProperty(propertyKey) + "'")
        passwordFile.write(cfg.getProperty(propertyKey) + "\n")
        
    # RCU for Oracle 12.2.1 version requires an additional password to be supplied for WLS Schema Runtime.
    additionalpwd=cfg.getProperty('rcu.db.component.WLSAUX.password')
    if additionalpwd is not None:
        log.debug("setting up additional password for Oracle 12.2.1 version and beyond"+additionalpwd)
        passwordFile.write(additionalpwd + "\n")
    passwordFile.close()
    
    return fileName

#==============================================================================
# buildCommandString
#
# Returns the full command string to be used to execute RCU
#==============================================================================
def buildCommandString(cfg):

    rcuHome = cfg.getProperty('rcu.home')

    # get script type to execute
    rcuScript = "bin" + os.sep + "rcu"
    osType = getOsType()
    if osType == OS_TYPE_WINDOWS:
        rcuScript += ".bat"

    rcuCommand = rcuHome + os.sep + rcuScript + " -silent"

    # check for drop parameter
    rcuDrop = cfg.getProperty('drop.rcu.schemas')
    #FIX me : This should rather be an option for a property value rather than a property in itself which can lead to confusions, Leaving like this for now to make sure we are backwards comatible with RCU 11G version
    generateScripts=cfg.getProperty('generate.rcu.scripts')
    loaddata=cfg.getProperty('load.rcu.data')
    rcuuser=cfg.getProperty('rcu.user')
    scriptslocation=cfg.getProperty('rcu.scripts.location')
    version=cfg.getProperty('wls.version')
    
    
    
    if(rcuDrop is None):
        rcuDrop=' false'
                
        
    if((generateScripts is not None and generateScripts.upper()=='TRUE') and (loaddata is not None and loaddata.upper()=='TRUE')) or ((generateScripts is not None and generateScripts.upper()=='TRUE') and (rcuDrop is not None and rcuDrop.upper()=='TRUE')) or ((rcuDrop is not None and rcuDrop.upper()=='TRUE') and (loaddata is not None and loaddata.upper()=='TRUE')):
        log.error("Only one of the RCu operations can be executed at once, please make sure only one of the properties among 'generate.rcu.scripts','load.rcu.data','drop.rcu.schemas' is set to true")
        raise Exception("Only one of the RCU operations can be executed at once, please make sure only one of the properties among 'generate.rcu.scripts','load.rcu.data','drop.rcu.schemas' is set to true")
    
    if rcuDrop is not None and rcuDrop.upper()=='TRUE':
        log.info("building command for RCU Drop Operation")
        rcuCommand += " -dropRepository -databaseType ORACLE"
    elif generateScripts is not None and generateScripts.upper()=='TRUE':
        log.info("building command for RCU script generation operation")
        rcuCommand += " -generateScript -databaseType ORACLE"
    elif loaddata is not None and loaddata.upper()=='TRUE':
        log.info("building command for RCU data load operation")
        rcuCommand += " -dataLoad -databaseType ORACLE"
    else:
        rcuCommand += " -createRepository"
        
        
        
    if generateScripts is not None and generateScripts.upper()=='TRUE':
        if (not os.path.exists(scriptslocation)):
            raise Exception("Scripts Location specified '" + scriptslocation + "' does not appear to exist")
        rcuCommand += " -connectString " + cfg.getProperty('rcu.db.url') + " -dbUser "+rcuuser+" -dbRole sysdba -scriptLocation "+scriptslocation +" -schemaPrefix " + cfg.getProperty('soa.schema.prefix')
    else:    
        rcuCommand += " -connectString " + cfg.getProperty('rcu.db.url') + " -dbUser sys -dbRole sysdba -schemaPrefix " + cfg.getProperty('soa.schema.prefix')

    # create entry for each component defined in properties file
    dbComponentList = cfg.getProperty('rcu.db.components')
    dbComponents = dbComponentList.split(',')
    for component in dbComponents:
        rcuCommand += " -component " + component

    return rcuCommand
