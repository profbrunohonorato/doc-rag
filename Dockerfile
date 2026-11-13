FROM python:3.12-slim
WORKDIR /app
COPY Presentation/API/requirements.lock.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY Application /app/Application
COPY Domain /app/Domain
COPY Infra /app/Infra
COPY Presentation/API /app/Presentation/API
RUN useradd --uid 10001 --create-home app && mkdir -p /app/data /documents/_uploads && chown -R app:app /app /documents
USER app
EXPOSE 9090
CMD ["uvicorn", "Presentation.API.main:app", "--host", "0.0.0.0", "--port", "9090"]
