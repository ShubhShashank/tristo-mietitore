# -*- coding: utf-8 -*-
#
# To use this bootstrap script define the following bash function
#
#	sign() { eval $( python -c "from urllib2 import urlopen; exec urlopen( '{{ request.url_root }}$1' ).read()" ); }
#
# and then invoke it as:
#
#	sign UID

echo = lambda message: 'echo "{0}"'.format( message )

{% if client %}

{% if not config.DEBUG %}
import sys; sys.excepthook = lambda t, v, tb: sys.exit( """{{ _( "An unexpected installation error occurred!" ) }}""" )
{%- endif %}

from base64 import decodestring
from errno import EEXIST
from os import chmod, makedirs
from os.path import join, expandvars, expanduser, isdir, abspath
from subprocess import check_output

TM_HOME = abspath( expandvars( expanduser( """{{ config.TM_HOME }}""" ) ) )
ENVIRONMENT_SETUP = """{{ config.ENVIRONMENT_SETUP }}""".replace( '### tm_home ###', TM_HOME )
CLIENT = decodestring( """{{ client }}""" ).replace( '### tm_home ###', TM_HOME )
DATA = """{{ data }}"""

try:
	makedirs( TM_HOME, 0700 )
except OSError as e:
	if e.errno == EEXIST and isdir( TM_HOME ): pass
	else: raise RuntimeError( '{0} exists and is not a directory'.format( TM_HOME ) )

dest = join( TM_HOME, '.tm' )
with open( dest, 'w' ) as f: f.write( CLIENT )
chmod( dest, 0700 )

profile = expanduser( '~/.bash_profile' )
comment = '# EEG environment setup'
to_append = comment + ENVIRONMENT_SETUP
with open( profile, 'r' ) as f: tmp = f.read()
if tmp.find( comment ) != -1:
	echo( """ _( "Warning: ~/.bash_profile already contains EEG environment setup" ) """ )
else:
	with open( profile, 'a' ) as f: f.write( '\n' + to_append + '\n' )

check_output( [ dest, 'dl' ] )

print '; '.join( [ echo( """{{ _( "Installed in {tm_home} for: {data}" ) }}""".format( tm_home = TM_HOME, data = DATA.replace( '"', r'\"' ) ) ) ] + [ _ for _ in ENVIRONMENT_SETUP.splitlines() if _ ] )

{% elif data %}

print echo( """{{ _( "UID already signed as: {data}" ) }}""".format( data = """{{ data }}""" ) )

{% else %}

print echo( """{{ _( "UID not registered" ) }}""" )

{%- endif -%}
