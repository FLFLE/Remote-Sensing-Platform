# 平台在线体验

在线体验地址：[www.scuzfy.com](http://www.scuzfy.com)

[Scu·Earth](http://www.scuzfy.com)

由于服务器硬件和内网穿透带宽浪费，在线体验的性能要差于本地部署，推荐在使用每个功能时，每次只上传一张或者一对遥感图像，以避免网络超时。

# 所需环境

```python
# cuda环境
CUDA == 10.2

# paddle环境
paddlepaddle == 2.3
paddlers == 1.0b0

# 前端环境
vue == 3.0

# 数据库环境
MySQL == 8.0.14

# 后端环境
python == 3.7
Django==3.2.13
djangorestframework==3.13.1
numpy==1.19.3
opencv_python==4.5.5.64
paddlers==1.0b0
Pillow==9.1.1
PyMySQL==1.0.2
```

# 环境配置

## paddlepaddle安装:

### CUDA安装：

paddlepaddle安装需要依赖CUDA环境.，本次开发的环境是CUDA10.2。

如果您使用的是安培架构的GPU（NVIDIA GeForce 30系列），推荐使用CUDA11以上，非安培架构CPU推荐使用CUDA10.2。

CUDA各版本下载地址：（paddlepaddle目前支持快速安装的CUDA版本为10.1—11.2，其他版本需自行下载源码编译）

[CUDA Toolkit Archive](https://developer.nvidia.com/cuda-toolkit-archive)

下载完成后依照默认安装程序逐步执行即可。

### cuDNN安装：

下载地址：

[](https://developer.nvidia.com/rdp/cudnn-download)

登录或注册账号后，下载与CUDA相对应版本的cuDNN，得到一个压缩包，将压缩包中的bin，include，lib目录下的文件复制到CUDA安装目录下的同名文件夹内。

### 验证安装：

控制台执行 `nvcc -V` 显示版本号则安装成功。

### 安装paddlepaddle：

- 确认python版本：

  - 使用以下命令确认python版本为3.7/3.8：

  ```powershell
  python --version
  ```

- 确认pip版本是否为20.2.2或更高版本：

  ```powershell
  python -m pip --version
  ```

  如果pip版本不符合要求，使用如下命令更新：

  ```powershell
  python -m pip install --upgrade pip
  ```

- 使用以下命令确认python和pip是64bit，并且处理器是x86_64：

  ```powershell
  python -c "import platform;print(platform.architecture()[0]);print(platform.machine())"
  ```

  输出结果的第一行为64bit，第二行输出为”x86_64”、”x64”或”AMD64”即可

- CUDA安装成功后，根据安装的CUDA版本，执行对应的安装指令（以CUDA 10.2为例）

  ```powershell
  python -m pip install paddlepaddle-gpu==2.3.0 -i https://mirror.baidu.com/pypi/simple
  ```

  其它CUDA版本安装指令见paddlepaddle官网：

  [开始使用_飞桨-源于产业实践的开源深度学习平台](https://www.paddlepaddle.org.cn/install/quick?docurl=/documentation/docs/zh/install/pip/windows-pip.html)

### 验证安装：

安装完成后您可以使用 `python` 进入python解释器，输入`import paddle` ，再输入 `paddle.utils.run_check()`  ，如果出现`PaddlePaddle is installed successfully!`，说明您已成功安装。

## paddlers安装：

### 方式一：

依次执行下列指令：

```bash
git clone https://github.com/PaddleCV-SIG/PaddleRS
cd PaddleRS
git checkout develop
pip install -r requirements.txt
python setup.py install
```

### 方式二：

windows同样可以通过下列链接，选择与自己对应的python和系统版本的二进制文件：

[Archived: Python Extension Packages for Windows - Christoph Gohlke](https://www.lfd.uci.edu/~gohlke/pythonlibs/#gdal)

以 *`GDAL‑3.3.3‑cp37-cp37‑win_amd64.whl`*为例,下载完成后进入下载目录并执行安装指令

```bash
cd {download} #download代表本机的下载保存目录
pip install  GDAL‑3.3.3‑cp37-cp37‑win_amd64.whl
```

## vue 3.0安装：

### 安装node.js

进入Node.js官网下载稳定版本的64位Node.js的windows安装包(.msi):

[下载](http://nodejs.cn/download/)

逐步按照默认安装程序完成安装。

### 安装npm国内镜像cnpm

```bash
npm install -g cnpm --registry=registry.npm.taobao.org
```

### 安装vue及相关工具

```bash
cnpm install -g vue
cnpm install -g webpack
cnpm install -g express
cnpm install @vue/cli -g
```

### 验证安装

```bash
vue -V
```

## Django及其它python依赖安装：

进入到 `requirements.txt` 所在目录，执行下列命令：

```bash
pip install -r requirements.txt
```

# 项目运行

## 前端启动：

进入到frontend文件夹，执行下列命令：

```bash
npm install
npm run serve
```

## 后端启动：

### 数据库配置

在MySQL中新建数据库，修改项目`backend/backend` 目录下`settings.py` 文件第118行——127行配置项

```python
DATABASES = {
      'default': {  
        'ENGINE': 'django.db.backends.mysql',  
        'NAME': 'paddle',  
        'USER': 'root',  
        'PASSWORD': 'goodnight',  
        'HOST': '127.0.0.1',  
        'PORT': '3306',  
      }
}
```

将 `name`, `user` , `password` , `port` 分别修改为您自己的 `前面新创建的数据库名` , `登录mysql的用户名` , `mysql登陆密码` , `mysql运行端口` 

> 如果您不想修该源代码配置，可以直接将新建的数据库命名为paddle，数据库密码设置为goodnight

### 运行项目

进入到backend文件夹，执行下列命令：

```bash
# 执行数据迁移
python [absolute path]/manage.py makemigrations
python [absolute path]/manage.py makemigrate

# 运行项目
python [absolute path]/manage.py runserver 0.0.0.0:8000 
#[absolute path]/manage.py为项目文件中manage.py文件的绝对路径

```

## 访问网站

浏览器中访问 `127.0.0.1:8080` 

# 项目github地址

[https://github.com/FLFLE/Remote-Sensing-Platform](https://github.com/FLFLE/Remote-Sensing-Platform)
