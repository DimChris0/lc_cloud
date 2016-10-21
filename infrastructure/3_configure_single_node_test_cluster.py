# Copyright 2015 refractionPOINT
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import sys
import hashlib
import argparse

root = os.path.join( os.path.abspath( os.path.dirname( __file__ ) ), '..', '..' )
binaryPath = os.path.join( root, 'prebuilt_binaries' )
hcpRootKey = os.path.join( root, 'keys', 'root.priv.der' )
hcpConfig = None
hbsConfig = None

parser = argparse.ArgumentParser()
parser.add_argument( '-b', '--binaries',
                     type = str ,
                     required = False,
                     help = 'Specify a directory containing all prebuilt and configured binaries you want to task.',
                     dest = 'binaries' )
parser.add_argument( '-hcp', 
                     type = str,
                     required = False,
                     help = 'Specify an HCP sensor config file to apply to the binaries.',
                     dest = 'hcp' )
parser.add_argument( '-hbs', 
                     type = str,
                     required = False,
                     help = 'Specify an HBS sensor config file to apply to the binaries.',
                     dest = 'hbs' )
parser.add_argument( '-k', '--rootkey',
                     type = str,
                     required = False,
                     help = 'Path to the HCP root private key to sign modules with.',
                     dest = 'key' )
parser.add_argument( '-g', '--genkeys',
                     required = False,
                     action = 'store_true',
                     default = False,
                     help = 'If present, generate a new set of keys.',
                     dest = 'genkeys' )
arguments = parser.parse_args()

if arguments.binaries is not None:
    binaryPath = os.path.abspath( arguments.binaries )
    print( 'Setting binaries path: %s' % binaryPath )

if arguments.key is not None:
    hcpRootKey = os.path.abspath( arguments.key )
    print( 'Using HCP root key: %s' % hcpRootKey )

if arguments.hcp is not None:
    hcpConfig = os.path.abspath( arguments.hcp )
    print( 'Using HCP config: %s' % hcpConfig )

if arguments.hbs is not None:
    hbsConfig = os.path.abspath( arguments.hbs )
    print( 'Using HBS config: %s' % hbsConfig )

cwd = os.path.curdir

def printStep( step, *ret ):
    msg = '''
===============
Step: %s
Return Values: %s
===============

''' % ( step, str( ret ) )
    print( msg )
    if any( ret ):
        print( 'Stopping execution since this step failed.' )
        sys.exit(-1)

def execInBackend( script ):

    script = 'login %s\n%s' % ( os.path.join( root,
                                              'cloud',
                                              'beach',
                                              'sample_cli.conf' ),
                                script )

    with open( '_tmp_script', 'w' ) as f:
        f.write( script )

    ret = os.system( 'python %s --script _tmp_script' % ( os.path.join( root,
                                                                        'cloud',
                                                                        'beach',
                                                                        'hcp',
                                                                        'admin_cli.py' ), ) )
    os.unlink( '_tmp_script' )
    return ret

if arguments.genkeys:
    printStep( 'Clean old keys and generate a new set.',
                os.system( 'rm -rf %s' % os.path.join( root, 'keys', '*' ) ),
                os.system( 'python %s %s' % ( os.path.join( root, 'tools', 'generate_key.py' ),
                                              os.path.join( root, 'keys', 'c2' ) ) ),
                os.system( 'python %s %s' % ( os.path.join( root, 'tools', 'generate_key.py' ),
                                              os.path.join( root, 'keys', 'hbs_root' ) ) ),
                os.system( 'python %s %s' % ( os.path.join( root, 'tools', 'generate_key.py' ),
                                              os.path.join( root, 'keys', 'root' ) ) ),
                os.system( '%s %s %s "-pass pass:letmein"' % ( os.path.join( root, 'tools', 'encrypt_key.sh' ),
                                                               os.path.join( root, 'keys', 'hbs_root.priv.der' ),
                                                               os.path.join( root, 'keys', 'hbs_root.priv.enc' ) ) ) )

