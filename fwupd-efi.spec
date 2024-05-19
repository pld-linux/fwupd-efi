# TODO: genpeimg (from mingw-w64-tools?)
#
# Conditional build:
%bcond_with	pesign	# sign EFI binary (pesign is NFY)

Summary:	Firmware update EFI binaries
Summary(pl.UTF-8):	Binaria EFI do uaktualniania firmware'u
Name:		fwupd-efi
Version:	1.5
Release:	1
License:	LGPL v2+
Group:		Base
Source0:	https://people.freedesktop.org/~hughsient/releases/%{name}-%{version}.tar.xz
# Source0-md5:	0ad0080dae28a0a72b97237fc692bd22
URL:		https://github.com/fwupd/fwupd-efi
BuildRequires:	gnu-efi >= 1:3.0.15
BuildRequires:	meson >= 0.62.0
BuildRequires:	ninja >= 1.5
%{?with_pesign:BuildRequires:	pesign}
BuildRequires:	python3 >= 1:3.6
BuildRequires:	python3-pefile
BuildRequires:	python3-uswid >= 0.4.3
BuildRequires:	tar >= 1:1.22
BuildRequires:	xz
Requires:	fwupd >= 1.6.0
ExclusiveArch:	%{ix86} %{x8664} x32 %{arm} aarch64 loongarch64 riscv64
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		efi_arch	%(echo %{_target_base_arch} | sed -e 's/i386/ia32/;s/x86_64/x64/;s/aarch64/aa64/')

%define		_enable_debug_packages	0

%description
fwupd is a project to allow updating device firmware, and this package
provides the EFI binary that is used for updating using UpdateCapsule.

%description -l pl.UTF-8
fwupd to projekt pozwalający uaktualniać firmware urządzeń. Ten pakiet
dostarcza program binarny EFI służący do uaktualniania przy użyciu
UpdateCapsule.

%package devel
Summary:	Development file for fwupd-efi
Summary(pl.UTF-8):	Plik programistyczny pakietu fwupd-efi
Group:		Development/Libraries

%description devel
Development file for fwupd-efi.

Plik programistyczny pakietu fwupd-efi.

%prep
%setup -q

%ifarch x32
# -m64 is needed to build x64 EFI
%{__sed} -i -e "/^if host_cpu == 'x86_64'/,/^elif/ s/'-mno-red-zone',/& '-m64',/" efi/meson.build
%{__sed} -i -e 's/args\.cc, /&"-m64", /' efi/generate_sbat.py
%endif

%build
%meson build \
	-Defi-ldsdir=%{_libdir} \
	-Defi_sbat_distro_id="pld" \
	-Defi_sbat_distro_summary="PLD Linux" \
	-Defi_sbat_distro_pkgname="%{name}" \
	-Defi_sbat_distro_version="%{version}" \
	-Defi_sbat_distro_url="https://pld-linux.org/" \

%ninja_build -C build

%install
rm -rf $RPM_BUILD_ROOT

%ninja_install -C build

%if %{with pesign}
%pesign -s -i $RPM_BUILD_ROOT%{_libexecdir}/fwupd/efi/fwupd%{efi_arch}.efi \
	-o $RPM_BUILD_ROOT%{_libexecdir}/fwupd/efi/fwupd%{efi_arch}.efi.tmp
%pesign -s -i $RPM_BUILD_ROOT%{_libexecdir}/fwupd/efi/fwupd%{efi_arch}.efi.tmp \
	-o $RPM_BUILD_ROOT%{_libexecdir}/fwupd/efi/fwupd%{efi_arch}.efi.signed
%{__rm} $RPM_BUILD_ROOT%{_libexecdir}/fwupd/efi/fwupd%{efi_arch}.efi.tmp
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc AUTHORS COMMITMENT MAINTAINERS README.md SECURITY.md
%dir %{_libexecdir}/fwupd
%dir %{_libexecdir}/fwupd/efi
%{_libexecdir}/fwupd/efi/fwupd%{efi_arch}.efi
%if %{with pesign}
%{_libexecdir}/fwupd/efi/fwupd%{efi_arch}.efi.signed
%endif

%files devel
%defattr(644,root,root,755)
%{_pkgconfigdir}/fwupd-efi.pc
