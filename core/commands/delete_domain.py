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

import common.assertions as assertions
import common.logredirect as logredirect
import shutil
import stat

from java.io import File

execfile('wlst/common.py')
execfile('wlst/server.py')
execfile('wlst/workmgr.py')
execfile('wlst/deployment.py')
execfile('wlst/createDomain.py')
execfile('wlst/jdbc_offline.py')

def run(cfg):
    """Delete WebLogic Domain"""
    assertions.sanityCheckInstall(cfg)
    assertions.sanityCheckDomainConfig(cfg)
    if wlst_support:
    	logredirect.setup()
        delete_domain(cfg)
    else:
        raise Exception('WLST support required for this command')

def remove_readonly(fn, path, excinfo):
    if fn is os.rmdir:
        os.chmod(path, stat.S_IWRITE)
        os.rmdir(path)
    elif fn is os.remove:
        os.chmod(path, stat.S_IWRITE)
        os.remove(path)

def delete_domain(configProperties):
    domainPath=configProperties.getProperty('wls.domain.dir')
    domainName=configProperties.getProperty('wls.domain.name')   
    domainAppDir=configProperties.getProperty('wls.domain.app.dir')

    try:
        if domainName=='':
            log.error("wls.domain.name property can't be empty")
            raise Exception('wls.domain.name property can not be empty')
            
        domainFullPath=str(domainPath) + '/' + str(domainName)
        if not domainExists(domainFullPath):
            log.error("Cannot delete domain at '" + domainPath + "' - directory does not exist")
            return

        log.info("Deleting domain directory '" + domainFullPath + "'")
        shutil.rmtree(domainFullPath, onerror=remove_readonly)

        if domainExists(domainFullPath):
            log.error("Failed to remove domain directory completely. Please check file permissions/open files, and try again.")

    except Exception, error:
        log.error('Unable to delete domain [' + str(domainPath) + '/' + str(domainName) + ']')
        dumpStack()
        raise error

def domainExists(domainPath):
    return File(domainPath).exists()
