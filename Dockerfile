FROM public.ecr.aws/lambda/python:3.11

WORKDIR /var/task

COPY requirements.txt ./

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY ./app/. ./

CMD ["main.handler"]