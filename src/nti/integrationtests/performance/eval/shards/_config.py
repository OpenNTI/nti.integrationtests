from __future__ import print_function, unicode_literals

# avoid monkey patching
import gevent
setattr( gevent, 'version_info', (0,) )

import os
import tempfile
import ConfigParser

from nti.dataserver.config import write_configs 
from nti.integrationtests.utils import get_int_option

def get_port(config):	
	ini = ConfigParser.SafeConfigParser()
	ini.read(config)
	config_port = get_int_option(ini, name='http_port', default=8081)
	return config_port

def write_pserve_config(config,
						port=8081,
						workers=1,
						out_dir=None):

	config = os.path.expanduser(config)
	if not os.path.exists(config):
		raise OSError('No pserve file %s' % config)

	ini = ConfigParser.SafeConfigParser()
	ini.read(config)
	
	config_port = get_int_option(ini, name='http_port', default=8081)
	config_workers = get_int_option(ini, section='server:main', name='workers', default=1)
	
	if config_port != port:
		ini.set('DEFAULT', 'http_port', str(port))
	
	if config_workers != workers:
		ini.set('server:main', 'workers', str(workers))
	
	out_dir = out_dir or tempfile.mkdtemp(prefix="ntids.", dir="/tmp")
	if not os.path.exists(out_dir):
		os.makedirs(out_dir)

	name = os.path.basename(config)
	config = os.path.join(out_dir, name)
	with open(config, "wb") as fp:
		ini.write(fp)
	
	return config

def write_relstorage_config(out_dir,
							shards=4,
							db_user='Users',
							db_pwd='Users',
							db_socket=None, #'/opt/local/var/run/mysql55/mysqld.sock',
							db_host='localhost',
							db_prefix='Users',
							cache_servers='localhost:11211'):
	
	if not os.path.exists(out_dir):
		os.makedirs(out_dir)
			
	template_1 = """
		<zodb %(db_name)s>
			pool-size 7
			database-name %(db_name)s
			<relstorage %(db_name)s>
				cache-servers %(cache_servers)s
				cache-prefix %(db_name)s
				poll-interval 0
				commit-lock-timeout 30
				keep-history false
				pack-gc false
				<mysql>
					db %(db_name)s
					user %(db_user)s
					passwd %(db_pwd)s
	"""

	template_2 ="""\t\t\t\tunix_socket %(db_socket)s
				</mysql>
		 	</relstorage>
		</zodb>
	"""
	
	template_3 ="""\t\t\t\thost %(db_host)s
				</mysql>
		 	</relstorage>
		</zodb>
	"""
	
	template = template_1 + template_2 if db_socket else template_1 + template_3
	zeo_conf_config = ["""
		%import relstorage
		%import zc.zlibstorage
	"""]
	zeo_uri_config = ["[ZODB]\nuris ="]
	for x in range(0, shards+1):
		# conf
		db_name = db_prefix if x == 0 else db_prefix + "_" + str(x)
		params = dict(locals())
		params['db_name'] = db_name
		s = template % params
		zeo_conf_config.append(s)
		
		# uri
		zeo_uri_config.append("zconfig://%s/zeo_conf.xml#%s" % (out_dir, db_name.lower()))
	
	# time to save
	name = os.path.join(out_dir, "zeo_conf.xml")
	zeo_conf_config = ''.join(zeo_conf_config)
	with open(name, "w") as tgt:
		tgt.write(zeo_conf_config)
	
	zeo_uri_config = ' '.join(zeo_uri_config)
	name = os.path.join(out_dir, "zeo_uris.ini")
	with open(name, "w") as tgt:
		tgt.write(zeo_uri_config)
		tgt.write("\n")
		
def get_default_config():
	config = os.path.join(os.path.dirname(__file__), "development.ini")
	return config

def write_base_configs(root_dir, config):
	# write base confi from the server
	write_configs(root_dir, config, update_existing=True, write_supervisord=True)
	
	def _remove_sections(sconf):
		if os.path.exists(sconf):
			ini = ConfigParser.SafeConfigParser()
			ini.read(sconf)
			ini.remove_section('program:zeo')
			ini.remove_section('program:nti_sharing_listener')
			ini.remove_section('program:nti_index_listener')
			with open(sconf, "wb") as fp:
				ini.write(fp)
			
	_remove_sections(os.path.join(os.path.join(root_dir, 'etc'), 'supervisord.conf'))
	_remove_sections(os.path.join(os.path.join(root_dir, 'etc'), 'supervisord_dev.conf'))
	_remove_sections(os.path.join(os.path.join(root_dir, 'etc'), 'supervisord_demo.conf'))

def prepare(port=8081, workers=1, shards=4, config=None, out_dir=None):
	out_dir = out_dir or tempfile.mkdtemp(prefix="ntids.", dir="/tmp")
	etc_dir = os.path.join(out_dir, 'etc')
	config = config or get_default_config()
	
	# write pserve config
	config = write_pserve_config(config, port, workers, out_dir=etc_dir)
	
	# write base confi from the server
	write_base_configs(out_dir, config)
	
	# overide
	write_relstorage_config(etc_dir, shards=shards)
	
	return config

if __name__ == '__main__':
	prepare(out_dir='/tmp')
	