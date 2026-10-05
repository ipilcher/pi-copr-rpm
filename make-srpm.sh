#!/usr/bin/bash
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 Ian Pilcher <arequipeno@gmail.com>


set -ex


#
# Install tools required to build SRPM
#

dnf -y install \
	rpm-build \
	rpmdevtools \
	nodejs24-npm-bin \
	nodejs-packaging-bundler \
	jq \
	sed

npm install -g license-checker


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

exit 0


#
# Check licenses & generate license-checker.txt
#

rpmbuild -bp --nodeps pi-coding-agent.spec

SPEC_LICENSES=$(rpmspec -q --qf '%{license}' *.spec | sed 's/ AND /;/g')

pushd ~/rpmbuild/BUILD/pi-coding-agent-1.0.3-build/package
license-checker \
	--relativeLicensePath \
	--onlyAllow "$SPEC_LICENSES" \
	> ~/rpmbuild/SOURCES/license-checker.txt
popd


#
# COPR wants the SPEC and sources (not an SRPM) in the working directory
#

mv ~/rpmbuild/SOURCES/* .
