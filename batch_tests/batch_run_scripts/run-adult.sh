source ../../set_env.sh
c=1
while IFS='	' read -r data model sub name count dcs max_dim location
do

    echo $location
    echo $name
    mkdir ../log/${data}/
    mkdir ../analysis/${data}/
    for feat in lang initsim occurattr constraint initattr freq
    do 
        ./../../create_db_ubuntu.sh adult_1_f${c}
        python hc.py -notes f${c} -dataname adult_1 -dcpath $location -dc $name -k 0.1 -w 0.01 -omit init occur $feat --wlog --example |& tee ../log/${data}/${c}_${feat}.log
        echo $c
        c=$((c+1))
    done
    python send_email.py hc3
done < ../batch_run_dcs/dc-adult-joint.txt
