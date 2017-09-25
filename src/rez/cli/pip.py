"""
Install a pip-compatible python package, and its dependencies, as rez packages.
"""


def setup_parser(parser, completions=False):
    parser.add_argument(
        "--pip-version", dest="pip_ver", metavar="VERSION",
        help="pip version (rez package) to use, default is latest")
    parser.add_argument(
        "--python-version", dest="py_ver", metavar="VERSION",
        help="python version (rez package) to use, default is latest. Note "
        "that the pip package(s) will be installed with a dependency on "
        "python-MAJOR.MINOR.")
    parser.add_argument(
        "-i", "--install", action="store_true",
        help="install the package")
    parser.add_argument(
        "--ignore-installed", action="store_true",
        help="ignore installed packages")
    parser.add_argument(
        "-s", "--search", action="store_true",
        help="search for the package on PyPi")
    parser.add_argument(
        "-r", "--release", action="store_true",
        help="install as released package; if not set, package is installed "
        "locally only")
    parser.add_argument(
        "--variant", dest="variant",
        help="Specify the variant requirements for package "
        " default=platform,arch,os")
    parser.add_argument(
        "--build-requires", nargs='+',
        help="packages to use for installation environment and add them to build_requires.")
    parser.add_argument(
        "--requires", nargs='+',
        help="packages to use for installation environment and add them to requires.")
    parser.add_argument(
        "PACKAGES", nargs='+',
        help="package to install or archive/url to install from")


def command(opts, parser, extra_arg_groups=None):
    from rez.pip import pip_install_package, run_pip_command
    import sys

    if not (opts.search or opts.install):
        parser.error("Expected one of: --install, --search")

    if opts.search:
        p = run_pip_command(["search", opts.PACKAGE])
        p.wait()
        return

    installed_variants = set()
    skipped_variants = set()
    failed_variants = set()

    for package in opts.PACKAGES:
        try:
            installed, skipped = pip_install_package(
                package,
                pip_version=opts.pip_ver,
                python_version=opts.py_ver,
                release=opts.release,
                default_variant=opts.variant,
                build_requires=opts.build_requires,
                requires=opts.requires,
                ignore_installed=opts.ignore_installed)
            if installed is not None:
                installed_variants.update(installed)
            if skipped is not None:
                skipped_variants.update(skipped)
        except Exception as e:
            print "Package", package, "failed to install"
            raise

    def print_variant(v):
        pkg = v.parent
        txt = "%s: %s" % (pkg.qualified_name, pkg.uri)
        if v.subpath:
            txt += " (%s)" % v.subpath
        print "  " + txt

    print
    if installed_variants:
        print "%d packages were installed:" % len(installed_variants)
        for variant in installed_variants:
            print_variant(variant)
    else:
        print "NO packages were installed."

    if skipped_variants:
        print
        print "%d packages were already installed:" % len(skipped_variants)
        for variant in skipped_variants:
            print_variant(variant)

    if failed_variants:
        print
        print "%d packages failed to install:" % len(failed_variants)
        for variant in failed_variants:
            print "  " + variant[0], type(variant[1]), variant[1]


# Copyright 2013-2016 Allan Johns.
#
# This library is free software: you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library.  If not, see <http://www.gnu.org/licenses/>.
