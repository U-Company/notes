# yandex-cloud-add-user

Create new machine with default `username` and pair ssh key (`id_rsa_default.pub`).

Copy additional key `id_rsa_key.pub` for additional user:

    scp id_rsa_key.pub username@1.2.3.4:.

Connect to your machine by ssh:

    ssh username@1.2.3.4
    
    
Turn on `sudo` mode:

    sudo su

Create new user:

    mkdir ../username
    useradd username

Create user to root group:

    sudo usermod -a -G root username
    
If you use docker, you need docker-group:

    sudo usermod -a -G docker username
    
Now, you need go to `/etc/sudores.d/` (only `sudo su`):

    cd /etc/sudores.d/

Open `90-cloud-init-users`:

    sudo vi 90-cloud-init-users
    
**90-cloud-init-users**:

    # Created by cloud-init v. 19.2-24-ge7881d5c-0ubuntu1~18.04.1 on Mon, 06 Jan 2020 16:21:48 +0000

    # User rules for eurvanov
    username_default ALL=(ALL) NOPASSWD:ALL
 
 Add line:
 
    username ALL=(ALL) NOPASSWD:ALL

    
