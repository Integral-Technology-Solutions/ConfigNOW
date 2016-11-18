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

def run(config):
    valid=1
    
    obpmHome=config.getProperty('obpm.home')
    if obpmHome:
    	obpmAdminPwd=config.getProperty('obpm.admin.password')
    	if obpmAdminPwd:
			if len(obpmAdminPwd) < 6:
				valid=0
				log.error('The password set for obpm.admin.password must be at least 6 characters long.')
	
    return valid