if test -z $(which rdmsr) ; then
    echo "msr-tools is not installed. Run 'sudo apt-get install msr-tools' to install it." >&2
    exit 1
fi

cores=$(cat /proc/cpuinfo | grep processor | awk '{print $3}')
for core in $cores; do
    sudo wrmsr -p${core} 0x1a0 0x4000850089
    state=$(sudo rdmsr -p${core} -f 38:38 0x1a0)
    echo "core ${core}: 0=enabled 1=disabled ${state}"
done
