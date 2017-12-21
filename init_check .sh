#!/bin/bash

#Define log file
FILE='/opt/init.log'


#Defing echo thead
function echo_th(){
	STRLEN=$( echo $1 | awk '{ print length($0) }');
	WIDTH=`echo \(100-$STRLEN\)/2 | bc`;
	eval printf "%.s*" {1..$WIDTH};
    echo -n $1;
    eval printf "%.s*" {1..$WIDTH};
	echo;
}


#Define echo filter
function echo_filter(){
	grep -vE "^#|^$" $1;
}


#Check directory exist or not
function directory_check(){
	if [ -d $1 ];then
		echo "$1 directory exist";
		return 0;
	else
		echo "$1 directory not exist";
		return 1;
	fi
}


#Check porcessor exist or not
function proc_check(){
	ps -ef | grep $1 | grep -v grep | wc -l;
}


#Check hosts & network config, etc.
function net_check(){
	#hostname
	echo_th Host_Check;
	hostname;
	#hosts file
	echo_th /etc/hosts;
	echo_filter /etc/hosts;
	#network
	echo_th Network_Check;
	ifconfig 2>/dev/null || ip addr;
	#DNS
	echo_th DNS_Check;
	ping -c 3 www.iflytek.com;
	ping -c 3 transfer01.falcon;
	#ntp
	echo_th NTP_Check;
	ntpq -p;
	#yum/apt conf
	echo_th YUM/APT_Check;
	yum -h 2&>/dev/null && echo_filter /etc/yum.repos.d/centos.repo || echo_filter /etc/apt/sources.list;
	#iptables/firewall
	echo_th Iptables_Check;
	iptables -L || firewall-cmd  --state;
}


#Check kernel config
function kernel_check(){
	#ulimit
	echo_th ulimit_Check;
	ulimit -a;
	#/etc/sysctl.conf
	echo_th /etc/sysctl.conf;
	echo_filter /etc/sysctl.conf;
}


#Check system config
function sys_check(){
	#disk
	echo_th Disk_Check;
	fdisk -l 2>/dev/null;
	echo_th Mount;
	df -h;
	#rc.local
	echo_th rc.local;
	echo_filter /etc/rc.local;
	#selinux
	echo_th Selinux;
	getenforce;
	#vc account
	echo_th vc_accout;
	grep vc /etc/passwd;
}


#Check basic tools
function tool_check(){
	#pmc
	echo_th pmc;
	echo -n 'pmc processor:';
	echo `proc_check pmc`;
	#pauto
	echo_th pauto;
	echo -n 'pauto processor:';
	echo `proc_check pauto`;
	#open-falcon
	echo_th falcon;
	echo -n 'falcon processor:';
	echo `proc_check falcon`;
	directory_check /opt/open-falcon;
	#saltstack
	echo_th salt;
	echo -n 'salt processor:';
	echo `proc_check salt-minion`;
	directory_check /etc/salt;
}

#Function main
function main(){
	sys_check;
	kernel_check;
	net_check;
	tool_check;
}


main | tee $FILE