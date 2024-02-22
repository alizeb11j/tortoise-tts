#Steps for Running on Windows
Goto https://www.python.org/downloads/release/python-3108/
Download Windows installer (64-bit)
Verify you have correct version of python
    py --version    
    git clone https://github.com/neonbjb/tortoise-tts.git
    cd tortoise-tts
    py -m pip install -r ./requirements.txt
    pip install pysoundfile
    pip install libsndfile1
    pip install torchaudio==2.0.1
    py -m pip  install psutil
    py setup.py install
    py tortoise/do_tts.py --text "I'm going to speak this" --voice random --preset fast

    ##(This takes about 2.2GB)
    py -m pip install torch==1.11.0+cu113 torchvision==0.12.0+cu113 torchaudio===0.11.0+cu113 -f https://download.pytorch.org/whl/cu113/torch_stable.html

    To verify GPU Usage
    py -c "import torch; print(torch.cuda.is_available());torch.zeros(1).cuda()"



