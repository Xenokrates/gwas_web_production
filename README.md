# gwas_web_production

Install in a conda environment (Miniconda or Anaconda)


````
conda install mkl==2019.4 scipy numpy
pip install --no-build-isolation fastlmm
git clone https://github.com/snowformatics/gwas_web_production.git

cd myfolder/gwas_web_production

pip install -r requirements.txt

python main_app.py
````

to update

````
pip pull
````
