#!/bin/bash
#if test -z $(/bin/which rdmsr) ; then
#   /bin/echo "msr-tools is not installed. Run 'sudo apt-get install msr-tools' to install it." >&2
#   exit 1
#fi

cores=$(/bin/cat /proc/cpuinfo | /bin/grep processor | /usr/bin/awk '{print $3}')
for core in $cores; do
    /usr/sbin/wrmsr -p${core} 0x1a0 0x850089
    state=$(/usr/sbin/rdmsr -p${core} -f 38:38 0x1a0)
    /bin/echo "core ${core}: 0=enabled 1=disabled ${state}"
done
/usr/bin/x86_energy_perf_policy -c 0 -v "performance"
