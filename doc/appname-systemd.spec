Name: appname
Version: 1.0
Release: 1
Summary: appname
License: none
Vendor: zoosky
AutoProv: yes
AutoReq: yes
BuildRoot: /home/andreas/dev/sbtrpm/target/rpm/buildroot
BuildArch: noarch

%description
appname


%install
if [ -e "$RPM_BUILD_ROOT" ]; then
  mv "/home/andreas/dev/sbtrpm/target/rpm/tmp-buildroot"/* "$RPM_BUILD_ROOT"
else
  mv "/home/andreas/dev/sbtrpm/target/rpm/tmp-buildroot" "$RPM_BUILD_ROOT"
fi

%pre
# #######################################
# ## SBT Native Packager Bash Library  ##
# #######################################

# Adding system user
# $1 = user
# $2 = uid
# $3 = group
# $4 = description
# $5 = shell (defaults to /bin/false)
addUser() {
    user="$1"
    if [ -z "$user" ]; then
	echo "usage: addUser user [group] [description] [shell]"
	exit 1
    fi
    uid="$2"
    if [ -z "$uid" ]; then
	uid_flags=""
	  else
  uid_flags="--uid $uid"
    fi
    group=${3:-$user}
    descr=${4:-No description}
    shell=${5:-/bin/false}
    if ! getent passwd | grep -q "^$user:";
    then
	echo "Creating system user: $user in $group with $descr and shell $shell"
	useradd $uid_flags --gid $group -r --shell $shell -c "$descr" $user
    fi
}

# Adding system group
# $1 = group
# $2 = gid
addGroup() {
    group="$1"
    gid="$2"
    if [ -z "$gid" ]; then
	  gid_flags=""
  else
    gid_flags="--gid $gid"
  fi
    if ! getent group | grep -q "^$group:" ;
    then
	echo "Creating system group: $group"
	groupadd $gid_flags -r $group
    fi
}

# Will return true even if deletion fails
# $1 = user
deleteUser() {
    if hash deluser 2>/dev/null; then
	deluser --quiet --system $1 > /dev/null || true
    elif hash userdel 2>/dev/null; then
	userdel $1
    else
	echo "WARNING: Could not delete user $1 . No suitable program (deluser, userdel) found"
    fi
}

# Will return true even if deletion fails
# $1 = group
deleteGroup() {
    if hash delgroup 2>/dev/null; then
	delgroup --quiet --system $1 > /dev/null || true
    elif hash groupdel 2>/dev/null; then
	groupdel $1
    else
	echo "WARNING: Could not delete user $1 . No suitable program (delgroup, groupdel) found"
    fi
}

# #######################################


# Scriptlet syntax: http://fedoraproject.org/wiki/Packaging:ScriptletSnippets#Syntax
# $1 == 1 is first installation and $1 == 2 is upgrade
if [ $1 -eq 1 ] ;
then
    # Adding system user/group : appname and appname

    addGroup appname ""
    addUser appname "" appname "appname user-daemon" "/bin/false"
fi

if [ -e /etc/sysconfig/appname ] ;
then
  sed -i 's/PACKAGE_PREFIX\=.*//g' /etc/sysconfig/appname
fi

if [ -n "$RPM_INSTALL_PREFIX" ] ;
then
  echo "PACKAGE_PREFIX=${RPM_INSTALL_PREFIX}" >> /etc/sysconfig/appname
fi



%post
#
# Adding service to autostart
# $1 = service name
#
startService() {
    app_name=$1

    app_sys_config="/etc/sysconfig/${app_name}"
    [ -e "${app_sys_config}" ] && . "${app_sys_config}"
    if [ -n "${PACKAGE_PREFIX}" ] ;
    then
      default_install_location="/usr/share/appname"
      actual_install_location="${PACKAGE_PREFIX}/${app_name}"

      sed -i "s|$default_install_location|$actual_install_location|g" "/usr/lib/systemd/system/${app_name}.service"
    fi

    systemctl enable "$app_name.service"
    systemctl start "$app_name.service"
}

#
# Removing service from autostart
# $1 = service name
#

stopService() {
    app_name=$1

    systemctl stop "$app_name.service"
    systemctl disable "$app_name.service"
}

#
# Restarting the service after package upgrade
# $1 = service name
#
restartService() {
   app_name=$1

   systemctl daemon-reload
   systemctl try-restart "$app_name.service"
}



# Scriptlet syntax: http://fedoraproject.org/wiki/Packaging:ScriptletSnippets#Syntax
# $1 == 1 is first installation and $1 == 2 is upgrade

if [ $1 -eq 1 ] ;
then
  startService appname || echo "Could not start appname"
fi


relocateLink() {
  if [ -n "$4" ] ;
  then
    RELOCATED_INSTALL_DIR="$4/$3"
    echo "${1/$2/$RELOCATED_INSTALL_DIR}"
  else
    echo "$1"
  fi
}
rm -rf $(relocateLink /usr/share/appname/logs /usr/share/appname appname $RPM_INSTALL_PREFIX) && ln -s $(relocateLink /var/log/appname /usr/share/appname appname $RPM_INSTALL_PREFIX) $(relocateLink /usr/share/appname/logs /usr/share/appname appname $RPM_INSTALL_PREFIX)


