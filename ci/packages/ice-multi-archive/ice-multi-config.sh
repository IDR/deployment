#!/bin/bash
#
# eval this file in bash, and provide arguments to set the environment
# variables for building or running omero.
#
# Example: setup the environment for ice 3.4.2
#   $ eval $(~/ice/ice-multi-config.sh ice342)
#   $ echo $ICE_HOME
#   $ echo $PYTHONPATH
#   $ echo $PATH
#   $ echo $LD_LIBRARY_PATH
#

set -e

ICE_SCRIPT="$(readlink -e "$0")"
ICE_BASEDIR="$(dirname "$ICE_SCRIPT")"

prepend_path() {
    VAR="$1"
    PRE="$2"
    eval CURRENT="\\\"\$$VAR\\\""
    if [ "$CURRENT" != \"\" ]; then
        eval echo export "$VAR=\\\"$PRE:$CURRENT\\\""
    else
        echo export "$VAR=\"$PRE\""
    fi
}

omero_env() {
    # Remove - and . when matching
    IV="${1//[-.]/}"
    case "$IV" in
        ice33 | ice331 )
            ICE_VERSION=3.3.1
            ;;

        ice34 | ice342 )
            ICE_VERSION=3.4.2
            ;;

        ice350 )
            ICE_VERSION=3.5.0
            ;;

        ice35 | ice351 )
            ICE_VERSION=3.5.1
            ;;

        ice36 | ice362 )
            ICE_VERSION=3.6.3
            ;;

        * )
            echo "ERROR: Unknown environment option: $1" >&2
            # This ensures the eval returns non-zero
            echo false
            exit 1
            ;;
    esac

    if [ -n "$ICE_VERSION" ]; then
        ICE_HOME=$ICE_BASEDIR/ice-$ICE_VERSION
        echo export ICE_HOME=\"$ICE_HOME\"
        echo export ICE_VERSION=\"$ICE_VERSION\"
        prepend_path PYTHONPATH "$ICE_HOME/python"
        prepend_path PATH "$ICE_HOME/bin"
        prepend_path LD_LIBRARY_PATH "$ICE_HOME/lib64"
        prepend_path LIBPATH "$ICE_HOME/lib64"
        prepend_path SLICEPATH "$ICE_HOME/slice"
    fi

    return 0
}

while [ $# -gt 0 ]; do
    omero_env "$1"
    shift
done
