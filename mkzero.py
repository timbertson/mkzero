#!/usr/bin/env python
import os
import sys
import subprocess
import time
from optparse import OptionParser

opts = None

def main():
	global opts
	parser = OptionParser("Usage: %prog [options] -v version -n URI xmlfile")
	parser.add_option("-v", "--version", default=None, help="version (REQUIRED)")
	parser.add_option("-n", "--namespace", default=None, help="namespace (URI - REQUIRED)")

	parser.add_option("-p", "--path", action='append', dest='paths', default=[], help="file/directory to publish (defaults to basename of xml file)")
	parser.add_option("-x", "--extract", default=None, help="extract path (within archive)")
	parser.add_option("-b", "--build", default="0inst", help="build dir (for tarballs)")
	parser.add_option("-d", "--dest", dest="dest", default=None, help="directory to copy published artifacts (signed xml and tgz)")

	parser.add_option("-V", "--verbose", default=False, action='store_true', help="verbose")
	parser.add_option("-f", "--force", default=False, action='store_true')

	parser.add_option("-a", "--artifact", default=None, help="artifact (ignores --path and --build)")
	parser.add_option("-c", "--copy-only", dest='copy_only', action="store_true", help="copy to --publish-to only (don't build or add archive)")
	parser.add_option("-e", "--edit", default=False, action='store_true', help="edit the xml directly")
	parser.add_option("-r", "--replace", default=False, action='store_true', help="replace existing version <implmentation>")

	opts, args = parser.parse_args()
	if len(args) != 1:
		parser.print_help()
		sys.exit(1)
	if opts.namespace and not opts.namespace.endswith('/'):
		opts.namespace += '/'
	opts.filename = args[0]
	opts.pkg = os.path.splitext(opts.filename)[0]
	opts.localzip = None
	if not opts.version:
		if not (opts.copy_only or opts.edit):
			ensure_version()
	if opts.version=='date':
		opts.version=time.strftime("%Y%m%d.%H%M")
		print "version: %s" % (opts.version,)
	if len(opts.paths) == 1 and isarchive(opts.paths[0]):
		opts.localzip = opts.paths[0]
		opts.artifact = opts.namespace + opts.pkg + '/' + os.path.basename(opts.localzip)
		opts.buildzip = False
	if opts.version and not opts.artifact:
		zipname = "%s-%s.tgz" % (opts.pkg, opts.version)
		opts.localzip = os.path.join(opts.build, zipname)
		opts.artifact = opts.namespace + opts.pkg + '/' + zipname
		opts.buildzip = True
	try:
		run()
	except AssertionError, e:
		print >> sys.stderr, "ERROR: %s" % (e,)
		parser.print_help()
	except Exception, e:
		print >> sys.stderr, "Error: %s" % (e,)
		if opts.verbose: raise
		sys.exit(2)

def isarchive(filename):
	"""
	>>> isarchive("foo.tgz")
	True
	>>> isarchive("foo.tar.gz")
	True
	>>> isarchive("foo.tar.Gz")
	True
	>>> isarchive("foo")
	False
	"""
	return os.path.splitext(filename)[-1].lower() in ('.tgz', '.gz', '.zip')

def ensure_version():
	version_suggestion = ''
	try:
		with open('VERSION') as version_file:
			version_suggestion = version_file.read().strip()
	except StandardError: pass
	version_response = raw_input('version? [%s] ' % version_suggestion).strip()
	if len(version_response) == 0:
		opts.version = version_suggestion
	else:
		opts.version = version_response
	assert opts.version, "version required!"

def run():
	assert opts.namespace is not None, "namespace required!"
	set_interface()
	if not (opts.copy_only or opts.edit):
		mk_zip()
		edit_xml()
	if opts.edit:
		pub(opts.filename, 'edit')
	if opts.dest:
		artifact_dir = os.path.join(opts.dest, opts.pkg)
		mkdir(artifact_dir)
		if opts.localzip:
			cp(opts.localzip, artifact_dir)
		cp(opts.filename, opts.dest)
		sign(os.path.join(opts.dest, opts.filename))

def set_interface():
	pub(opts.filename, set_interface_uri=(opts.namespace + opts.filename))

def edit_xml():
	kwargs = dict(archive_url=opts.artifact, set_released='today')
	if '://' not in opts.artifact:
		kwargs['archive_file'] = opts.artifact
	if opts.localzip:
		kwargs['archive_file'] = opts.localzip
	if opts.extract:
		kwargs['archive_extract'] = opts.extract
	version_key = 'set_version' if opts.replace else 'add_version'
	kwargs[version_key] = opts.version
	pub(opts.filename, **kwargs)

def mk_zip():
	if not (opts.localzip and opts.buildzip):
		print "not making zip"
		return
	source_dirs = opts.paths or [opts.pkg]
	output_dir = opts.build
	version = opts.version
	mkdir(output_dir)
	if os.path.exists(opts.localzip):
		delete = opts.force or raw_input("%s exists. overwrite it? [y/N] " % (opts.localzip,)).lower() == 'y'
		if delete:
			c('rm', '-f', opts.localzip)
		else:
			sys.exit(1)
	c('tar', 'zcf', opts.localzip, '--exclude-vcs', *source_dirs)

def sign(xml):
	pub(xml, 'xmlsign')

def mkdir(d): c('mkdir', '-p', d)
def cp(s, d): c('cp', s, d)
def pub(file, *args, **kwargs):
	a = []
	for arg in args:
		a.append('--%s' % (arg,))
	for k,v in kwargs.items():
		a.append('--%s=%s' % (k.replace('_','-'),v))
	c('0publish', file, *a)

def c(*a):
	if opts.verbose:
		print "# " + ' '.join(a)
	return subprocess.check_call(a)

if __name__ == '__main__':
	main()
