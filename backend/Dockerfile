FROM python:3.12
                                       
WORKDIR /app
                      
COPY requirements.txt .
                             
RUN pip install -r requirements.txt --no-cache-dir
                                             
COPY . .

COPY ../docs/ .

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "backend.wsgi"]