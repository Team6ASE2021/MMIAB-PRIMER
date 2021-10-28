FROM python:3.6

ADD ./ /code
WORKDIR /code

#ENV PATH .:$PATH
RUN pip install -r requirements.txt
RUN python setup.py develop
EXPOSE 5000
CMD ["bash", "run.sh"]
