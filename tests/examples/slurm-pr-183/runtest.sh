simex e purge --failed -f

rm -r output
rm -r aux
rm .simex.cache

simex e list
simex e launch --launcher scaling
simex e list

squeue
squeue -r

sleep 3s

simex e list
