#!/usr/bin/env python

import sys
def _excepthook( t, v, tb ):
		tb = extract_tb( tb )[ -1 ]
		f = tb[ 0 ].split( '/' )[ -1 ]
		l = tb[ 1 ]
		e = format_exception_only( t, v )[ -1 ].strip()
		sys.exit( '[{0}:{1}] {2}'.format( f, l, e ) )
sys.excepthook = _excepthook

from base64 import encodestring, decodestring
from io import BytesIO
from os import walk, stat
from os.path import join, abspath, isdir
from re import compile as recompile
from tarfile import TarFile
from traceback import extract_tb, format_exception_only
from urllib import urlencode
from urllib2 import urlopen

DATA = '{{ data }}'
SIGNATURE = '{{ signature }}'
BASE_URL = '{{ request.url_root }}'
EEG_HOME = '$eeg_home'

MAX_FILESIZE = 10 * 1024
MAX_NUM_FILES = 1024

def tar( dir = '.', glob = '.*', verbose = True ):
	if not isdir( dir ): raise ValueError( '{0} is not a directory'.format( dir ) )
	dir = abspath( dir )
	glob = recompile( glob )
	buf = BytesIO()
	tf = TarFile.open( mode = 'w', fileobj = buf )
	offset = len( dir ) + 1
	num_files = 0
	for base, dirs, files in walk( dir, followlinks = True ):
		if num_files > MAX_NUM_FILES: break
		for fpath in files:
			path = join( base, fpath )
			rpath = path[ offset: ]
			if glob.search( rpath ) and stat( path ).st_size < MAX_FILESIZE:
				num_files += 1
				if num_files > MAX_NUM_FILES: break
				if verbose: sys.stderr.write( rpath + '\n' )
				with open( path, 'r' ) as f:
					ti = tf.gettarinfo( arcname = rpath, fileobj = f )
					tf.addfile( ti, fileobj = f )
	tf.close()
	return encodestring( buf.getvalue() )

def untar( data, dir = '.' ):
	f = BytesIO( decodestring( data ) )
	tf = TarFile.open( mode = 'r', fileobj = f )
	tf.extractall( dir )
	tf.close()

def upload_tar( glob = '.*', dir = '.' ):
	conn = urlopen( BASE_URL, urlencode( {
		'signature': SIGNATURE,
		'tar': tar( join( EEG_HOME, dir ), glob, False )
	} ) )
	ret = conn.read()
	conn.close()
	return ret

def download_tar():
	conn = urlopen( BASE_URL, urlencode( { 'signature': SIGNATURE } ) )
	untar( conn.read(), EEG_HOME )
	conn.close()
	return ''

if __name__ == '__main__':
	try:
		_, verb = sys.argv.pop( 0 ), sys.argv.pop( 0 )
		dispatch = {
			'_t': tar,
			'ul': lambda *args: upload_tar( *args ),
			'dl': lambda *args: download_tar(),
			'id': lambda *args: DATA
		}
		res = dispatch[ verb ]( *sys.argv )
		if res: print res
	except KeyError:
		sys.exit( 'wrong verb' )
	except IndexError:
		sys.exit( 'wrong number of args' )
