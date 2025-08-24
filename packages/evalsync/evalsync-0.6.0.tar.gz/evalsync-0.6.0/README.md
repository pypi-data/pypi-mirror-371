# EvalSync

## Development

### Setup

Install dependencies:
```bash
uv sync --group dev
```

### Generate Protobuf Proto

```bash
protoc --proto_path=../proto --python_out=src/evalsync/proto --mypy_out=src/evalsync/proto ../proto/sync.proto
```

### Running Tests

```bash
uv run pytest
```

### Linting and Type Checking

```bash
uv run ruff check
uv run mypy src/
```

### Submit to PyPI

```bash
uv build
uv publish
```
