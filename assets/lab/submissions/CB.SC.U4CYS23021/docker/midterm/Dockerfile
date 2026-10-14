FROM python:3.12-slim

ENV ROLLNUMBER="cb.sc.u4cys23021"
ENV NAME="K.C.K.SANJAI"

LABEL EMAIL="cb.sc.u4cys23021@cb.students.amrita.edu"
LABEL PRODUCTION_VERSION="1.0"

WORKDIR /midterm-exam

RUN pip install --no-cache-dir flask psycopg2-binary

COPY web/ /midterm-exam/

EXPOSE 5000

CMD ["python", "app.py"]
