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

execfile('wlst/common.py')
execfile('wlst/persist.py')
execfile('wlst/jms.py')
execfile('wlst/jdbc.py')
execfile('wlst/sec.py')
execfile('wlst/snmp.py')
execfile('wlst/securityProviders.py')
execfile('wlst/server.py')
execfile('wlst/deployment.py')  
execfile('wlst/migration.py')
execfile('wlst/nodemanager.py')
execfile('wlst/apps.py')

def run(cfg):
    """Configure existing WebLogic Domain"""
    assertions.sanityCheckInstall(cfg)
    assertions.sanityCheckDomainConfig(cfg)
    assertions.sanityCheckOnlineConfig(cfg)
    if wlst_support:
        configure_domain(cfg)
    else:
        raise Exception('WLST support required for this command')
        
def configure_domain(cfg):
    __connectAdminServer(cfg)
    edit()
    startEdit()
    try:
        createFileStores(cfg,cfg)
        createDataSources(cfg,cfg)
        createMultiDataSources(cfg,cfg)
        createJMSServers(cfg,cfg)
        createJMSModules(cfg,cfg)
        createSecurityProviders(cfg,cfg)
        createSNMP(cfg,cfg)
        configureClusters(cfg,cfg)
        configureServers(cfg,cfg)
        configureMigration(cfg,cfg)
        configureSubApplications(cfg)
        configureNodeManager(cfg)
        deployApps(cfg)
    except Exception, error:
        print 'Unable to update domain : ' + str(error)
        cancelEdit('y')
        disconnect('true')
    else:
        save()
        activate(block='true')