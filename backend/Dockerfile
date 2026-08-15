FROM python:3.13-alpine AS builder
WORKDIR /app
RUN apk add --no-cache \
    build-base \
    libffi-dev \
    musl-dev
COPY requirements.txt .
RUN pip install \
    --no-cache-dir \
    --prefix=/install \
    -r requirements.txt

FROM python:3.13-alpine AS runtime
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
RUN apk add --no-cache \
    libffi
COPY --from=builder /install /usr/local
COPY . .
RUN addgroup -S appgroup \
    && adduser -S appuser -G appgroup \
    && chown -R appuser:appgroup /app
USER appuser
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
