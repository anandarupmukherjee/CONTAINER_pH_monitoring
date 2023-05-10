FROM python:3.9

RUN pip3 install CherryPy
RUN pip3 install pandas
RUN pip3 install jinja2
RUN pip3 install openpyxl

COPY . .

EXPOSE 9000

CMD [ "python3", "server.py"]