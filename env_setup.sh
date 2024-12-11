#!/bin/bash

module load python/3.10
module load scipy-stack

virtualenv jupyter_sklearn
source ./jupyter_sklearn/bin/activate

pip install --no-index --upgrade pip
pip install --no-index scikit_learn
pip install --no-index jupyter
pip install --no-index tqdm

echo "Done!"
