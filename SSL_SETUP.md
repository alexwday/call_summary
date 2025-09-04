# SSL Certificate Setup for Corporate Environments

## Overview
This application supports custom SSL certificates for corporate environments where internet access goes through proxy servers with custom certificate authorities.

## Setup Instructions

### 1. Place Your Certificate
Copy your corporate SSL certificate bundle to the project root:
```bash
cp /path/to/your/rbc-ca-bundle.cer ./rbc-ca-bundle.cer
```

The certificate file should be named exactly: `rbc-ca-bundle.cer`

### 2. Run the Application
The `run.sh` script will automatically detect and use the certificate:
```bash
./run.sh
```

## How It Works

### Automatic Detection
- If `rbc-ca-bundle.cer` exists: SSL verification is enabled with your certificate
- If no certificate found: Runs in development mode without SSL verification

### Environment Variables Set
When a certificate is detected, the following are configured:
- `REQUESTS_CA_BUNDLE` - For Python requests library
- `SSL_CERT_FILE` - For general SSL operations  
- `CURL_CA_BUNDLE` - For curl operations
- `PIP_CERT` - For pip installations

### Model Downloads
The SSL configuration ensures:
- Whisper models download from HuggingFace with proper SSL
- Kokoro TTS models download with SSL verification
- All API calls respect the certificate

## Pre-downloading Models

If you need to download models separately (useful in restricted environments):

```bash
# With certificate
./venv/bin/python download_models.py

# Or specify certificate path
./venv/bin/python download_models.py /path/to/certificate.cer
```

## Troubleshooting

### SSL Certificate Errors
If you see SSL errors like:
- `SSL: CERTIFICATE_VERIFY_FAILED`
- `unable to get local issuer certificate`

**Solutions:**
1. Ensure `rbc-ca-bundle.cer` is in the project root
2. Verify the certificate is valid: `openssl x509 -in rbc-ca-bundle.cer -text -noout`
3. Try running without SSL verification (development only):
   ```bash
   export SSL_VERIFY=false
   ./run.sh
   ```

### Behind Corporate Proxy
If behind a proxy, also set:
```bash
export HTTP_PROXY=http://your.proxy:port
export HTTPS_PROXY=http://your.proxy:port
export NO_PROXY=localhost,127.0.0.1
```

### Model Download Issues
If models fail to download:
1. Pre-download using the download script
2. Check proxy settings
3. Verify certificate is correctly configured
4. Try with SSL verification disabled (development only)

## Security Notes

- **Production**: Always use proper SSL certificates
- **Development**: SSL verification can be disabled but should never be done in production
- **Certificate Updates**: Update `rbc-ca-bundle.cer` when corporate certificates change

## Supported Formats

The certificate file can be in:
- `.cer` format (DER or PEM encoded)
- `.pem` format
- `.crt` format (rename to `.cer`)

For bundle files containing multiple certificates, ensure they're concatenated properly.