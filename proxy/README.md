# Proxy
## Description
- 提供本地的代理池服务
- 需要提供代理池的API URL
- 支持为每一个worker提供单独的IP
- 429重试时切换
- 通过socket进行通信

## Usage

### 单独启动

```bash
sudo docker build -t proxy:latest .
sudo docker run -d -p 10756:10756 \
-e PROXY_URL="http://api.proxy.ip2world.com/getProxyIp?num=1&lb=4&return_type=txt&protocol=http" \
-e PORT=10756 \
-e NUM_WORKERS=10 \
proxy:latest 
```

**默认内部端口为10756,默认worker数量为10**
**需要注意端口冲突**

### 配合服务启动
一般使用docker compose. 见镜像名爬取/元数据名爬取文档

### 请求一个代理
请求格式说明
```json
{
    "type": "get_proxy",//请求类型 get_proxy(获取代理)/report(报告代理失效)
    "thread_index": 0//代理池代理索引:不应超过容器启动时配置的大小
}
```

向代理池POST请求代理IP格式:

```json
curl -X POST -H "Content-Type: application/json" \
-d '{"type":"get_proxy","thread_index":0}' \
http://localhost:10756
```

返回格式
```json
{
    "proxy": '43.159.30.199:19526'
}
```

### 报告代理失效
```json
curl -X POST -H "Content-Type: application/json" \
-d '{"type":"report","thread_index":0}' \
http://localhost:10756
```

返回格式
```json
{"status":"OK"}
```


