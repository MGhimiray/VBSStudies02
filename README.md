<<<<<<< HEAD
# VBSStudies
=======
# VBSStudies02
The VBSStudies01 consists of initial checks whereas this repo is for full analysis
<<<<<<< HEAD
>>>>>>> 3402d9045d03499789d2cd396b7325d98346a01b
=======

To run it in CIS:

    salloc srun --pty bash -l
    wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh
    bash Miniforge3-Linux-x86_64.sh
    conda create --name myenv
    conda activate myenv
    conda install -c conda-forge root
    python3 -m pip install --user --no-binary=correctionlib correctionlib
    conda install -c conda-forge boost boost-cpp
    eval "$(/mnt/home/mghimiray/miniforge3/bin/conda shell.bash hook)"
    conda activate myenv
>>>>>>> a45e8918ab1fbf5c0de63ada27d24ea1b871c4b3
