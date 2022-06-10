FROM python:3.8-slim
ENV PYTHONUNBUFFERED=1

WORKDIR /Instagram-Clone-Backend

# RUN apk add --update --no-cache postgresql-client jpeg-dev

# RUN apk add --update --no-cache --virtual .tmp-build-deps \ 
#     gcc libc-dev linux-headers postgresql-dev musl-dev zlib zlib-dev
# RUN apk del .tmp-build-deps


COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
# RUN postgres psql

COPY . .

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]