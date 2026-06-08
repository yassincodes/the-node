# Apple setup — one time, then Adopt works for everyone

Without this, macOS blocks strangers from opening a download. There is no code workaround. Apple requires it.

**Cost:** $99/year — [Apple Developer Program](https://developer.apple.com/programs/)

**Time:** ~20 minutes once. After that, every Adopt click works for your mom, brother, anyone.

---

## 1. Enroll

Sign up at developer.apple.com → Programs → enroll as Individual.

---

## 2. Create a signing certificate

1. Xcode → Settings → Accounts → your Apple ID → Manage Certificates
2. Click **+** → **Developer ID Application**
3. Or: [Certificates portal](https://developer.apple.com/account/resources/certificates/list) → **+** → Developer ID Application

Export as `.p12` (password-protected). Keep it safe.

---

## 3. App-specific password

appleid.apple.com → Sign-In and Security → App-Specific Passwords → generate one. Save it.

---

## 4. GitHub secrets (repo → Settings → Secrets → Actions)

| Secret | Value |
|--------|--------|
| `APPLE_CERTIFICATE_BASE64` | `base64 -i YourCert.p12 \| pbcopy` |
| `APPLE_CERTIFICATE_PASSWORD` | p12 export password |
| `MACOS_SIGNING_IDENTITY` | e.g. `Developer ID Application: Your Name (TEAMID123)` |
| `APPLE_ID` | your Apple ID email |
| `APPLE_APP_SPECIFIC_PASSWORD` | from step 3 |
| `APPLE_TEAM_ID` | developer.apple.com → Membership → Team ID |

---

## 5. Ship

```bash
git tag v1.0.0
git push origin v1.0.0
```

GitHub Actions builds, signs, notarizes, uploads **The-Node.dmg** to Releases.

**Adopt** on the site downloads that file. User opens it, drags to Applications, opens. No Terminal. No “unidentified developer.”

---

## Test locally (optional)

```bash
export MACOS_SIGNING_IDENTITY="Developer ID Application: …"
export APPLE_ID="you@email.com"
export APPLE_APP_SPECIFIC_PASSWORD="xxxx-xxxx-xxxx-xxxx"
export APPLE_TEAM_ID="XXXXXXXXXX"
bash apps/mac/release.sh
open dist/The-Node.dmg
```

---

## What Adopt does after this

1. Click **Adopt**
2. **The-Node.dmg** downloads
3. Open → drag **The Node** to **Applications**
4. Open from Applications → passphrase in Terminal → node runs

That is the same path every real Mac app uses.
