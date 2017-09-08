#!/bin/sh
if test -z $1
then
    echo "arg expected"
    exit 1
fi
if ! test -f $1
then
    echo "$1 does note exist or is not a file."
    exit 1
fi
n=`basename $1`
posted_name="BIOL848-${n}"
scp "$1" "mholder@phylo.bio.ku.edu:/var/www/html/BIOL848/${posted_name}"
echo "Posted as"
echo "http://phylo.bio.ku.edu/BIOL848/${posted_name}"
