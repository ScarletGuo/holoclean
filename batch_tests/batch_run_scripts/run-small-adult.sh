source ../../set_env.sh
c=1
while IFS='	' read -r data model sub name count dcs max_dim location
do

    echo $location
    echo $name
    #mkdir ../log/small_adult/
    for feat in lang initsim occurattr constraint initattr freq
    do
        ./../../create_db_ubuntu.sh small_adult_1_${c}
        python hc.py -notes ${c} -dataname small_adult_1 -dcpath $location -dc $name -k 0.1 -w 0.01 -omit init $feat occur --wlog --example |& tee ../log/small_adult/$c.log
        echo $c
        c=$((c+1))
    done
    python send_email.py hc3
    break
done < ../batch_run_dcs/dc-adult-joint.txt
