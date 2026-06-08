(function (global) {
  var KEY = "thenode.portal.v1";

  function load() {
    try {
      return JSON.parse(localStorage.getItem(KEY) || "null") || fresh();
    } catch (e) {
      return fresh();
    }
  }

  function fresh() {
    var seed = new Uint8Array(16);
    crypto.getRandomValues(seed);
    var hex = Array.from(seed, function (b) {
      return b.toString(16).padStart(2, "0");
    }).join("");
    return {
      id: hex.slice(0, 16),
      born: false,
      entries: [],
    };
  }

  function save(state) {
    localStorage.setItem(KEY, JSON.stringify(state));
  }

  function adopt() {
    var s = load();
    if (!s.born) {
      s.born = true;
      s.bornAt = new Date().toISOString();
      save(s);
    }
    return s;
  }

  function store(text) {
    var s = load();
    if (!s.born) adopt();
    var entry = {
      id: Math.random().toString(16).slice(2, 10),
      content: text.trim(),
      at: new Date().toISOString(),
    };
    s.entries.unshift(entry);
    save(s);
    return entry;
  }

  function status() {
    var s = load();
    return {
      id: s.id,
      born: s.born,
      count: s.entries.length,
      last: s.entries[0] || null,
      entries: s.entries.slice(0, 5),
    };
  }

  global.TheNodePortal = { load: load, adopt: adopt, store: store, status: status, save: save };
})(window);
