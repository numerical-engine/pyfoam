# pyfoam
OpenFOAMを操作するためのPythonモジュール

## 環境構築
本モジュールはOpenFOAM v9の利用を想定。Ubuntu22.04及びPython3.10.12で動作確認をした。
### OpenFOAM
<https://openfoam.org/download/9-ubuntu/>に従い以下のコマンドを実行した。
```
sudo sh -c "wget -O - https://dl.openfoam.org/gpg.key > /etc/apt/trusted.gpg.d/openfoam.asc"
sudo add-apt-repository http://dl.openfoam.org/ubuntu
sudo apt-get update
sudo apt-get -y install openfoam9
source /opt/openfoam9/etc/bashrc
```