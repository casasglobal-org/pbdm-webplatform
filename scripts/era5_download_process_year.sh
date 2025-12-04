#!/bin/bash

YEAR=$1

if [ -z "$YEAR" ]; then
    echo "Usage: $0 <YEAR>"
    exit 1
fi

this_dir=`dirname $0`
main_dir=`dirname $this_dir`
env_dir="$main_dir/venv"

if [ ! -d "$main_dir" ]; then
    echo "Main directory does not exist"
fi

if [ ! -d "$env_dir" ]; then
    echo "Virtual environment directory 'venv' does not exist"
    env_dir="$main_dir/.env"

    if [ ! -d "$env_dir" ]; then
        echo "Environment directory '.env' does not exist"
        env_dir="$main_dir/.venv"

        if [ ! -d "$env_dir" ]; then
            echo "Virtual environment directory '.venv' does not exist"

            env_dir="$main_dir/env"

            if [ ! -d "$env_dir" ]; then
                echo "Environment directory 'env' does not exist"
                exit 1;
            else
                source "$env_dir/bin/activate"
            fi
        else
            source "$env_dir/bin/activate"
        fi
    else
        source "$env_dir/bin/activate"
    fi
else
    source "$env_dir/bin/activate"
fi

time python ${main_dir}/casas_web_portal/manage.py download_era5 $YEAR

time python ${main_dir}/casas_web_portal/manage.py create_txt_era5 --dir /opt/casas_data/ $YEAR

rm -f /opt/casas_data/data/era5/*/*-$YEAR-*-merged.nc
rm -f /opt/casas_data/data/era5/*/*${YEAR}*.zip

exit