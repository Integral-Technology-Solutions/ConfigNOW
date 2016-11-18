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

import validation_helper as helper

def run(cfg):
	valid=1
	
	helper.printHeader('[VALIDATING] nodemanager properties')
	
	if helper.validateBoolean(cfg,'nodemanager.secure.listener') is 0:
		valid=0		
	if helper.validateBoolean(cfg,'nodemanager.crashrecovery') is 0:
		valid=0		
	if helper.validateBoolean(cfg,'nodemanager.startscriptenabled') is 0:
		valid=0	
	if helper.validateBoolean(cfg,'nodemanager.domain.dir.sharing') is 0:
		valid=0
	if helper.validateNumber(cfg,'nodemanager.logcount') is 0:
		valid=0
	if helper.validateNumber(cfg,'nodemanager.loglimit') is 0:
		valid=0
	if helper.validateNumber(cfg,'nodemanager.listerner.port') is 0:
		valid=0
		
	return valid
		