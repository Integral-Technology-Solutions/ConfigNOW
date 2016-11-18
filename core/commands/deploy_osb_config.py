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

try:
    execfile('wlst/common.py')
    execfile('wlst/osb.py')
except ImportError:
    print 'deploy_osb_config command is not available as CLASSPATH requirements are not met'
    raise  Exception('OSB not found in classpath') 
    
def run(cfg):
    """Deploy OSB configuration to OSB domain"""
    assertions.sanityCheckInstall(cfg)
    assertions.sanityCheckDomainConfig(cfg)
    assertions.sanityCheckOnlineConfig(cfg)
    if wlst_support:
        deploy_osb_config(cfg)
    else:
        raise Exception('WLST support required for this command')
        
def deploy_osb_config(cfg):
    __connectAdminServer(cfg)

    try:
        deployOsbCfg(cfg)
    except Exception, error:
        print 'Unable to deploy OSB application : ' + str(error)
