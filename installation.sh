#!/bin/bash

######################################################################################
#
#   This is to simplify the whole intallation process of python and by extension, 
#   RESTful service managed by Vertical Data Management Team.
#   
#   REQUIREMENT: 
#       - Python tarball
#       - dependencies.tar.gz
#
#   ARGUMENT1 Python-{version}-tar  (NOT tar.gz)
#   ARGUMENT2 dependencies.tar.gz   (Where you place all the python dependencies)
######################################################################################

help(){
  echo -e "  installation.sh [OPTIONS] [arg]
    -p, --python Path to Python-{version}-tar  (Required)
    -d, --dependencies Path to Python dependencies to boot up the RESTful service (Required)
  "
}

params(){
  SCRIPT=$(realpath $0)
  CURDIR=$(dirname $SCRIPT)
  if [[ "$#" -eq 0 ]];then
    help
    exit 1
  elif [[ -z $(echo "$@" | grep "\-p\|\-\-python") ]];then
  echo -e "
  [ERROR] Python tar must be given."
          help
          exit 1
  elif [[ -z $(echo "$@" | grep "\-d\|\-\-dependencies") ]];then
  echo -e "
  [ERROR] Python dependencies tar.gz must be given."
          help
          exit 1
  else 
    while [[ $# -gt 0 ]]; do
      if [[ "${1,,}" == "-p" ]] || [[ "${1,,}" == "--python" ]]; then
        shift
        TAR_FILENAME=$1
        FILENAME="${TAR_FILENAME%.*}"
        VERSION=$(echo $FILENAME | grep -Po "[0-9]{1}\.[0-9]{1,2}")
        #File path Validation
        if [[ $TAR_FILENAME=$1 =~ ^[-] ]]; then
          echo -e "
  [ERROR] Invalid file path."
          help
          exit 1
        elif [[ "$TAR_FILENAME" == "" ]]; then
          echo -e "
  [ERROR] File path must be given"
          help
          exit 1
        fi
        if ! [[ -f $TAR_FILENAME ]]; then
          echo -e "
  [ERROR] No such file: $TAR_FILENAME "
          echo "Program exists..."
          exit 1
        fi
        shift
      elif [[ "${1,,}" == "-d" ]] || [[ "${1,,}" == "--dependencies" ]]; then
        shift
        TAR_DEPENDENCY=$1
        DEPENDENCY="${TAR_DEPENDENCY%%.*}"
        if [[ $TAR_DEPENDENCY =~ ^[-] ]]; then
          echo -e "[ERROR] Invalid input."
          help
          exit 1
        elif [[ -z $TAR_DEPENDENCY ]]; then 
        echo -e "
  [ERROR] Dependencies must be given."
          help
          exit 1
        fi
        shift  
      else
        help
        exit 0 
      fi
    done
  fi

}


main(){
    params "$@"
    echo "
    TAR_FILENAME : $TAR_FILENAME
    FILENAME : $FILENAME
    VERSION : $VERSION
    TAR_DEPENDENCY : $TAR_DEPENDENCY
    DEPENDENCY : $DEPENDENCY
    "
    read -p "You you want to continue? [y/N]" -n1 GO
    GO=${GO,,} 
    if [ $GO == "y" ];then
        #Decompressed tar 
        tar xfz $TAR_FILENAME

        #Preliminary steps
        sudo apt-get update 
        sudo apt-get upgrade
        sudo apt-get install -y make build-essential libssl-dev zlib1g-dev \
            libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
            libncurses5-dev libncursesw5-dev xz-utils tk-dev 

        #For Systemd control
        sudo apt install -y dbus libdbus-glib-1-dev libdbus-1-dev python-dbus 

        #prepare build python
        cd $FILENAME
        ./configure --enable-optimizations --with-ensurepip=install
        #enable-optimizations flag will enable some optimizations within Python to make it run about 10 percent faster.
        #with-ensurepip=install flag will install pip bundled with this installation.

        #build python using make
        make -j 8
        # -j option simply tells make to split the building into parallel steps to speed up


        # You’ll use the altinstall target here to avoid overwriting 
        # the system Python. Since you’re installing into /usr/bin, 
        # you’ll need to run as root:
        sudo make altinstall

        cd $CURDIR
        tar zxvf $TAR_DEPENDENCY

        sleep 0.5
        cd $DEPENDENCY/  ##
        sudo pip${VERSION} install * -f ./ --no-index

        echo "
        [Unit]
        Description=Health Check Service
        After=multi-user.target


        [Service]
        Type=simple
        WorkingDirectory=/root/vertica-agent
        ExecStart=python${version} -m flask run
        StandardInput=tty-force
        Restart=always
        RestartSec=30s
        StartLimitIntervalSec=100
        StartLimitBurst=3

        [Install]
        WantedBy=multi-user.target
        " | sudo tee "/lib/systemd/system/vertica-agent.service" /dev/null

        sudo systemctl enable vertica-agent.service

        sudo mkdir /root/vertica-agent

        #Move files except for the unwanted
        FILES=$(ls -a $CURDIR -I . -I ..)
        for file in $FILES;do
            case "${file##*/}" in 
                "installation.sh"|"$TAR_FILENAME"|"$FILE_NAME"|"$TAR_DEPENDENCY"|"$DEPENDENCY"|"requirements.txt")
                ;;
            *)
                sudo mv $CURDIR/$file /root/vertica-agent
            esac
        done
        sudo service vertica-agent start 
    else
    echo "Bye!"
    fi


}

main "$@"