FROM nlzimmerman/alpine-anaconda3

RUN conda install -y --no-update-deps ipython-notebook=4.0.4
ADD jupyter_notebook_config.py /root/.jupyter/

# Yahoo-finance dependencies that _are_ in anaconda
RUN conda install -y --no-update-deps pytz=2016.10 simplejson=3.10.0
RUN pip install yahoo-finance==1.4.0


EXPOSE 8888
VOLUME [ "/notebooks", "/python" ]
CMD [ "jupyter", "notebook" ]
