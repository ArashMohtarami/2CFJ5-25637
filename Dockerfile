FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /code

RUN useradd -m appuser && chown -R appuser /code
USER appuser

COPY --chown=appuser:appuser requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY --chown=appuser:appuser . .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
