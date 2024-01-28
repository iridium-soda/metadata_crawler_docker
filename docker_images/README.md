# Images

## Description
- 根据从keywords模块获取的有效关键词列表在DockerHub中获取镜像名
- 好像用不到proxy
- 每个容器只执行一个prefix(关键词文件)的爬取.**不能多个容器同时使用同一个keyword文件运行**
- **启动容器之前必须保证keyword文件已经爬取完毕并且存放在`/keywords/data/`下且命名正确,容器启动时会自动挂载**
- 挂载列表：
    - `/keywords/data`:`/data`
    - `/docker_images/data`:`/result`

## Usage

### Build image
**注意：用环境变量指定爬取文件**

```bash
#/docker_images/
sudo docker build -t images .
```

### Startup

启动前检查：
- `/keywords/data/`目录下是否已经准备好爬取的完整的关键词列表
- `/docker_images/data/`目录是否存在

```bash
# /docker_images 目录下
sudo docker run -d --name imagename_crawler -v $(pwd)/data:/result -v $(pwd)/../keywords/data:/data -e PREFIX=1 images
```

## Reference
- 一键build & run脚本在`build_and_test.sh`,运行前注意修改prefix环境变量
- 测试API的命令在`test_api.sh`
- API 参考示例在`sample.json`
