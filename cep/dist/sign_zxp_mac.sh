#!/bin/bash
# Make a signed WordWave.zxp for distribution (macOS). Needs ZXPSignCmd (Adobe CEP-Resources, "ZXPSignCMD")
# next to this file or on PATH. The self-signed certificate is created once (wordwave_cert.p12) and reused.
set -e
cd "$(dirname "$0")"
Z=./ZXPSignCmd; [ -x "$Z" ] || Z=ZXPSignCmd
PASS="${WORDWAVE_CERT_PASS:-change-this-password}"
[ -f wordwave_cert.p12 ] || "$Z" -selfSignedCert JP Tokyo hakoniwa WordWave "$PASS" wordwave_cert.p12
rm -f WordWave.zxp
"$Z" -sign com.852wa.jizura WordWave.zxp wordwave_cert.p12 "$PASS" -tsa http://timestamp.digicert.com
"$Z" -verify WordWave.zxp
echo "WordWave.zxp ready"
