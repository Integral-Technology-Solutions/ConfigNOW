# ============================================================================
#
# Copyright (c) 2007-2011 Integral Technology Solutions Pty Ltd, 
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
execfile('wlst/apps.py')

def run(cfg):
    """Deploy JEE applications to WebLogic"""
    assertions.sanityCheckInstall(cfg)
    assertions.sanityCheckDomainConfig(cfg)
    assertions.sanityCheckOnlineConfig(cfg)
    if wlst_support:
        deploy_apps(cfg)
    else:
        raise Exception('WLST support required for this command')
        
def deploy_apps(cfg):
    __connectAdminServer(cfg)
    edit()
    startEdit()
    try:
        deployApps(cfg)
    except Exception, error:
        print 'Unable to deploy applications : ' + str(error)
        cancelEdit('y')
    else:
        save()
        activate(block='true')
    #disconnect('true')

