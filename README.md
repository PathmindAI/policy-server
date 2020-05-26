# Pathmind Policy Server Prototype 

```bash
python generate.py schema examples/lpoc/schema.yaml
```


## TODOs and things to look out for

- For faster inference, we should switch to TensorFlow Serving internally. 
Not necessarily difficult, just needs to be done. TF Serving
- TensorFlow GPU usage
- Proper SSL/TLS support
- Proper password management
- OAuth support
- PyTorch support
- Do we need proper hot reloading of models?

Use `chrome://flags/#allow-insecure-localhost` and confirm. On MacOS paste your
certificate into Keychain and mark it as trusted.
 

