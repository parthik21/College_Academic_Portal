FROM ubuntu:latest
LABEL "Author"="Parthik"
LABEL "Project"="College_academic_portal"
RUN apt update && apt install git -y
RUN apt install python3 -y
RUN apt install python3-pip -y
RUN pip3 install django==4.0.1
RUN pip3 install pillow
RUN pip3 install djangorestframework
RUN pip3 install django-filter
RUN pip3 install markdown
RUN pip3 install django-cors-headers
RUN pip3 install tzdata
RUN pip3 install beautifulsoup4==4.9.1
RUN pip3 install cffi==1.14.0
RUN pip3 install django-bootstrap4==1.1.1
RUN pip3 install django-misaka==0.2.1
RUN pip3 install houdini.py==0.1.0
RUN pip3 install misaka==2.1.1
RUN pip3 install pycparser==2.20
RUN pip3 install Pygments==2.6.1
RUN pip3 install pytz==2020.1
RUN pip3 install soupsieve==2.0.1
RUN pip3 install sqlparse==0.3.1
RUN pip3 install pillow
RUN pip3 install pillow
WORKDIR /home
EXPOSE 8000
RUN git init
RUN git pull https://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@github.com/parthik21/college_academic_portal.git
CMD ["python3", "./manage.py", "runserver", "0.0.0.0:8000"]
