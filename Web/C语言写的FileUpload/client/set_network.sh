#!/bin/bash

#sudo tc qdisc add dev eth0 root handle 1:0 netem delay 150ms 70ms distribution normal loss 10%
sudo tc qdisc add dev eth0 root handle 1:0 netem 
sudo tc qdisc add dev eth0 parent 1:1 handle 10: tbf rate 100kbps buffer 1600 limit 3000

#sudo tc qdisc add dev lo root handle 1: prio
#sudo tc qdisc add dev lo parent 1:3 handle 30: \
#    tbf rate 1mbps buffer 10000 limit 3000
#sudo tc qdisc add dev lo parent 30:1 handle 31: \
#    netem delay 150ms 70ms distribution normal loss 50%
#sudo tc filter add dev lo protocol ip parent 1:0 prio 3 u32 \
#    match ip dst 127.0.0.1/32 flowid 1:3
#tbf rate 100kbit buffer 1600 limit  3000

#sudo tc qdisc add dev lo root handle 1:0 netem delay 150ms 70ms distribution normal loss 40%
#sudo tc qdisc add dev lo parent 1:1 handle 10: tbf rate 100kbit buffer 1600 limit 3000
#sudo tc qdisc add dev lo parent 1:1 handle 10: tbf rate 10mbit buffer 16000 limit 3000
#sudo tc qdisc add dev lo root tbf rate 10mbit buffer 16000 limit 3000
#sudo tc qdisc add dev eth0 root tbf rate 100kbps latency 150ms 

#sudo tc qdisc add dev lo root handle 100: cbq bandwidth 10Mbit avpkt 1000 
