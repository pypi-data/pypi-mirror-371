# fatehan

### gRPC/Protobuf message & service stubs.

## Install

```bash
pip install fatehan-pypb
```

## GRPC Usage

```python
import grpc
from services import api_pb2, api_pb2_grpc

channel = grpc.insecure_channel("localhost:50051")
stub = api_pb2_grpc.ApiService(channel) 
resp = stub.DeviceIndex(api_pb2.DeviceRequest(page=1, page_size=25))
print(resp)
```

## Compile

```bash
python -m grpc_tools.protoc \
  -I ../protocols \
  --python_out=. \
  --grpc_python_out=. \
  --pyi_out=. \
  $(find ../protocols -name "*.proto" -print)
```

## Build And Test Locally
```bash
python -m pip install --upgrade build twine
python -m build
python -m twine check dist/*
```

## Try a local install
```bash
python -m venv .venv && . .venv/bin/activate
pip install dist/fatehan-0.2.0-py3-none-any.whl
python -c "from devices import devices_pb2; print('ok', bool(devices_pb2))"
```

## Publish
```bash
python -m twine upload dist/*
```