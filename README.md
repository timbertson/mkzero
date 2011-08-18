mkzero is a wrapper around 0publish to make publishing and updating
zero install feeds simple.

It's sort of like a lightweight version of [0release]. But while
0release requires VCS integration and a releases directory and
tags a handful of build steps, `mkzero` requires very little,
and allows you to quickly publish new versions of your feeds.

It's designed so that you can have your own alias to it,
specifying as much default information as is reasonable. For
example, the author uses the following alias:

	alias mkzero-gfxmonk='0launch \
		http://gfxmonk.net/dist/0install/mkzero.xml \
		--namespace="http://gfxmonk.net/dist/0install" \
		--dest="$HOME/Sites/gfxmonk/dist/0install"'

Given this alias, often the only required invocation is:

	version +
	mkzero-gfxmonk feed-name.xml

To increment the current project's version number, create an
artifact, add it to the feed file, sign it with my GPG key and
copy it to the build directory of my website (which another
script will rsync to the remote server).

(The `version` command above refers to
http://gfxmonk.net/dist/0install/version.xml )

### Required information:

**URI**:

Obviously, your feed needs an interface URI. This should not
change between invocations. If you don't want to provide the
full URI, you can use the `--namespace` argument to provide
the base URI, and your feed's filename will be appended to get
the full URI.

**version**:

If not given, this is assumed to be the contents of the
`VERSION` file in the current directory. If `mkzero` uses this
default, you will be prompted to accept the suggested version
number.

If `$build/feed-name-$version.tgz` already exists, you will
be prompted to overwrite it.

If version is "date", `mkzero` will generate a version of the
form: "YYYYMMDD.HHMM"

**path(s)**:

The paths to include in your artifact (.tgz). You can use
`--path` multiple times to include multiple top-level files or
directories. If not given, the basename of your feed file is
assumed to be the single file or directory to include (i.e for
foo.xml, it would assume that only "foo" is to go in the
artifact).

### Paths used by mkzero:

**0inst/**

mkzero assumes a build directory of 0inst/ for placing the
generated .tgz files. You can pass --build or -b to change
this default.

### Optional information:

**dest**:
If supplied, mkzero will copy the following files into `dest`:

 - _feed-name_.xml -> `$dest`/
 - `$build`/_feed-name_-`$version`.tgz -> `$dest`/_feed-name_/

After copying the feed xml file, mkzero will sign it with your
default GPG key in order to enable remote execution.

--------

For full usage, see `mkzero --help`
