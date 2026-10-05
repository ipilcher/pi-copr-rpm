## START: Set by rpmautospec
## (rpmautospec version 0.8.4)
## RPMAUTOSPEC: autorelease, autochangelog
%define autorelease(e:s:pb:n) %{?-p:0.}%{lua:
    release_number = 1;
    base_release_number = tonumber(rpm.expand("%{?-b*}%{!?-b:1}"));
    print(release_number + base_release_number - 1);
}%{?-e:.%{-e*}}%{?-s:.%{-s*}}%{!?-n:%{?dist}}
## END: Set by rpmautospec

%global npm_name @earendil-works/pi-coding-agent

# esbuild RPMs must match what Pi bundles
%global sys_esbuild_ver 0.28.2

Name:           pi-coding-agent
Version:        1.0.1
Release:        1%{?dist}
Summary:        An open source coding agent

License:        MIT AND Apache-2.0 AND BSD-2-Clause AND BSD-3-Clause AND ISC AND BlueOak-1.0.0 AND 0BSD AND CC-BY-SA-4.0 AND CC0-1.0 AND Unlicense
# To add a LICENSE file to the project
# https://github.com/badlogic/pi-mono/issues/4215
# MIT is mentioned in the README.md
#
# see license-checker.txt for a breakdown of the depend projects
URL:            https://github.com/earendil-works/pi
# npm pack @earendil-works/pi-coding-agent
Source0:        earendil-works-pi-coding-agent-%{version}.tgz
# nodejs-packaging-bundler @earendil-works/pi-coding-agent <version>
Source1:        @earendil-works-pi-coding-agent-%{version}-nm-prod.tgz
Source2:        @earendil-works-pi-coding-agent-%{version}-bundled-licenses.txt

# npm i -g license-checker
# (in installed rpm dir run) license-checker 
Source10:       license-checker.txt

BuildArch:      noarch

Requires:       nodejs24-full-i18n
Requires:       nodejs-esbuild = %{sys_esbuild_ver}
BuildRequires:  nodejs24-devel
BuildRequires:  fdupes
BuildRequires:  nodejs-esbuild = %{sys_esbuild_ver}
BuildRequires:  jq

%description
Pi is a minimal terminal coding harness. Adapt pi to your workflows,
not the other way around, without having to fork and modify pi internals.
Extend it with TypeScript Extensions, Skills, Prompt Templates, and
Themes. Put your extensions, skills, prompt templates, and themes in Pi
Packages and share them with others via npm or git.

Pi ships with powerful defaults but skips features like sub agents and
plan mode. Instead, you can ask pi to build what you want or install a
third party pi package that matches your workflow.

Pi runs in four modes: interactive, print or JSON, RPC for process
integration, and an SDK for embedding in your own apps.
See openclaw/openclaw for a real-world SDK integration.

%prep
%setup -q -n package

cp -p %{SOURCE2} %{name}-%{version}-bundled-licenses.txt

tar xfz %{SOURCE1}
mkdir -p node_modules
pushd node_modules
ln -s ../node_modules_prod/* .
ln -s ../node_modules_prod/.bin .
popd

# Strip out examples
rm -rf examples

# remove zero length files
find . -size 0 -type f -print0 | xargs -0 rm -f

# remove hidden things
# pi-coding-agent.noarch: W: hidden-file-or-dir /usr/lib/node_modules/
#  @mariozechner/pi-coding-agent/node_modules_prod/socks/.eslintrc.cjs
N=".bin .claude .editorconfig .eslintrc .eslintrc.cjs .eslintrc.js .eslintignore .github \
   .gitkeep .history .keep .jscs.json .jshintrc .npmignore .nvmrc \
   .package-lock.json .prettierignore .prettierrc .prettierrc.json .prettierrc.yaml .travis.yml"
for n in $N; do
    find . -name ${n} -print0 | xargs -0 rm -rf
done

# remove devel things
# pi-coding-agent.noarch: W: devel-file-in-non-devel-package /usr/lib/node_modules/
#   @mariozechner/pi-coding-agent/node_modules_prod/@tootallnate/quickjs-emscripten/c/interface.c
find . -name 'interface.c' -print0 | xargs -0 rm -rf

# remove some binaries
PI_ESBUILD_VER="$(jq -r .version node_modules_prod/esbuild/package.json)"
if [ "$PI_ESBUILD_VER" != "%{sys_esbuild_ver}" ]; then
    echo "ERROR: esbuild version mismatch"
    echo "    Pi requires version $PI_ESBUILD_VER"
    echo "    System version is %{sys_esbuild_ver}"
    exit 1
fi
rm -rf node_modules_prod/esbuild
rm -rf node_modules_prod/@earendil-works/pi-tui/native
rm -f node_modules_prod/@silvia-odwyer/photon-node/photon_rs_bg.wasm

# make some scripts executable
chmod a+x dist/bun/cli.d.ts
chmod a+x dist/bun/cli.js
chmod a+x dist/cli.d.ts
chmod a+x dist/rpc-entry.d.ts
chmod a+x node_modules_prod/@earendil-works/pi-ai/dist/cli.d.ts
chmod a+x node_modules_prod/marked/bin/main.js

# remove some execute permisions
chmod a-x node_modules_prod/@aws-sdk/types/package.json

%build
#nothing to do

%install
mkdir -p %{buildroot}%{nodejs_sitelib}/%{npm_name}
cp -pr * %{buildroot}%{nodejs_sitelib}/%{npm_name}/

mkdir -p %{buildroot}%{_bindir}
pushd %{buildroot}%{_bindir}
ln -s ../lib/node_modules/%{npm_name}/dist/cli.js pi
popd

# cleanup dupes
%fdupes %{buildroot}

%files
%license README.md %{name}-%{version}-bundled-licenses.txt
%doc README.md
%dir %{nodejs_sitelib}/@earendil-works
%{nodejs_sitelib}/%{npm_name}
%{_bindir}/pi

%changelog
* Sat Oct 3 2026 Ian Pilcher <arequipeno@gmail.com> - 1.0.1-1
- Update to 1.0.1-1

* Fri Oct 2 2026 Ian Pilcher <arequipeno@gmail.com> - 1.0.0-1
- Update to 1.0.0-1

* Wed Sep 30 2026 Ian Pilcher <arequipeno@gmail.com> - 0.99.2-1
- Update to 0.99.2

* Tue Sep 29 2026 Ian Pilcher <arequipeno@gmail.com> - 0.99.1-1
- Update to 0.99.1

* Tue Sep 22 2026 Ian Pilcher <arequipeno@gmail.com> - 0.87.0-1
- Update to 0.87.1

* Mon Sep 21 2026 Ian Pilcher <arequipeno@gmail.com> - 0.86.1-1
- Update to 0.86.1
- Force use of NodeJS 24
- Change dependency from nodejs to nodejs24-full-i18n
- Use system esbuild packages

## START: Generated by rpmautospec
* Tue Aug 18 2026 Tom Rix <Tom.Rix@amd.com> - 0.84.2-1
- Update to 0.84.2

* Thu Jul 16 2026 Fedora Release Engineering <releng@fedoraproject.org> - 0.80.3-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_45_Mass_Rebuild

* Thu Jul 09 2026 Tom Rix <Tom.Rix@amd.com> - 0.80.3-3
- Remove Unlicense

* Thu Jul 09 2026 Tom Rix <Tom.Rix@amd.com> - 0.80.3-2
- Update license-checker output

* Thu Jul 09 2026 Tom Rix <Tom.Rix@amd.com> - 0.80.3-1
- Initial package
## END: Generated by rpmautospec
