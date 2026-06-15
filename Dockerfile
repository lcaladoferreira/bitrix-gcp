FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src
RUN groupadd -r appgroup && useradd -r -g appgroup appuser
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ /app/src/
RUN chown -R appuser:appgroup /app
USER appuser
ENTRYPOINT ["python", "-m", "bitrix_gcp.main"]
