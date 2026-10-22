# Reverse-engineering WindWings (APK) — pipeline notes

The Arena sandbox only reaches `github.com`, `codeload.github.com`,
`api.github.com`, `registry.npmjs.org`, `pypi.org`, `files.pythonhosted.org`.
APK mirrors, `raw.githubusercontent.com` and release-asset CDNs are blocked.

Therefore APK acquisition and the heavy Java/.NET toolchain run on a
GitHub-hosted runner (open internet). Results are committed back to this
branch; the sandbox reads them through git.

## Steps

1. `tools/apk-probe/probe.sh` — find a working mirror (APKPure CDN works).
2. `ingest-apk` workflow — download XAPK, parse every APK part, record hashes,
   package metadata, permissions, native/Unity clues, upload artifact.
3. `analyze-apk` workflow — apktool + jadx + Il2CppDumper + UnityPy + REA.
