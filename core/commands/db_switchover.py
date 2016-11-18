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

from java.net import Socket

execfile('wlst/common.py')

def run(config):
    """Database Switchover to Alternate Site"""
    
    rac_site=config.getProperty('rac.site')
    if not rac_site:
    	raise Exception('rac.site property must be set.')
    
    server_running=__isAdminServerRunning(config)
    if server_running:
        log.debug('Performing switchover via WLST Online')
        __performOnlineSwitch(config, rac_site)
    else:
        log.debug('Performing switchover via WLST Offline')
        __performOfflineSwitch(config, rac_site)

def __isAdminServerRunning(config):
    address=config.getProperty('wls.admin.listener.address')
    port=config.getProperty('wls.admin.listener.port')
    try:
        Socket(str(address),int(port))
    except Exception, error:
        return False
    return True
        
def __performOnlineSwitch(config, rac_site):
    try:
        __connectAdminServer(config)
        edit()
        startEdit()
        multids_prop=config.getProperty('jdbc.multidatasources')
        if multids_prop is not None:
            previousDataSources=[]
            mds_list=multids_prop.split(',')
            for mds in mds_list:
                mds_prefix='jdbc.multidatasource.' + str(mds)
                mds_name=config.getProperty(mds_prefix + '.Name')
                jdbcSystemResource = lookup(mds_name, 'JDBCSystemResource')
                jdbcResource = jdbcSystemResource.getJDBCResource()
                dpBean = jdbcResource.getJDBCDataSourceParams()
                site_datasources=config.getProperty(mds_prefix + '.rac.site.' + rac_site + '.DataSources')
                if site_datasources is not None:
                    resolved_datasources=__resolveDsNames(site_datasources, config)
                    current_list = dpBean.getDataSourceList()
                    __setTargetsOnline(resolved_datasources, jdbcSystemResource.getTargets())
                    
                    dpBean.setDataSourceList(resolved_datasources)
                    log.info('Switched [' + str(mds_name) + '] from [' + str(current_list) + '] to [' + str(resolved_datasources) + ']') 
					
                    if current_list!=resolved_datasources:
                        previousDataSources.append(current_list)
                else:
                    log.warn(mds_name + ' not configured for ' + rac_site + ' site')
            
			# Untarget the previous data sources so that their unavailbility
			# does not cause the servers to fail on startup. Required for OSB 10.3.1
            if previousDataSources.__len__() > 0:
                save()
                activate(block='true')
                edit()
                startEdit()
                for oldDs in previousDataSources:
                    log.debug('Untargeting ' + str(oldDs))
                    __untargetOnline(oldDs)
                
    except Exception, error:
        cancelEdit('y')
        disconnect('true')
        raise Exception('Unable to perform online DB switch over : ' + str(error))
    else:
        save()
        activate(block='true')
        disconnect('true')

def __untargetOnline(datasources):
	dsList=datasources.split(',')
	for ds in dsList:
		ds=lookup(ds, 'JDBCSystemResources')
		ds.setTargets(None)

def __setTargetsOnline(datasources, targets):
	dsList=datasources.split(',')
	for ds in dsList:
		ds=lookup(ds, 'JDBCSystemResources')
		ds.setTargets(targets)

def __untargetOffline(datasources):
	dsList=datasources.split(',')
	for ds in dsList:
		cd('/JDBCSystemResource/' + ds)
		targets=get('Target')
		for target in targets:
			targetName=target.getName()
			unassign('JDBCSystemResource', ds, 'Target', targetName)	

def __setTargetsOffline(datasources, targets):
	dsList=datasources.split(',')
	for ds in dsList:
		for target in targets:
			targetName=target.getName()
			assign('JDBCSystemResource', ds, 'Target', targetName)
 
def __performOfflineSwitch(config, rac_site):
    domainDir=config.getProperty('wls.domain.dir')
    domainName=config.getProperty('wls.domain.name')
    readDomain(domainDir + '/' + domainName)
    multids_prop=config.getProperty('jdbc.multidatasources')
    if multids_prop is not None:
        mds_list=multids_prop.split(',')
        for mds in mds_list:
            mds_prefix='jdbc.multidatasource.' + str(mds)
            mds_name=config.getProperty(mds_prefix + '.Name')
            cd('/JDBCSystemResource/' + mds_name)
            targets=get('Target')
            site_datasources=config.getProperty(mds_prefix + '.rac.site.' + rac_site + '.DataSources')
            cd('/JDBCSystemResource/' + mds_name + '/JdbcResource/' + mds_name + '/JDBCDataSourceParams/NO_NAME_0')
            if site_datasources:
                resolved_datasources=__resolveDsNames(site_datasources, config)
                __setTargetsOffline(resolved_datasources,targets)
                current_list = get('DataSourceList')
                set('DataSourceList',resolved_datasources)
                log.info('Switched [' + str(mds_name) + '] from [' + str(current_list) + '] to [' + str(resolved_datasources) + ']') 
            	
            	# Untarget the previous data sources so that their unavailbility
			    # does not cause the servers to fail on startup. Required for OSB 10.3.1
            	if current_list!=resolved_datasources:
            	    __untargetOffline(current_list)
            	    log.debug('Untargeting ' + str(current_list))
            else:
                log.warn(mds_name + ' not configured for ' + rac_site + ' site')
    updateDomain()
    closeDomain()
 
def __resolveDsNames(data_sources, config):
    dslist = data_sources.split(',')
    datasourceNames = None
    for item in dslist:
        datasourceName = config.getProperty('jdbc.datasource.' + item + '.Name')
        if datasourceNames is None:
            datasourceNames = datasourceName
        else:
            datasourceNames = datasourceNames + ',' + datasourceName
    return datasourceNames

# Put this into common
def __cleanCd(path):
    original_stdout = sys.stdout
    sys.stdout = NullDevice()
    try:
        cd(path)
    except Exception, error:
        sys.stdout = original_stdout
        return False
    sys.stdout = original_stdout 
    return True

class NullDevice:
    def write(self, s):
        pass
