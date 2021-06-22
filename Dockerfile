##
## Test base image with
## > docker run -i -t continuumio/miniconda3 /bin/bash
##
## (Re-)Build image
## > docker image rm gwas-app
## > docker build -t gwas-app .
##
## Run app
## > docker run -p 5000:5000 --rm gwas-app
##
## Run a shell
## > docker run -p 5000:5000 --rm -i -t gwas-app /bin/bash
##
FROM continuumio/miniconda3:latest
SHELL ["/bin/bash", "-c"]
RUN apt-get update && apt-get upgrade -y  && apt-get install -y g++ && \
    rm -rf /var/lib/apt/lists/* && \
    conda update -y -n base -c defaults conda && \
    useradd -m -u 1000 -s /bin/bash gwas && \
    conda install -y mkl==2019.4 scipy numpy && \
    su -l gwas && \
    cd /home/gwas && \
    conda init bash && \
    source /home/gwas/.bashrc && \
    pip install --no-build-isolation fastlmm && \
    git clone https://github.com/Xenokrates/gwas_web_production.git && \
    cd gwas_web_production/ && \
    chown 1000:1000 data/results && \
    chown -R 1000:1000 ./ && \
    chown 1000:1000 data/uploads && \
    pip install -r requirements.txt

USER 1000
WORKDIR /home/gwas/gwas_web_production
EXPOSE 5000/tcp
ENTRYPOINT [ "/bin/bash", "-l", "-c" ]
CMD ["FLASK_APP=main_app.py /opt/conda/bin/python -m flask run --host=0.0.0.0"]