%preun
#
# Adding service to autostart
# $1 = service name
#
startService() {
    app_name=$1

    app_sys_config="/etc/sysconfig/${app_name}"
    [ -e "${app_sys_config}" ] && . "${app_sys_config}"
    if [ -n "${PACKAGE_PREFIX}" ] ;
    then
      default_install_location="/usr/share/appname"
      actual_install_location="${PACKAGE_PREFIX}/${app_name}"

      sed -i "s|$default_install_location|$actual_install_location|g" "/usr/lib/systemd/system/${app_name}.service"
    fi

    systemctl enable "$app_name.service"
    systemctl start "$app_name.service"
}

#
# Removing service from autostart
# $1 = service name
#

stopService() {
    app_name=$1

    systemctl stop "$app_name.service"
    systemctl disable "$app_name.service"
}

#
# Restarting the service after package upgrade
# $1 = service name
#
restartService() {
   app_name=$1

   systemctl daemon-reload
   systemctl try-restart "$app_name.service"
}



# Scriptlet syntax: http://fedoraproject.org/wiki/Packaging:ScriptletSnippets#Syntax
# $1 == 1 is upgrade and $1 == 0 is uninstall
if [ $1 -eq 0 ] ;
then
    stopService appname || echo "Could not stop appname"
fi



%postun
# #######################################
# ## SBT Native Packager Bash Library  ##
# #######################################

# Adding system user
# $1 = user
# $2 = uid
# $3 = group
# $4 = description
# $5 = shell (defaults to /bin/false)
addUser() {
    user="$1"
    if [ -z "$user" ]; then
	echo "usage: addUser user [group] [description] [shell]"
	exit 1
    fi
    uid="$2"
    if [ -z "$uid" ]; then
	uid_flags=""
	  else
  uid_flags="--uid $uid"
    fi
    group=${3:-$user}
    descr=${4:-No description}
    shell=${5:-/bin/false}
    if ! getent passwd | grep -q "^$user:";
    then
	echo "Creating system user: $user in $group with $descr and shell $shell"
	useradd $uid_flags --gid $group -r --shell $shell -c "$descr" $user
    fi
}

# Adding system group
# $1 = group
# $2 = gid
addGroup() {
    group="$1"
    gid="$2"
    if [ -z "$gid" ]; then
	  gid_flags=""
  else
    gid_flags="--gid $gid"
  fi
    if ! getent group | grep -q "^$group:" ;
    then
	echo "Creating system group: $group"
	groupadd $gid_flags -r $group
    fi
}

# Will return true even if deletion fails
# $1 = user
deleteUser() {
    if hash deluser 2>/dev/null; then
	deluser --quiet --system $1 > /dev/null || true
    elif hash userdel 2>/dev/null; then
	userdel $1
    else
	echo "WARNING: Could not delete user $1 . No suitable program (deluser, userdel) found"
    fi
}

# Will return true even if deletion fails
# $1 = group
deleteGroup() {
    if hash delgroup 2>/dev/null; then
	delgroup --quiet --system $1 > /dev/null || true
    elif hash groupdel 2>/dev/null; then
	groupdel $1
    else
	echo "WARNING: Could not delete user $1 . No suitable program (delgroup, groupdel) found"
    fi
}

# #######################################

#
# Adding service to autostart
# $1 = service name
#
startService() {
    app_name=$1

    app_sys_config="/etc/sysconfig/${app_name}"
    [ -e "${app_sys_config}" ] && . "${app_sys_config}"
    if [ -n "${PACKAGE_PREFIX}" ] ;
    then
      default_install_location="/usr/share/appname"
      actual_install_location="${PACKAGE_PREFIX}/${app_name}"

      sed -i "s|$default_install_location|$actual_install_location|g" "/usr/lib/systemd/system/${app_name}.service"
    fi

    systemctl enable "$app_name.service"
    systemctl start "$app_name.service"
}

#
# Removing service from autostart
# $1 = service name
#

stopService() {
    app_name=$1

    systemctl stop "$app_name.service"
    systemctl disable "$app_name.service"
}

#
# Restarting the service after package upgrade
# $1 = service name
#
restartService() {
   app_name=$1

   systemctl daemon-reload
   systemctl try-restart "$app_name.service"
}



# Removing system user/group : appname and appname

# Scriptlet syntax: http://fedoraproject.org/wiki/Packaging:ScriptletSnippets#Syntax
# $1 == 1 is upgrade and $1 == 0 is uninstall

if [ $1 -eq 0 ] ;
then
    echo "Try deleting system user and group [appname:appname]"
    if getent passwd | grep -q "^appname:";
    then
	echo "Deleting system user: appname"
	deleteUser appname
    fi
    if getent group | grep -q "^appname:" ;
    then
	echo "Deleting system group: appname"
	deleteGroup appname
    fi
else
     restartService appname || echo "Failed to try-restart appname"
fi


relocateLink() {
  if [ -n "$4" ] ;
  then
    RELOCATED_INSTALL_DIR="$4/$3"
    echo "${1/$2/$RELOCATED_INSTALL_DIR}"
  else
    echo "$1"
  fi
}
[ -e /etc/sysconfig/appname ] && . /etc/sysconfig/appname
rm -rf $(relocateLink /usr/share/appname/logs /usr/share/appname appname $PACKAGE_PREFIX)


%files
%attr(0644,root,root) /usr/share/appname/lib/appname.appname-1.0.jar
%attr(0644,root,root) /usr/share/appname/lib/org.scala-lang.scala-library-2.10.6.jar
%dir %attr(755,appname,appname) /var/log/appname
%config %attr(644,root,root) /etc/default/appname
%dir %attr(755,appname,appname) /var/run/appname
%config %attr(0644,root,root) /usr/lib/systemd/system/appname.service
