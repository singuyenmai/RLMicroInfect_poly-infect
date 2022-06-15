#!/bin/bash
python /home/s4278836/polyInfect/parallel_experiments.py -f collection_params.rational.sameMIC.json

python /home/s4278836/polyInfect/parallel_experiments.py -f collection_params.rational.MIC12.json

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

summarize_t5p rational_sameMIC
summarize_t5p rational_MIC12
