#!/bin/bash
PARALLEL_SCRIPT="/home/s4278836/polyInfect/parallel_experiments.py"

python $PARALLEL_SCRIPT -f collection_params.rational.micEZ70.json

python $PARALLEL_SCRIPT -f collection_params.rational.micZ20.json
python $PARALLEL_SCRIPT -f collection_params.rational.micZ50.json

python $PARALLEL_SCRIPT -f collection_params.rational.micZ100.json
python $PARALLEL_SCRIPT -f collection_params.rational.micZ140.json

function get_features(){
    collection=$1;
    metafile=$collection"/metadata.tsv";
    output=$collection"/features.tsv";

    echo -e exp_ID"\t"alpha_EZ"\t"alpha_ZE"\t"e_return"\t"t5p"\t"t5p_first"\t"tTiny"\t"tTiny_first"\t"total_drug_in > $output;

    while IFS=$'\t' read -r ID aEZ aZE || [ -n "$ID" ]; do
        pf=$collection"/"$ID"/testing_perf."$ID".tsv";
        awk -v a1=$aEZ -v a2=$aZE '{FS="\t"; OFS="\t"} FNR == 2 { \
            x=$3; gsub(/[\[\]]/, "", x); n=split(x, t, " ");  \
            y=$4; gsub(/[\[\]]/, "", y); nT=split(y, tT, " "); \
            if (n > 0) pt=t[1]; else pt="N/A"; \
            if (nT > 0) ptT=tT[1]; else ptT="N/A"; \
            print $1, a1, a2, $2, $3, pt, $4, ptT, $5}' $pf >> $output;
    done < <(tail -n +2 $metafile);
}
export -f get_features

get_features rational_micEZ70
get_features rational_micZ20
get_features rational_micZ50
get_features rational_micZ100
get_features rational_micZ140