exeファイルへの変換について
===========================

Nuitka や py2exe を使えば、Pythonスクリプトをexeファイルに変換できる。

Nuitkaでexeファイル化
---------------------

Nuitka の利用には、Cコンパイラ(MSVC or MinGW64)が必要。

今回は以下の環境でexe化を試した。

* Windows10 x64 22H2
* Python 3.10.10 64bit
* Nuitka 2.2.3
* Microsoft Visual Studio Community 2022

### Python仮想環境の作成

Pythonの仮想環境を作成して、動作に必要なモジュールをインストールする。

```
python -m venv venv
venv\Scripts\activate.bat

python -m pip install --upgrade pip
python -m pip install --upgrade setuptools
python -m pip install pyautogui
python -m pip install pynput
```

Nuitkaをインストールする。

```
python -m pip install nuitka
```

### Nuitkaで変換

Nuitka でexeファイル化する。

```
python -m nuitka --standalone --enable-plugin=tk-inter --windows-disable-console pyrgbfloatviewer.pyw
```

仮想環境から抜ける。

```
deactivate
```

### 動作確認

`pyrgbfloatviewer.dist` ディレクトリが出来上がるので、別の環境にコピー。

中にある `pyrgbfloatviewer.exe` を実行すれば起動する。

py2exeでexeファイル化
---------------------

py2exe でexeファイル化できることも確認できた。

* Windows10 x64 22H2
* Python 3.10.10 64bit
* py2exe 0.13.0.1

仮想環境の作成と切替、必要なモジュールのインストールは、Nuitka と同じ。

Nuitka の代わりに、py2exe をインストールする。

```
python -m pip install py2exe
```

注意点。2024/05/27現在、pynput を使っているPythonスクリプトを py2exeを利用してexe化する場合は、pynput 1.6.8にダウングレードしないと import error が出る。

* [python 3.x - Getting error when using pynput with pyinstaller - Stack Overflow](https://stackoverflow.com/questions/63681770/getting-error-when-using-pynput-with-pyinstaller)
* [ImportError when using PyInstaller - Issue #312 - moses-palmer/pynput](https://github.com/moses-palmer/pynput/issues/312)

```
python -m pip install pynput==1.6.8
```

setup.py を作成。

```python
from distutils.core import setup
import py2exe

setup(windows = [{"script": "pyrgbfloatviewer.pyw"}])
```

py2exe でexe化する。

```
python setup.py py2exe
```

`dist/`ディレクトリが出来上がるので、別の環境にコピー。

中にある `pyrgbfloatviewer.exe` を実行すれば起動する。

