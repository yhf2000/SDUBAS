#!/bin/bash

# 配置参数
frontend_repository_path="/home/ubuntu/SDUBAS-frontend"  # 本地前端仓库路径
backend_repository_path="/home/ubuntu/SDUBAS-backend"  # 本地后端仓库路径
# 获取本地分支的最新提交哈希值
get_local_head() {
    local repository_path=$1
    cd "$repository_path" || exit 1
    git rev-parse HEAD
}

# 获取远程分支的最新提交哈希值
get_remote_head() {
    local repository_path=$1
    cd "$repository_path" || exit 1
    git fetch
    git rev-parse origin/master   # 这里假设检测的是远程的 master 分支
}

# 主循环
while true; do
    frontend_local_head=$(get_local_head $frontend_repository_path)
    frontend_remote_head=$(get_remote_head $frontend_repository_path)
    backend_local_head=$(get_local_head $backend_repository_path)
    backend_remote_head=$(get_remote_head $backend_repository_path)

    # 比较本地分支和远程分支的最新提交哈希值
    if [ "$frontend_local_head" != "$frontend_remote_head" ]; then
        echo "前端仓库有内容更新，正在拉取最新代码..."
        cd "$frontend_repository_path" || exit 1
        git pull
    else
        echo "仓库无内容更新"
    fi

    if [ "$backend_local_head" != "$backend_remote_head" ]; then
        echo "后端仓库有内容更新，正在拉取最新代码..."
        cd "$backend_repository_path" || exit 1
        git pull
    else
        echo "仓库无内容更新"
    fi

done