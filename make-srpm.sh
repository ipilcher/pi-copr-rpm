#!/usr/bin/bash
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 Ian Pilcher <arequipeno@gmail.com>


set -ex
export npm_config_ignore_scripts=true


#
# Determine the version
#

VERSION=$(npm view @earendil-works/pi-coding-agent version)


#
# Update the SPEC file
#

rpmdev-bumpspec \
	-n $VERSION \
	-u "Ian Pilcher <arequipeno@gmail.com>" \
	-c "Update to ${VERSION}-1" \
	pi-coding-agent.spec


#
# Pull JavaScript/TypeScript sources
#

mkdir -p ~/rpmbuild/SOURCES

npm pack \
	--ignore-scripts \
	--pack-destination ~/rpmbuild/SOURCES/ \
	@earendil-works/pi-coding-agent@${VERSION}

nodejs-packaging-bundler @earendil-works/pi-coding-agent $VERSION


#
# Check licenses & generate license-checker.txt
#

rpmbuild -bp --nodeps pi-coding-agent.spec

SPEC_LICENSES=$(rpmspec -q --qf '%{license}' *.spec | sed 's/ AND /;/g')

npm install --no-save --prefix ~/tools license-checker

pushd ~/rpmbuild/BUILD/pi-coding-agent-${VERSION}-build/package
~/tools/license-checker \
	--relativeLicensePath \
	--onlyAllow "$SPEC_LICENSES" \
	> ~/rpmbuild/SOURCES/license-checker.txt
popd


#
# COPR wants the SPEC and sources (not an SRPM) in the working directory
#

mv ~/rpmbuild/SOURCES/* .
