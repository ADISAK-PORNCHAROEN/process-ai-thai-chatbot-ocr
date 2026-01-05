FROM python:3.11-alpine AS builder

WORKDIR /app

RUN apk add --no-cache \
    gcc \
    g++ \
    musl-dev \
    linux-headers \
    libffi-dev \
    cmake \
    make \
    rust \
    cargo \
    postgresql-dev \
    mupdf-dev \
    jbig2dec-dev \
    openjpeg-dev \
    freetype-dev

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --no-cache-dir --upgrade pip setuptools wheel
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11-alpine
WORKDIR /app

RUN apk add --no-cache libstdc++ mupdf

COPY --from=builder /opt/venv /opt/venv
COPY . .

ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUTF8=1

CMD ["python", "-X", "utf8", "app.py"]