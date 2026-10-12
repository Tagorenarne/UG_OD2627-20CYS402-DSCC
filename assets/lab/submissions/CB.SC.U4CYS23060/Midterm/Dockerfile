FROM python:3.13-slim
ENV ROLLNUMBER="CB.SC.U4CYS23060"
ENV NAME="RAAHUL SIVAKUMAR"
LABEL EMAIL = "cb.sc.u4cys23060@cb.students.amrita.edu"
LABEL PRODUCTION_VERSION = "1.0"
WORKDIR /midterm-exam
COPY web/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY web/ .
EXPOSE 8000
CMD ["python","app.py"]


