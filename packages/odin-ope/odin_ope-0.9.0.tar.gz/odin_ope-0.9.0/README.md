# ODIN OPE (Open Proof Envelope)

**Lightweight, production-grade primitives for verifiable AI↔AI / AI↔Human communication.**  
This package gives you *deterministic canonical JSON*, *CID hashing*, *Ed25519 signatures*,
and helpers to *build/verify envelopes & export bundles* used across the ODIN ecosystem.

- **Deterministic canonical JSON** → stable hashes and signatures
- **CID**: `sha256:<hex>` computed over canonical bytes
- **Envelope signing**: sign `"{cid}|{trace_id}|{ts}"` with Ed25519
- **Bundle signing**: sign `"{bundle_cid}|{trace_id}|{exported_at}"`
- **Signer backends**: local seed (default). Optional extras for GCP KMS / AWS KMS / Azure KV.

**Install**
```bash
pip install odin-ope
# or with extras: pip install "odin-ope[gcpkms]"  # etc.
```

---

## Quick start

```python
from odin_ope.signers import FileSigner
from odin_ope.envelope import build_envelope, sign_envelope
from odin_ope.verify import verify_envelope, build_jwks_for_signers
from odin_ope.bundle import build_bundle, sign_bundle, verify_bundle

# 1. Create a signer (Ed25519, deterministic seed for demo)
seed_b64u = "A"*43  # 32-byte Ed25519 seed as base64url (example placeholder)
signer = FileSigner(seed_b64u=seed_b64u)  # kid derived from public key

# 2. Build and sign an envelope
payload = {"invoice_id": "INV-1", "amount": 100.25, "currency": "USD"}
env = build_envelope(payload, payload_type="openai.tooluse.invoice.v1", target_type="invoice.iso20022.v1")
signed_env = sign_envelope(env, signer)

# 3. Build JWKS and verify the envelope
jwks = build_jwks_for_signers([signer])

ok, reason = verify_envelope(signed_env, jwks)
assert ok, reason  # (or use verify_envelope_or_raise for exceptions)

# 4. Create and sign a bundle
receipts = [
    {"hop": 0, "receipt_hash": "h0", "prev_receipt_hash": None},
    {"hop": 1, "receipt_hash": "h1", "prev_receipt_hash": "h0"}
]
bundle = build_bundle(trace_id=signed_env["trace_id"], receipts=receipts)
sig = sign_bundle(bundle, signer)
ok2, reason2 = verify_bundle(bundle, sig, jwks, kid=signer.kid)
assert ok2, reason2
```

See `examples/end_to_end.py` for a full, annotated script.

---

## FAQ: Common errors

**Q: `ModuleNotFoundError: No module named 'odin_ope'`**
A: Make sure your `PYTHONPATH` includes the `src` directory, or install the package in editable mode: `pip install -e .`

**Q: `ValueError: Ed25519 seed must be 32 bytes`**
A: The seed for `FileSigner` must be a base64url-encoded string representing exactly 32 bytes.

**Q: Envelope verification fails with `cid_mismatch`**
A: The payload was likely modified after signing. Always verify before mutating envelopes.

**Q: How do I generate a valid Ed25519 seed?**
A: Use `os.urandom(32)` and encode with `base64.urlsafe_b64encode(seed).rstrip(b'=')`.

**Q: How do I run the tests?**
A: `PYTHONPATH=src pytest` (or on Windows: `$env:PYTHONPATH='src'; python -m pytest`)

## Reason Codes

| Code | Meaning |
|------|---------|
| cid_mismatch | Payload hash changed after signing |
| missing_sig_or_kid | Envelope missing sender_sig or kid |
| kid_not_found | KID not present in supplied JWKS |
| signature_invalid | Signature verification failed |
| timestamp_skew | ts outside allowed skew window |
| schema_error | Structural or field validation error |
| not_yet_valid | not_before is in the future |
| expired | expires_at is in the past |

These map 1:1 to exception subclasses (see `odin_ope.exceptions`).

## CLI

The package installs a `odin-ope` CLI:

```
odin-ope sign-envelope --payload payload.json --payload-type t --target-type tgt --seed <base64url-seed>
odin-ope verify-envelope --envelope env.json --jwks jwks.json --json --max-skew 300 --strict
```
Use `--json` for structured output and `--no-skew` to disable time skew checks.

## Development

Install dev extras and run tests + type checking:

```
pip install -e .[dev]
pytest -q
mypy src/odin_ope
python scripts/gen_sbom.py --out sbom.json  # generate CycloneDX SBOM
```

Programmatic version: `import odin_ope; print(odin_ope.__version__)`.
\n+## Development
\n+Install dev extras and run tests + type checking:
\n+```
pip install -e .[dev]
pytest -q
mypy src/odin_ope
```
## Publishing
## Publishing

A GitHub Actions workflow is included (`.github/workflows/publish.yml`).  
Create a repository, push, add `PYPI_API_TOKEN` secret, then tag a release like `v0.9.0`.
The workflow produces:
- Signed artifacts published to PyPI
- CycloneDX SBOM artifact (download from workflow run)
- Build provenance attestation (GitHub Attestations UI / API)

---

## License

Apache-2.0
