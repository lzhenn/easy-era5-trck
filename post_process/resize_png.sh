#!/bin/bash

PREFIX_ARR=( "SP_Jan16" )
SUFFIX="png"
STRT_F=0
END_F=648

N_FRM=$(( $END_F - $STRT_F ))

SCRIPT_DIR=`pwd`

WRK_DIR=../fig/
cd $WRK_DIR
echo $WRK_DIR

rm -f *noborder*

L_PREFIX=${#PREFIX_ARR[@]}
for((IPRE=0;IPRE<L_PREFIX;IPRE++))
do
    PREFIX=${PREFIX_ARR[$IPRE]}
    b=''
    for((I=$STRT_F;I<=${END_F};I++))
    do
        printf "[%-50s] %d/%d \r" "$b" "$(( $I - $STRT_F ))" "$N_FRM";
        b+='#'
        TFSTMP=`printf "%.4d" $I`
        convert ${PREFIX}.${TFSTMP}.${SUFFIX} -resize 738x200! ${PREFIX}.r.${TFSTMP}.${SUFFIX}
    done
done
ffmpeg -r 15 -i ${PREFIX}.r.%04d.png -vf format=yuv420p  out.mp4

