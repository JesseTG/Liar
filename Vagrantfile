# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "bento/ubuntu-16.04"
  config.vm.network "forwarded_port", guest: 80, host: 8080, host_id: "127.0.0.1"
  config.vm.network "forwarded_port", guest: 5000, host: 5000, host_id: "127.0.0.1"
  config.vm.network "forwarded_port", guest: 27017, host: 16906, host_id: "127.0.0.1"
  config.vm.synced_folder ".", "/vagrant"

  config.vm.provider "virtualbox" do |vb|
    vb.memory = 2048
    vb.linked_clone = true if Vagrant::VERSION =~ /^1.8/

  end

  config.vm.provision "shell", inline: <<-SHELL
    apt-get update -q
    apt-get install -qy software-properties-common
    apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 0C49F3730359A14518585931BC711F9BA15703C6
    echo "deb [ arch=amd64,arm64 ] http://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/3.4 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.4.list
    apt-mark hold grub*
    add-apt-repository -y ppa:ubuntu-toolchain-r/test
    add-apt-repository -y ppa:jonathonf/python-3.6
    apt-get update -q
    apt-get dist-upgrade -qy
    apt-get install -qy \
      build-essential \
      coreutils \
      curl \
      g++ \
      gcc-6 \
      git \
      jq \
      lsb \
      lshw \
      lsof \
      mongodb-org \
      moreutils \
      nano \
      patchutils \
      python3-pip \
      python3.6 \
      silversearcher-ag \
      tree \
      virtualbox-guest-dkms \
      virtualbox-guest-utils \
      wget \

    echo "#!/bin/sh -e
sudo service mongod start
exit 0
" > /etc/rc.local
    chmod +x /etc/rc.local
    service mongod start
    cd /vagrant
    pip3 install --requirement requirements/dev.txt
  SHELL
end