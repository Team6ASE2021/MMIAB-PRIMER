FROM python:3.6

ADD ./ /code
WORKDIR /code

#ENV PATH .:$PATH
RUN apt-get update -y
RUN apt-get install -y tzdata
ENV TZ Europe/Rome
RUN pip install -r requirements.txt
RUN python setup.py develop
EXPOSE 5000
CMD ["bash", "run.sh"]
