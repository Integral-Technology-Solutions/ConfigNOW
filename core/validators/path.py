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
from java.io import File

def run(config):
    result = True
    enum = config.keys()
    # The list of properties that we currently identify as the ones that need a path value against it.
    pathprops=["wls.oracle.home","obpm.home","wls.domain.dir","wls.domain.javahome",".log.rotationDir",".httplog.rotationDir","wls.template."]
    wrongprops=[]
    while enum.hasMoreElements():
        key = enum.nextElement()
        for pathprop in pathprops:
        	if key.find(pathprop)>-1 and len(config.getProperty(key))>1 and config.getProperty(key).find("/")==-1:
				
        		wrongprops.append(key)
        		        		
    if len(wrongprops)>0:
    	log.error("")
       	log.error("The following properties expects a path as its value.Please provide a valid path for this property. If you are on Windows operating system please consider changing your path seperating character from \\ to /")
       	for wrongprop in wrongprops:
       		print "	"+wrongprop+"\n"
       	return False
        		   
    return result
