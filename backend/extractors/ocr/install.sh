# Install python3.8
apt-get update -y

apt-get install python3.8 -y

apt-get install python3.8-distutils
python3.8 get-pip.py

# DeepSolo
cd DeepSolo
apt-get install python3.8-dev -y
apt-get install build-essential -y
python3.8 -m pip install torch==1.9.0+cu111 torchvision==0.10.0+cu111 -f https://download.pytorch.org/whl/torch_stable.html
python3.8 -m pip install -r requirements.txt
python3.8 -m pip install detectron2 -f https://dl.fbaipublicfiles.com/detectron2/wheels/cu111/torch1.9/index.html
python3.8 setup.py build develop

# Parseq
cd ../parseq
python3.8 -m pip install -r requirements/parseq.txt -e .[train,test]
python3.8 -m pip install pytorch_lightning torch==1.9

apt-get install ffmpeg libsm6 libxext6  -y