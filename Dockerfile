FROM python:3.9

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

RUN pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
RUN pip install easyocr

COPY . /app/

EXPOSE 8080

CMD [ "uvicorn","server:app","--host","0.0.0.0","--port","8080"]
