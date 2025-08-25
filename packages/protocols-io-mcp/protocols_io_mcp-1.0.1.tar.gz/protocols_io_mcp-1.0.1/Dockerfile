FROM python:3.13-slim

ENV PYTHONUNBUFFERED=True
ENV PYTHONDONTWRITEBYTECODE=True

RUN pip install uv

WORKDIR /app
COPY pyproject.toml .
COPY README.md .
COPY src ./src
RUN uv pip install --system .

EXPOSE 8000
CMD ["protocols-io-mcp", "--transport", "http", "--host", "0.0.0.0", "--port", "8000"]