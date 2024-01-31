# Metadata 

基于上一步爬取的镜像名爬取每个镜像的更详细信息.包括:
- Short description
- Full description
- Dockerfile
- ...

支持中断自动恢复

支持运行完毕自动导出mongo记录到`./data`

为节省空间，每个镜像最多爬取100个tag

## Configure

### Proxy

配置代理API URL需要满足以下要求：

1. 单次返回一个代理
2. 返回格式为txt
3. 换行符为`\n`

例如：http://api.proxy.ip2world.com/getProxyIp?num=1&lb=4&return_type=txt&protocol=http

返回示例应为：`"43.159.28.58:19594"`

URL填入`docker-compose.yaml`中的`API_URL`项

### Input

上一步爬取到的镜像名列表，名如`all_images_1.list`

> 手动模式下需将存放`.list`文件的目录挂载到`/data`下。docker-compose部署方式已经自动挂载

### Mongo

json格式的镜像元数据.

需要将mongo运行目录挂载到`/data/db`,将结果导出目录挂载到`/result`

## Usage

### 单例手动运行

#### 设置network
```bash
sudo docker network create  -d bridge meta
```
#### 拉起mongo

```bash
# /metadata
docker run --name mongo --network=meta -v ./../database:/data/db -v ./data:/result --restart=unless-stopped mongo:latest
```

注意:如果mongo容器意外关闭,可以通过运行相同指令自动恢复

#### 拉起crawler容器

```bash
sudo docker build -t metadata:latest .
```

注意修改`API_URL`和`PREFIX`为需要的值.
并且注意mongo容器已经启动

```bash
#在/metadata下运行

docker build -t crawler:latest .
docker run \
  --name metadata_1 \
  --network=meta \
  -e PREFIX=1 \
  -e API_URL=http://api.proxy.ip2world.com/getProxyIp?num=1&lb=4&return_type=txt&protocol=http \
  -e MONGO_HOST=mongo \
  -e MONGO_PORT=27017 \
  -e DB_NAME=metadata \
  -v ./../docker_images/data:/data \
  --restart-condition=on-failure \
  --restart-delay=5s \
  --restart-max-attempts=3 \
  crawler:latest
```
### Docker-compose运行

运行前需要在环境变量中设置爬取前缀，并在`docker-compose.yaml`中调整代理URL
```bash
PREFIX="1";sudo docker-compose up -d
```
