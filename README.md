# VBSStudies02
The VBSStudies01 consists of initial checks whereas this repo is for full analysis

Setup in CIS:

    salloc srun --pty bash -l
    wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh
    bash Miniforge3-Linux-x86_64.sh
    conda create --name myenv
    conda activate myenv
    conda install -c conda-forge root or conda install -c conda-forge root=6.30.09
    python3 -m pip install --user --no-binary=correctionlib correctionlib
    conda install -c conda-forge boost boost-cpp
    conda install -c conda-forge mkl
    export LD_LIBRARY_PATH=/mnt/home/mghimiray/miniforge3/envs/myenv/lib:$LD_LIBRARY_PATH

    eval "$(/mnt/home/mghimiray/miniforge3/bin/conda shell.bash hook)"
    conda activate myenv

To run:
  python3 sswwAnalysis.py --year=20230 --process=1042 --whichJob=0

To remove a package:
  conda remove root --force

For cmsstyle:
    git clone https://github.com/cms-cat/cmsstyle.git
    cd cmsstyle
    source scripts/setup_cmstyle
    /mnt/home/mghimiray/VBSStudies/cmsstyle/cmsstyle/
    source /mnt/home/mghimiray/VBSStudies/cmsstyle/cmsstyle/scripts/setup_cmstyle 
    
    
export LD_PRELOAD=/mnt/home/mghimiray/miniforge3/envs/root630env/x86_64-conda-linux-gnu/lib/libstdc++.so.6
    python3 sswwAnalysis.py --year=20230 --process=1042 --whichJob=0



