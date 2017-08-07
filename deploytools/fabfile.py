from fabric.contrib.files import append, exists, sed
from fabric.api import env, local, run
import random

REPO_URL = 'https://github.com/eliasvc/superlists.git'

def _create_directory_structure_if_necessary(site_folder):
	for subfolder in ('database', 'static', 'virtualenv', 'source'):
		# run will basically run the shell command in the server
		run('mkdir -p {site_folder}/{subfolder}'.format(
													site_folder=site_folder, 
													subfolder=subfolder
												)
		)

def _get_latest_source(source_folder):
	if exists(source_folder + '/.git'):
		run('cd {source_folder} && git fetch'.format(source_folder=source_folder))
	else:
		run('git clone {repo} {source_folder}'.format(repo=REPO_URL, source_folder=source_folder))
	# local() will run the command in your local machine. capture determines if the output is
	# printed to the screen or if its returned. True means it is returned.
	# git log -n 1 --format=%H will get the last commit hash 
	current_commit = local('git log -n 1 --format=%H', capture=True)
	run('cd {source_folder} && git reset --hard {commit}'.format(
															source_folder=source_folder,
															commit=current_commit
														)
	)

def _update_settings(source_folder, site_name):
	settings_path = source_folder + '/superlists/settings.py'
	sed(settings_path, "DEBUG = True", "DEBUG = False")
	sed(settings_path,
		'ALLOWED_HOSTS =.+$',
		'ALLOWED_HOSTS = ["{site_name}"]'.format(site_name=site_name)
	)
	# The secret key is used buy Django to generate its crypto things. It is a good idead to have
	# a different one on the live server than the one in development since dev code might be
	# open to the public (public repos in GitHub for example)
	secret_key_file = source_folder + '/superlists/secret_key.py'
	if not exists(secret_key_file):	
		chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
		# The _ in the for loop basically ignores the values obtained in range.
		key = ''.join(random.SystemRandom().choice(chars) for _ in range(50))
		append(secret_key_file, 'SECRET_KEY = "{key}"'.format(key=key))
	# Fabric's append will only add the text if is not found in the file
	append(settings_path, '\nfrom .secret_key import SECRET_KEY')

def _update_virtual_env(source_folder):
	virtualenv_folder = source_folder + '/../virtualenv'
	if not exists(virtualenv_folder + '/bin/pip'):
		run('python3.6 -m venv {virtualenv_folder}'.format(virtualenv_folder=virtualenv_folder))
	run(
		'{virtualenv_folder}/bin/pip install -r' 
		' {source_folder}/requirements.txt'.format(
												virtualenv_folder=virtualenv_folder,
												source_folder=source_folder
											)
	)

def _update_static_files(source_folder):
	run(
		'cd {source_folder}'
		' && ../virtualenv/bin/python manage.py collectstatic --noinput'.format(
																			source_folder=source_folder
																		)
	)

def _update_database(source_folder):
	run(
		'cd {source_folder}'
		' && ../virtualenv/bin/python manage.py migrate --noinput'.format(source_folder=source_folder)
	)

def deploy():
	site_folder = '/home/{user}/sites/{host}'.format(user=env.user, host=env.host)
	source_folder = site_folder + '/source'
	_create_directory_structure_if_necessary(site_folder)
	_get_latest_source(source_folder)
	_update_settings(source_folder, env.host)
	_update_virtual_env(source_folder)
	_update_static_files(source_folder)
	_update_database(source_folder)

