source ../../set_env.sh
c=1
while IFS='	' read -r data model sub name count dcs max_dim location
do
    mkdir ../log/census_001/
    mkdir ../analysis/census_001/
    echo $location
    echo $name
    for feat in lang initsim constraint initattr freq
    do
        ./../../create_db_ubuntu.sh ${data}_${c}
        python hc.py -msg GL -notes $c -dataname $data -dcpath $location -dc $name -k 0.1 -w 0.01 -omit init occur embed $feat --wlog --example &> ../log/census_001/runtime-${c}.log
        c=$((c+1))
        ./../../create_db_ubuntu.sh ${data}_${c}
        python hc.py -msg GL -notes $c -dataname $data -dcpath $location -dc $name -k 0.1 -w 0.01 -omit init occurattr embed $feat --wlog --example &> ../log/census_001/runtime-${c}.log
        c=$((c+1))
    done
    python send_email.py census
done < ../batch_run_dcs/dc-census-001.txt