printStep( 'Downloading prebuilt release sensor binaries.',
           os.chdir( binaryPath ),
           os.system( os.path.join( binaryPath, 'download_binaries.sh' ) ),
           os.chdir( cwd ) )

printStep( 'Adding enrollment rule to the cloud to enroll all sensors into the 1.1 range.',
    execInBackend( 'hcp_addEnrollmentRule -m ff.ff.ffffffff.fff.ff -o 1 -s 1' ) )

binaries = os.listdir( binaryPath )
for binary in binaries:
    if hcpConfig is not None:
        if binary.startswith( 'hcp_' ) and not binary.endswith( '.sig' ):
            printStep( 'Setting HCP to config: %s' % hcpConfig,
                       os.system( 'python %s %s %s' % ( os.path.join( root, 'sensor', 'scripts', 'set_sensor_config.py' ),
                                                        hcpConfig,
                                                        os.path.join( binaryPath, binary ) ) ) )

    if hbsConfig is not None:
        if binary.startswith( 'hbs_' ) and not binary.endswith( '.sig' ):
            printStep( 'Setting HBS to config: %s' % hbsConfig,
                       os.system( 'python %s %s %s' % ( os.path.join( root, 'sensor', 'scripts', 'set_sensor_config.py' ),
                                                        hbsConfig,
                                                        os.path.join( binaryPath, binary ) ) ) )

    if ( binary.startswith( 'hbs_' ) or binary.startswith( 'kernel_' ) ) and not binary.endswith( '.sig' ):
        printStep( 'Signing binary: %s' % binary,
            os.system( 'python %s -k %s -f %s -o %s' % ( os.path.join( root, 'tools', 'signing.py' ),
                                                         hcpRootKey,
                                                         os.path.join( binaryPath, binary ),
                                                         os.path.join( binaryPath, binary + '.sig' ) ) ) )

        if 'release' in binary:
            targetAgent = 'ff.ff.ffffffff.%s%s%s.ff'
            if 'x64' in binary:
                arch = 2
            elif 'x86' in binary:
                arch = 1
            if 'win' in binary:
                major = 1
                minor = 0
            elif 'osx' in binary:
                major = 2
                minor = 0
            elif 'ubuntu' in binary:
                major = 5
                minor = 4

            targetAgent = targetAgent % ( hex( arch )[ 2: ],
                                          hex( major )[ 2: ],
                                          hex( minor )[ 2: ] )

            with open( os.path.join( binaryPath, binary ) ) as f:
                h = hashlib.sha256( f.read() ).hexdigest()

            if binary.startswith( 'hbs_' ):
                printStep( 'Tasking HBS %s to all relevant sensors.' % binary,
                    execInBackend( '''hcp_addModule -i 2 -d %s -b %s -s %s
                                      hcp_addTasking -m %s -i 2 -s %s''' % ( binary,
                                                                             os.path.join( binaryPath, binary ),
                                                                             os.path.join( binaryPath, binary + '.sig' ),
                                                                             targetAgent,
                                                                             h ) ) )
            elif binary.startswith( 'kernel_' ):
                printStep( 'Tasking KERNEL %s to all relevant sensors.' % binary,
                           execInBackend( '''hcp_addModule -i 5 -d %s -b %s -s %s
                                             hcp_addTasking -m %s -i 5 -s %s''' % ( binary,
                                                                                    os.path.join( binaryPath, binary ),
                                                                                    os.path.join( binaryPath, binary + '.sig' ),
                                                                                    targetAgent,
                                                                                    h ) ) )

printStep( 'Setting HBS profile.',
           execInBackend( '''hbs_addProfile -m ff.ff.ffffffff.fff.ff -f %s''' % ( os.path.join( root,
                                                                                                'cloud',
                                                                                                'beach',
                                                                                                'production_hbs.profile' ) ) ) )
