set -e
apt-get update -y
sleep 1
apt-get upgrade -y
sleep 1
apt-get install python git -y
sleep 1
su -c "git clone --recursive https://github.com/refractionPOINT/limacharlie.git -b $LC_BRANCH" `logname`
cd limacharlie/cloud/infrastructure/
python ./1_install_single_node_test_cluster.py
su -c "python ./2_start_single_node_test_cluster.py" `logname`