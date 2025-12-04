set -e

# 鎹㈡簮
sed -i 's|archive.ubuntu.com|mirrors.aliyun.com|g' /etc/apt/sources.list
sed -i 's|security.ubuntu.com|mirrors.aliyun.com|g' /etc/apt/sources.list

echo 'Updating APT...'
apt-get update

echo 'Downloading APT packages...'
# 瀹氫箟闇€瑕佷笅杞界殑鍖呭垪琛?(涓?Dockerfile 淇濇寔涓€鑷?
PACKAGES="bash tzdata locales libreoffice pandoc poppler-utils file jq python3 python3-pip python3-venv fonts-noto-cjk"

# 涓嬭浇鍖呭強鍏朵緷璧栧埌缂撳瓨鐩綍
# 浣跨敤 clean 娓呯悊鏃х紦瀛橈紝纭繚鍙笅杞介渶瑕佺殑
apt-get clean
apt-get install --download-only -y $PACKAGES

# 澶嶅埗 deb 鏂囦欢鍒版寕杞界洰褰?cp /var/cache/apt/archives/*.deb /output/apt/

echo 'Installing Python/Pip for wheel download...'
# 鍏堝畨瑁?pip 浠ヤ究涓嬭浇 Python 鍖?DEBIAN_FRONTEND=noninteractive apt-get install -y python3-pip python3-venv

echo 'Downloading PyPI packages...'
# 閰嶇疆 pip 婧?pip3 config set global.index-url https://mirrors.aliyun.com/pypi/simple/

# 涓嬭浇 wheel
pip3 download -d /output/pip pptx2md
pip3 download -d /output/pip -r /input/requirements.txt

echo 'Done!'
chown -R $(id -u):$(id -g) /output