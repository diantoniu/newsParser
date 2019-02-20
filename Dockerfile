FROM ubuntu:18.04

RUN apt-get update
RUN apt-get install -yq software-properties-common

RUN add-apt-repository ppa:jonathonf/python-3.6
RUN apt-get update

RUN apt-get install -yq python3.6 libpython3.6

#RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.5 1
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.6 1

RUN rm /usr/bin/python3
RUN ln -s python3.6 /usr/bin/python3

RUN apt-get update
RUN apt-get install -yq python3-pip
RUN pip3 install --upgrade pip

WORKDIR /project
COPY . /project

RUN pip3 install -r requirements.txt
#mysqlclient==1.3.10

EXPOSE 8000

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]

# to build
# $ docker build -t dinutss/news_parser .
# to run
# $ docker run -p 80:8000 -it --rm dinutss/news_parser
# to push
# $ docker push dinutss/news_parser