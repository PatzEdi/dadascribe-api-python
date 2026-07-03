# Python wrapper for the DaDaScribe API

The official DaDaScribe API wrapper in Python.

![DaDaScribe Logo](https://www.dadascribe.com/images/DaDaScribeLogo.svg)

## CLI Interface
The wrapper offers a CLI interface.

To start a job, for example:
```bash
$ dadascribe --source "link/to/youtube/or/path/to/file"
{
  "status": "ok",
  "id": "a7wuTaPrebOqheE0",
  "count": 1
}
```

Check a job status:
```bash
$ dadascribe --status a7wuTaPrebOqheE0
```

Easily download results of a completed job:
```bash
$ dadadascribe --download a7wuTaPrebOqheE0
```

## Python API
The wrapper offers a Python API.

```python
from dadascribe import ScribeAPIWrapper
api_key = ... # e.g. from an environment variable, as str
w = ScribeAPIWrapper(api_key)

# Example transcription:
trsc_result = w.transcribe(
    source="youtube/link/or/path/to/file",
    source_language="en",
    destination_language="es,it",
)
```


## Development
```bash
pip3 install -e .
```

Make sure to run the tests as well via the run_tests.sh script:
```bash
chmod +x run_tests.sh
./run_tests.sh
```
