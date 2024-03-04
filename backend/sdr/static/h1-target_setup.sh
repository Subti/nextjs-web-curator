export PYTHONPATH="/usr/local/lib/python3.10/site-packages/"
sudo ifconfig enp6s0f0np0 192.168.40.1 netmask 255.255.255.0
sudo ifconfig enp6s0f1np1 192.168.64.1 netmask 255.255.255.0
sudo ifconfig enp6s0f0np0 mtu 9000 # For 10 GigE
sudo ifconfig enp6s0f1np1 mtu 9000 # For 10 GigE
sudo sysctl -w net.core.rmem_max=24912805
sudo sysctl -w net.core.wmem_max=24912805

