# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  # All Vagrant configuration is done here. The most common configuration
  # options are documented and commented below. For a complete reference,
  # please see the online documentation at vagrantup.com.

  # Every Vagrant virtual environment requires a box to build off of.
  config.vm.box = "bento/ubuntu-16.04"
  config.vm.network "forwarded_port", guest: 80, host: 8080

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
      g++ \
      gcc-6 \
      git \
      lsb \
      lshw \
      lsof \
      mongodb-org \
      moreutils \
      nano \
      patchutils \
      python3-pip \
      python3.6 \
      tree \
      virtualbox-guest-dkms \
      virtualbox-guest-utils \
      xvfb \

    pip3 install -r requirements/dev.txt
  SHELL
end