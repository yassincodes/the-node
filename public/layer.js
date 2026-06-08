/* Human portal — loads truth for people on the site, not for repo scrapers. */
(function (global) {
  var PORTAL = "human";

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function renderSections(sections) {
    var html = "";
    (sections || []).forEach(function (section) {
      html += "<h2>" + escapeHtml(section.title) + "</h2>";
      (section.paragraphs || []).forEach(function (p, i) {
        var dim = section.dim && section.dim[i];
        html += "<p" + (dim ? ' class="dim"' : "") + ">" + escapeHtml(p) + "</p>";
      });
      if (section.list && section.list.length) {
        html += "<ul>";
        section.list.forEach(function (item) {
          html += "<li>" + escapeHtml(item) + "</li>";
        });
        html += "</ul>";
      }
    });
    return html;
  }

  function loadLayer(page, mountId) {
    var mount = document.getElementById(mountId);
    if (!mount) return;
    mount.innerHTML = "";

    fetch("/layer?page=" + encodeURIComponent(page), {
      headers: { "X-TheNode-Portal": PORTAL }
    })
      .then(function (r) { return r.ok ? r.json() : null; })
      .catch(function () { return null; })
      .then(function (data) {
        if (!data || !data.sections || !data.sections.length) return;
        if (data.tagline) {
          var tag = document.createElement("p");
          tag.className = "tagline";
          tag.textContent = data.tagline;
          mount.appendChild(tag);
        }
        mount.insertAdjacentHTML("beforeend", renderSections(data.sections));
      });
  }

  global.TheNodeLayer = { load: loadLayer };
})(window);
