#!/bin/bash
set -u  # 設定していないパラメータがあったら打ち止め

# user 権限で実行する処理
# function run_as_user() {
#     # Dockerfileでprofile, .bashrcに指定した設定を読み込む
#     source /etc/profile
#     source ${HOME}/.bashrc
#     #
#     PROJECT_DIR=${HOME}/work/${COMPOSE_PROJECT_NAME}/
#     pip install --editable ${PROJECT_DIR}
#     # jupyter lab --NotebookApp.token='password' --ip='*' --notebook-dir=/home/`id -n -u`/work --allow_remote_access=true --browser=False
# }

chown -R ${USER_NAME}:${USER_NAME} ${USER_HOME}

# sudo COMPOSE_PROJECT_NAME=${COMPOSE_PROJECT_NAME} su ${USER_NAME} -c "$(declare -f run_as_user); run_as_user"
pip install --editable /home/${USER_NAME}/work/${COMPOSE_PROJECT_NAME}/
pip install --editable /home/${USER_NAME}/work/data_fetcher/
pip install --editable /home/${USER_NAME}/work/stock/
pip install --editable /home/${USER_NAME}/work/crypto/

/usr/sbin/sshd -D
