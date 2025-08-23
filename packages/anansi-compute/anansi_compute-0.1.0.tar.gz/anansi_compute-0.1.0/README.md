# Anansi Compute

Secure multi-cloud compute orchestration with CPU TEE and GPU Confidential Computing support.

## Quick Start (30 seconds)

```python
# 1) Install
%pip install anansi-compute==0.1.0

# 2) Configure
import anansi
anansi.configure(
    endpoint="https://api.rewsr.com",
    api_key="your_api_key_here"
)

# 3) Run secure computation
result = anansi.compute(
    fn="vec_add",
    args=([1, 2, 3], [10, 20, 30]),
    policy={"min_trust": "GPU_CC", "allowed_clouds": ["azure", "gcp"]}
)
print(result["result"])  # [11, 22, 33]
```

## Features

- **CPU TEE Support**: AMD SEV-SNP, Intel TDX protection
- **GPU Confidential Computing**: NVIDIA H100 with attestation
- **Multi-cloud**: Auto-route across AWS, Azure, GCP based on policy
- **Cost Control**: Built-in budget limits and optimization
- **Verifiable**: Cryptographic attestation and audit trails

## Supported Platforms

- **Databricks**: Drop-in replacement for compute workloads
- **Snowflake**: External functions for SQL integration
- **Jupyter/Python**: Direct API access
- **REST**: Universal HTTP interface

## Documentation

- [Getting Started Guide](https://docs.rewsr.com/getting-started)
- [API Reference](https://docs.rewsr.com/api)
- [Examples](https://github.com/rewsr/anansi-compute/tree/main/examples)

## License

MIT License - see [LICENSE](LICENSE) file.