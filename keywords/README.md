# Keywords

- 测试**有效**的搜索关键词
- **有效**:由于DockerHub的限制,搜索词最短为2个字符,最多显示10000条搜索结果.有效指的是获得少于10000条数据的搜索词;这样可以得到完整的搜索结果
- 结果输出到`./data/keyWordList_[Prefix].txt`,每个关键词一行
- 不需要代理

## Installation

### Python venv
```bash
python -m venv keywords_venv
source keywords_venv/bin/activate
```

### Install geckodriver

```bash
wget https://github.com/mozilla/geckodriver/releases/download/v0.34.0/geckodriver-v0.34.0-linux64.tar.gz
tar -zxvf geckodriver-v0.34.0-linux64.tar.gz
mv geckodriver /usr/local/share/
ln -s /usr/local/share/geckodriver /usr/local/bin/geckodriver
ln -s /usr/local/share/geckodriver /usr/bin/geckodriver
```

### Install firefox

```bash
sudo snap remove firefox
sudo sysctl -w net.ipv6.conf.all.disable_ipv6=1 
sudo sysctl -w net.ipv6.conf.default.disable_ipv6=1
sudo sysctl -w net.ipv6.conf.lo.disable_ipv6=1
sudo add-apt-repository ppa:mozillateam/ppa
echo '
Package: *
Pin: release o=LP-PPA-mozillateam
Pin-Priority: 1001
' | sudo tee /etc/apt/preferences.d/mozilla-firefox
echo 'Unattended-Upgrade::Allowed-Origins:: "LP-PPA-mozillateam:${distro_codename}";' | sudo tee /etc/apt/apt.conf.d/51unattended-upgrades-firefox
sudo apt install firefox
```

## Usage

```shell
# at directory `keywords`
python src/main.py
# run background
nohup python src/main.py &
```

数据在`./data`里
