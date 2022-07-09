#!/bin/bash
# PARALLEL_SCRIPT="/home/s4278836/polyInfect/parallel_experiments.py"

# python $PARALLEL_SCRIPT -f collection_params.qlearning.micEZ70.json

# python $PARALLEL_SCRIPT -f collection_params.qlearning.micZ140.json

PARALLEL_SCRIPT="../parallel_experiments.py"

python $PARALLEL_SCRIPT -f collection_params.qlearning.micEZ70.json --local --re_test

python $PARALLEL_SCRIPT -f collection_params.qlearning.micZ140.json --local --re_test

function get_features(){
    collection=$1;
    metafile=$collection"/metadata.tsv";
    output=$collection"/features.tsv";

    echo -e exp_ID"\t"alpha_EZ"\t"alpha_ZE"\t"e_return"\t"t5p"\t"t5p_first"\t"tTiny"\t"tTiny_first"\t"total_drug_in > $output;

    while IFS=$'\t' read -r ID aEZ aZE || [ -n "$ID" ]; do #loop over the experiments in the collection

        pf=$collection"/"$ID"/testing_perf."$ID".tsv"; #testing performance file of each experiment

        l=$(cat $pf | wc -l); #get the number of lines of the file
        if [ $l -gt 2 ]; then #if there are more than 2 lines, it's because one of the array stored was too long and resulted in line break
            tmp="tmp.tsv";
            head -n 1 $pf > $tmp; 
            tail -n +2 $pf | tr --delete '\n' >> $tmp; #remove the line breaks within arrays
            mv $tmp $pf; 
        fi;

        # get the first t5p and the first tTiny, then print data into a pretty form
        awk -v a1=$aEZ -v a2=$aZE '{FS="\t"; OFS="\t"} FNR == 2 { \
            x=$3; gsub(/[\[\]]/, "", x); n=split(x, t, " ");  \
            y=$4; gsub(/[\[\]]/, "", y); nT=split(y, tT, " "); \
            if (n > 0) pt=t[1]; else pt="N/A"; \
            if (nT > 0) ptT=tT[1]; else ptT="N/A"; \
            print $1, a1, a2, $2, $3, pt, $4, ptT, $5}' $pf >> $output;
    done < <(tail -n +2 $metafile);
}
export -f get_features

get_features qlearning_micEZ70
get_features qlearning_micZ140

##### Collect features from Q-learning + Rational
collect="./features.qlearning.rational.tsv"

cat qlearning_micEZ70/features.tsv > $collect

tail -n +2 qlearning_micZ140/features.tsv >> $collect

rationals=("rational_micEZ70" "rational_micZ140")
exp_ids=("3" "24" "45")

for r in ${rationals[@]}; do
    for e in ${exp_ids[@]}$; do
        f=$r"."$e;
        grep -w "$f" ../Rational/$r/features.tsv >> $collect;
    done;
done
