#!/bin/bash
PARALLEL_SCRIPT="/home/s4278836/polyInfect/parallel_experiments.py"

python $PARALLEL_SCRIPT -f collection_params.rational.micEZ70.json

python $PARALLEL_SCRIPT -f collection_params.rational.micZ20.json
python $PARALLEL_SCRIPT -f collection_params.rational.micZ50.json

python $PARALLEL_SCRIPT -f collection_params.rational.micZ100.json
python $PARALLEL_SCRIPT -f collection_params.rational.micZ140.json

function summarize_t5p(){
    collection=$1;
    metafile=$collection"/metadata.tsv";
    output=$collection"/summary_t5p.tsv";

    echo -e exp_ID"\t"alpha_EZ"\t"alpha_ZE"\t"t5p"\t"t5p_first > $output;

    while IFS=$'\t' read -r ID aEZ aZE || [ -n "$ID" ]; do
        pf=$collection"/"$ID"/testing_perf."$ID".tsv";
        awk -v a1=$aEZ -v a2=$aZE '{FS="\t"; OFS="\t"} FNR == 2 { \
            x=$2; gsub(/[\[\]]/, "", x); split(x, t, " ");  print $1, a1, a2, $2, t[1]}' $pf >> $output;
    done < <(tail -n +2 $metafile);
}
export -f summarize_t5p

summarize_t5p rational_micEZ70
summarize_t5p rational_micZ20
summarize_t5p rational_micZ50
summarize_t5p rational_micZ100
summarize_t5p rational_micZ140