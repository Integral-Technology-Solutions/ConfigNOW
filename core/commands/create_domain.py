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

from java.io import File

execfile('wlst/common.py')
execfile('wlst/server.py')
execfile('wlst/workmgr.py')
execfile('wlst/deployment.py')
execfile('wlst/createDomain.py')
execfile('wlst/jdbc_offline.py')

def run(cfg):
    """Create WebLogic Domain"""
    assertions.sanityCheckInstall(cfg)
    assertions.sanityCheckDomainConfig(cfg)
    if wlst_support:
    	logredirect.setup()
        create_domain(cfg)
    else:
        raise Exception('WLST support required for this command')

def create_domain(configProperties):
    domainPath=configProperties.getProperty('wls.domain.dir')
    domainName=configProperties.getProperty('wls.domain.name')   
    domainAppDir=configProperties.getProperty('wls.domain.app.dir')
    webLogicHome=configProperties.getProperty('wls.oracle.home')
    osbname=configProperties.getProperty('osb.name')
    soaname=configProperties.getProperty('soa.name')
    version=configProperties.getProperty('wls.version')
    
    try:
    	if domainName=='':
    	    log.error("wls.domain.name property can't be empty")
    	    raise Exception('wls.domain.name property can not be empty')
        domainFullPath=str(domainPath) + '/' + str(domainName)
        checkDomainExistence(domainFullPath)	
		
        log.info('Creating domain: ' + domainFullPath)
		
        __createDomain(configProperties)
        log.info("Reading domain")
        readDomain(domainFullPath)
        if version == '12' and (not soaname is None):
            log.debug("not plain WLS domain")
                                 
            jrfTemplateLoc=configProperties.getProperty('wls.template.jrf.file')
            ServiceTableName=configProperties.getProperty('jdbc.datasource.LocalSvcTblDataSource.Name')
            ServiceTableUser=configProperties.getProperty('jdbc.datasource.LocalSvcTblDataSource.Username')
            ServiceTableURL=configProperties.getProperty('jdbc.datasource.LocalSvcTblDataSource.URL')
            ServiceTableDriver=configProperties.getProperty('jdbc.datasource.LocalSvcTblDataSource.Driver')
            ServiceTablePassword=configProperties.getProperty('jdbc.datasource.LocalSvcTblDataSource.Password')            
                       
            __addTemplate(configProperties)
                        
            log.info("Connecting to Service table")                
            cd('/JDBCSystemResources/'+ServiceTableName+'/JdbcResource/'+ServiceTableName+'')
            cd('JDBCDriverParams/NO_NAME_0')
            set('DriverName','oracle.jdbc.OracleDriver')
            set('URL',ServiceTableURL)
            set('PasswordEncrypted',ServiceTablePassword)
            cd('Properties/NO_NAME_0')
            cd('Property/user')
            
            cmo.setValue(ServiceTableUser)
            log.debug(ServiceTableURL)
            log.debug(ServiceTableUser)
            log.info('Connected to ServiceTable'+ServiceTableName+'......Fetching DB Schema details now')
            getDatabaseDefaults()
            #print 'Coherence changes'
            #cd('/')
            #cd('Server/soa_server1')
            #create('member_config', 'CoherenceMemberConfig')
            #cd('CoherenceMemberConfig/member_config')
            #set('UnicastListenAddress', '121.0.0.1')

            
            log.debug('Finished updating 12c changes')
            
        else:
            __addTemplate(configProperties)
            
        __createMachines(0, configProperties)
        __createClusters(0, configProperties)
        __createServers(0, configProperties)
        __createWorkManagers(0, configProperties)
        __configureDeployments(0, configProperties)
        __configureDataSources(configProperties)
        
        log.info("Closing Template NOW")
        updateDomain()
        closeDomain()
                
               
    except Exception, error:
        log.error('Unable to create domain [' + str(domainPath) + '/' + str(domainName) + ']')
        raise error
    
#    __processPostDomainCreation(configProperties)
        
def checkDomainExistence(domainPath):
	if File(domainPath).exists():
		raise Exception('Cannot create domain as it already exists at ' + domainPath)
