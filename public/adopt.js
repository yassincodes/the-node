/**
 * Adoption — Mac: clone + run (no download quarantine).
 * One paste in Terminal, then everything is automatic.
 */
(function (global) {
  var REPO = "https://github.com/yassincodes/the-node.git";
  var GITHUB = "https://github.com/yassincodes/the-node";
  var CLONE_DIR = "~/The-Node";

  function parseUA() {
    var ua = navigator.userAgent || "";
    var platform = navigator.platform || "";
    if (/iPhone|iPad|iPod/i.test(ua)) return { os: "ios", arch: "arm" };
    if (/Android/i.test(ua)) return { os: "android", arch: "arm" };
    if (/Win/i.test(ua) || platform === "Win32") return { os: "windows", arch: /x64|WOW64|Win64/i.test(ua) ? "x64" : "x86" };
    if (/Mac/i.test(ua) || platform === "MacIntel") {
      return { os: "mac", arch: /aarch64|arm64/i.test(ua) ? "arm64" : "x64" };
    }
    if (/Linux/i.test(ua)) return { os: "linux", arch: /aarch64|arm64/i.test(ua) ? "arm64" : "x64" };
    return { os: "unknown", arch: "unknown" };
  }

  function detect() {
    return new Promise(function (resolve) {
      if (navigator.userAgentData && navigator.userAgentData.getHighEntropyValues) {
        navigator.userAgentData
          .getHighEntropyValues(["platform", "architecture", "bitness"])
          .then(function (h) {
            var os = "unknown";
            var p = (h.platform || "").toLowerCase();
            if (p === "macos") os = "mac";
            else if (p === "windows") os = "windows";
            else if (p === "linux") os = "linux";
            else if (p === "android") os = "android";
            else if (/ios/i.test(navigator.userAgent)) os = "ios";
            resolve({ os: os, arch: (h.architecture || "unknown").toLowerCase(), source: "ua-client-hints" });
          })
          .catch(function () { resolve(Object.assign(parseUA(), { source: "ua" })); });
      } else {
        resolve(Object.assign(parseUA(), { source: "ua" }));
      }
    });
  }

  function downloadBlob(blob, filename) {
    var url = URL.createObjectURL(blob);
    var a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
  }

  function flashAdopt(text, ms) {
    var btn = document.getElementById("adopt");
    if (!btn) return;
    var orig = btn.textContent;
    btn.textContent = text;
    setTimeout(function () { btn.textContent = orig; }, ms || 10000);
  }

  function macInstallLine() {
    return (
      "git clone " + REPO + " " + CLONE_DIR + " && bash " + CLONE_DIR + "/adopt"
    );
  }

  function copy(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      return navigator.clipboard.writeText(text);
    }
    return Promise.reject(new Error("clipboard"));
  }

  function macAdopt() {
    var line = macInstallLine();
    return copy(line).then(function () {
      flashAdopt("Terminal → ⌘V → enter");
      return { ok: true, os: "mac", line: line };
    }).catch(function () {
      flashAdopt(line);
      return { ok: true, os: "mac", line: line };
    });
  }

  function adopt(hardware) {
    var os = hardware.os;
    if (os === "mac") return macAdopt();
    if (os === "windows") {
      return fetch("/downloads/the-node-win.zip")
        .then(function (r) {
          if (!r.ok) throw new Error("missing");
          return r.blob();
        })
        .then(function (blob) {
          downloadBlob(blob, "The Node.zip");
          return { ok: true, os: os };
        });
    }
    return Promise.resolve({ ok: false, os: os });
  }

  global.TheNodeAdopt = {
    detect: detect,
    adopt: adopt,
    learnUrl: GITHUB,
    macInstallLine: macInstallLine
  };
})(window);
