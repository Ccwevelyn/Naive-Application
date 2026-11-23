(function () {
  const DATA = window.NAIVE;
  const STORAGE_KEY = "naive-application-v2";

  const COPY = {
    zh: {
      eyebrow: "硕士选校",
      region: "地区",
      all: "全选",
      none: "全不选",
      weights: "权重",
      reset: "清零",
      authorTitle: "作者的话",
      authorBody: "这个排序用的是 Multiple Criteria Analysis。想法来自大三下学期的一门课，Risk Management。所以这里会把各项分数按你拉的权重加权，算出一个综合分。",
      kicker: "按你的权重",
      scrollList: "学校列表",
      schools: "所",
      search: "搜索学校",
      subject: "专业",
      subjectNone: "不按专业",
      subjectSort: "QS 学科",
      qsSubject: "QS 学科",
      sort: "排序",
      score: "综合分",
      empty: "勾选一个地区，或者换个搜索词。",
      open: "看每一项",
      close: "收起",
      missing: "这份榜单里没有",
      rank: "综合排名",
      lab: "实验室资源",
      industry: "产业连接",
      place: "环境",
      tagPlace: "地点类型",
      town: "大学城",
      city: "城市",
      downtown: "市中心",
      district: "城区",
      rural: "乡野",
      placeNeed: "先选一个想去的地方。",
      placeUnknown: "没有标注地点类型",
      placeHit: "对上",
      placeMiss: "对不上",
      price: "学费",
      tagPrice: "最低公布档",
      priceMax: "最高学费",
      priceUnit: "万元/年",
      priceNeed: "先填一个最高学费。",
      tagRank: "官方名次",
      tagLab: "环境与师生比",
      env: "科研环境",
      faculty: "师生比",
      tagIndustry: "THE Industry",
      qs: "QS",
      the: "THE",
      usnews: "U.S. News",
      soe: "央国企",
      energy: "能源",
      internet: "互联网大厂",
      foreign: "外企",
    },
    en: {
      eyebrow: "Master's school choice",
      region: "Region",
      all: "All",
      none: "None",
      weights: "Weights",
      reset: "Clear",
      authorTitle: "A note from the author",
      authorBody: "This ranking uses multiple criteria analysis. I learned the idea in a Risk Management course in the second semester of my junior year. The scores are weighted by the sliders and added into one result.",
      kicker: "By your weights",
      scrollList: "School list",
      schools: "schools",
      search: "Search schools",
      subject: "Subject",
      subjectNone: "No subject",
      subjectSort: "QS subject",
      qsSubject: "QS subject",
      sort: "Sort",
      score: "Score",
      empty: "Select a region, or try another search.",
      open: "Breakdown",
      close: "Hide",
      missing: "Not on this list",
      rank: "Ranking",
      lab: "Labs",
      industry: "Industry links",
      place: "Setting",
      tagPlace: "Campus type",
      town: "College town",
      city: "City",
      downtown: "City centre",
      district: "District",
      rural: "Countryside",
      placeNeed: "Pick a place first.",
      placeUnknown: "Setting is not labeled",
      placeHit: "Matches",
      placeMiss: "Does not match",
      price: "Tuition",
      tagPrice: "Lowest published",
      priceMax: "Highest tuition",
      priceUnit: "10k CNY/yr",
      priceNeed: "Enter a highest tuition first.",
      tagRank: "Published ranks",
      tagLab: "Setting and faculty",
      env: "Research setting",
      faculty: "Faculty ratio",
      tagIndustry: "THE Industry",
      qs: "QS",
      the: "THE",
      usnews: "U.S. News",
      soe: "State-owned",
      energy: "Energy",
      internet: "Big tech",
      foreign: "Foreign firms",
    },
  };

  const CRITERIA = [
    { key: "rank", label: "rank", tag: "tagRank", nested: "rank" },
    { key: "lab", label: "lab", tag: "tagLab", nested: "lab" },
    { key: "industry", label: "industry", tag: "tagIndustry" },
    { key: "place", label: "place", tag: "tagPlace", nested: "place" },
    { key: "price", label: "price", tag: "tagPrice", nested: "price" },
  ];

  const RANK_MIX = [
    { key: "qs", label: "qs" },
    { key: "the", label: "the" },
    { key: "usnews", label: "usnews" },
  ];

  const JOB_PATHS = [
    { key: "soe", label: "soe" },
    { key: "energy", label: "energy" },
    { key: "internet", label: "internet" },
    { key: "foreign", label: "foreign" },
  ];

  // Rank parts only. Industry and international outlook stay on their own criteria.
  const JOB_RANK = {
    soe: { qs: 72, the: 20, usnews: 8 },
    energy: { qs: 50, the: 25, usnews: 25 },
    internet: { qs: 30, the: 0, usnews: 15 },
    foreign: { qs: 40, the: 25, usnews: 0 },
  };

  const LAB_MIX = [
    { key: "env", label: "env" },
    { key: "faculty", label: "faculty" },
  ];

  const PLACE_OPTIONS = [
    { key: "town", label: "town" },
    { key: "city", label: "city" },
    { key: "downtown", label: "downtown" },
    { key: "district", label: "district" },
    { key: "rural", label: "rural" },
  ];

  const PLACE_MISS = 40;

  const COLORS = {
    rank: "#1c1814",
    lab: "#1d6844",
    industry: "#6a4c78",
    place: "#2a5f8a",
    price: "#c46a2f",
  };

  const DEFAULTS = {
    lang: "zh",
    weights: { rank: 30, lab: 10, industry: 10, place: 10, price: 0 },
    settings: [],
    priceMax: null,
    rankMix: { qs: 50, the: 25, usnews: 25, subject: 40 },
    subject: "",
    jobs: [],
    labMix: { env: 60, faculty: 40 },
    selected: [],
    query: "",
    sort: "score",
  };

  const state = loadState();
  applyJobRankMix();
  let openId = null;

  const regionBox = document.getElementById("region-chips");
  const weightBox = document.getElementById("weights");
  const list = document.getElementById("list");
  const mix = document.getElementById("mix");
  const countEl = document.getElementById("result-count");
  const queryEl = document.getElementById("query");
  const sortEl = document.getElementById("sort");
  const subjectEl = document.getElementById("subject");

  document.getElementById("lang").addEventListener("click", (event) => {
    const button = event.target.closest("[data-lang]");
    if (!button) return;
    state.lang = button.dataset.lang;
    persist();
    paint();
  });

  document.getElementById("select-all").addEventListener("click", () => {
    state.selected = allRegionsOn() ? [] : DATA.regions.map((region) => region.id);
    persist();
    renderRegions();
    syncSelectAll();
    render();
  });

  document.getElementById("reset-weights").addEventListener("click", () => {
    Object.keys(state.weights).forEach((key) => {
      state.weights[key] = 0;
    });
    openId = null;
    persist();
    renderWeights();
    render();
  });

  queryEl.addEventListener("input", () => {
    state.query = queryEl.value;
    persist();
    render();
  });

  subjectEl.addEventListener("change", () => {
    state.subject = subjectEl.value;
    if (state.subject && !state.rankMix.subject) state.rankMix.subject = 40;
    persist();
    renderWeights();
    render();
  });

  sortEl.addEventListener("change", () => {
    state.sort = sortEl.value;
    persist();
    render();
  });

  list.addEventListener("click", (event) => {
    const button = event.target.closest(".card-toggle");
    if (!button) return;
    const id = button.closest(".card").dataset.id;
    openId = openId === id ? null : id;
    render();
  });

  const REGION_GROUPS = [
    { zh: "中国", en: "China", lines: [["hk", "mo"], ["cn", "tw"]] },
    { zh: "美洲", en: "Americas", lines: [["us", "ca", "latam"]] },
    { zh: "欧洲", en: "Europe", lines: [["uk", "ie", "eu"]] },
    { zh: "亚太", en: "Asia-Pacific", lines: [["jp", "kr", "my"], ["sg", "in", "asia"]] },
    { zh: "大洋洲", en: "Oceania", lines: [["au", "nz"]] },
    { zh: "非洲与中东", en: "Africa & Middle East", lines: [["af", "me"]] },
  ];

  paint();

  function t(key) {
    return COPY[state.lang][key];
  }

  function loadState() {
    try {
      const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || "null");
      if (!saved || !saved.weights) return structuredClone(DEFAULTS);
      return {
        lang: saved.lang === "en" ? "en" : "zh",
        weights: Object.fromEntries(CRITERIA.map((criterion) => [
          criterion.key,
          saved.weights[criterion.key] == null ? DEFAULTS.weights[criterion.key] : Number(saved.weights[criterion.key]),
        ])),
        rankMix: { ...DEFAULTS.rankMix, ...saved.rankMix },
        subject: typeof saved.subject === "string" ? saved.subject : "",
        jobs: Array.isArray(saved.jobs) ? saved.jobs.filter((key) => JOB_PATHS.some((job) => job.key === key)) : [],
        labMix: lockPair({ ...DEFAULTS.labMix, ...saved.labMix }, "env", "faculty"),
        settings: Array.isArray(saved.settings) ? saved.settings.filter((key) => PLACE_OPTIONS.some((option) => option.key === key)) : [],
        priceMax: Number.isFinite(Number(saved.priceMax)) && Number(saved.priceMax) >= 0 ? Number(saved.priceMax) : null,
        selected: Array.isArray(saved.selected) ? saved.selected : [],
        query: saved.query || "",
        sort: saved.sort || "score",
      };
    } catch (err) {
      return structuredClone(DEFAULTS);
    }
  }

  function persist() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  }

  function paint() {
    document.documentElement.lang = state.lang === "en" ? "en" : "zh-CN";
    document.getElementById("eyebrow").textContent = t("eyebrow");
    document.getElementById("region-heading").textContent = t("region");
    syncSelectAll();
    document.getElementById("weight-heading").textContent = t("weights");
    document.getElementById("reset-weights").textContent = t("reset");
    document.getElementById("author-title").textContent = t("authorTitle");
    document.getElementById("author-body").textContent = t("authorBody");
    document.getElementById("result-kicker").textContent = t("kicker");
    document.getElementById("wake-scroll").setAttribute("aria-label", t("scrollList"));
    document.getElementById("search-label").textContent = t("search");
    document.getElementById("subject-label").textContent = t("subject");
    document.getElementById("sort-label").textContent = t("sort");
    sortEl.querySelector('[value="subject"]').textContent = t("subjectSort");
    queryEl.placeholder = t("search");
    queryEl.value = state.query;
    sortEl.querySelector('[value="score"]').textContent = t("score");
    sortEl.value = state.sort;
    renderSubjectOptions();
    document.querySelectorAll("#lang button").forEach((button) => {
      button.classList.toggle("active", button.dataset.lang === state.lang);
    });
    renderRegions();
    renderWeights();
    render();
  }

  function renderSubjectOptions() {
    const known = new Set(window.NAIVE_SUBJECTS.list.map((item) => item.id));
    if (state.subject && !known.has(state.subject)) state.subject = "";
    subjectEl.replaceChildren();
    const none = document.createElement("option");
    none.value = "";
    none.textContent = t("subjectNone");
    subjectEl.appendChild(none);
    window.NAIVE_SUBJECTS.list.forEach((item) => {
      const option = document.createElement("option");
      option.value = item.id;
      option.textContent = state.lang === "en" ? item.en : item.zh;
      subjectEl.appendChild(option);
    });
    subjectEl.value = state.subject;
  }

  function rankBag() {
    const bag = {
      qs: state.rankMix.qs,
      the: state.rankMix.the,
      usnews: state.rankMix.usnews,
    };
    if (state.subject) bag.subject = state.rankMix.subject;
    return bag;
  }

  function allRegionsOn() {
    return DATA.regions.every((region) => state.selected.includes(region.id));
  }

  function syncSelectAll() {
    document.getElementById("select-all").textContent = allRegionsOn() ? t("none") : t("all");
  }

  function renderRegions() {
    regionBox.replaceChildren();
    const byId = Object.fromEntries(DATA.regions.map((region) => [region.id, region]));
    REGION_GROUPS.forEach((group) => {
      const row = document.createElement("div");
      row.className = "region-row";
      const heading = document.createElement("span");
      heading.className = "region-label";
      heading.textContent = state.lang === "en" ? group.en : group.zh;
      const lines = document.createElement("div");
      lines.className = "region-lines";
      row.append(heading, lines);
      group.lines.forEach((ids) => {
        const chips = document.createElement("div");
        chips.className = "chips";
        ids.forEach((id) => {
          const region = byId[id];
          if (!region) return;
          const label = document.createElement("label");
          label.className = "chip";
          const input = document.createElement("input");
          input.type = "checkbox";
          input.checked = state.selected.includes(region.id);
          input.addEventListener("change", () => {
            if (input.checked) {
              if (!state.selected.includes(region.id)) state.selected.push(region.id);
            } else {
              state.selected = state.selected.filter((key) => key !== region.id);
            }
            persist();
            syncSelectAll();
            render();
          });
          const name = document.createElement("span");
          const count = DATA.schools.filter((school) => school.region === region.id).length;
          name.textContent = (state.lang === "en" ? region.en : region.zh) + " " + count;
          label.append(input, name);
          chips.appendChild(label);
        });
        lines.appendChild(chips);
      });
      regionBox.appendChild(row);
    });
    syncSelectAll();
  }

  function renderWeights() {
    weightBox.replaceChildren();
    const weightShare = weightFraction();
    CRITERIA.forEach((criterion) => {
      const group = document.createElement("div");
      group.className = "group";
      const title = document.createElement("div");
      title.className = "group-title";
      const nameWrap = document.createElement("span");
      nameWrap.className = "group-name";
      const name = document.createElement("strong");
      name.textContent = t(criterion.label);
      const tag = document.createElement("span");
      tag.className = "tag";
      tag.textContent = t(criterion.tag);
      nameWrap.append(name, tag);
      const pct = document.createElement("span");
      pct.className = "pct";
      pct.dataset.share = "weight:" + criterion.key;
      pct.textContent = percentText(weightShare[criterion.key]);
      title.append(nameWrap, pct);
      group.appendChild(title);
      group.appendChild(slider(state.weights, criterion.key, t(criterion.label), true));
      if (criterion.nested === "rank") {
        group.appendChild(jobChips());
        const items = state.subject ? RANK_MIX.concat([{ key: "subject", label: "qsSubject" }]) : RANK_MIX;
        group.appendChild(nested(items, state.rankMix, "rank", rankBag()));
      }
      if (criterion.nested === "lab") group.appendChild(nested(LAB_MIX, state.labMix, "lab"));
      if (criterion.nested === "place") group.appendChild(placeChips());
      if (criterion.nested === "price") group.appendChild(priceField());
      weightBox.appendChild(group);
    });
  }

  function priceField() {
    const label = document.createElement("label");
    label.className = "price-max";
    const name = document.createElement("span");
    name.textContent = t("priceMax");
    const input = document.createElement("input");
    input.type = "number";
    input.min = "0";
    input.step = "0.1";
    input.inputMode = "decimal";
    input.setAttribute("aria-label", t("priceMax"));
    if (state.priceMax != null) input.value = String(state.priceMax);
    input.placeholder = t("priceUnit");
    input.addEventListener("input", () => {
      const raw = input.value.trim();
      const next = raw === "" ? null : Number(raw);
      state.priceMax = next != null && Number.isFinite(next) && next >= 0 ? next : null;
      persist();
      render();
    });
    const unit = document.createElement("span");
    unit.textContent = t("priceUnit");
    label.append(name, input, unit);
    return label;
  }

  function applyJobRankMix() {
    const chosen = JOB_PATHS.filter((job) => state.jobs.includes(job.key));
    if (!chosen.length) return;
    const total = { qs: 0, the: 0, usnews: 0 };
    chosen.forEach((job) => {
      const mix = JOB_RANK[job.key];
      const sum = mix.qs + mix.the + mix.usnews;
      total.qs += mix.qs / sum;
      total.the += mix.the / sum;
      total.usnews += mix.usnews / sum;
    });
    const scale = 100 / chosen.length;
    const raw = {
      qs: total.qs * scale,
      the: total.the * scale,
      usnews: total.usnews * scale,
    };
    const keys = ["qs", "the", "usnews"];
    const rounded = {};
    keys.forEach((key) => { rounded[key] = Math.round(raw[key]); });
    let drift = 100 - keys.reduce((sum, key) => sum + rounded[key], 0);
    const order = keys.slice().sort((a, b) => (raw[b] - rounded[b]) - (raw[a] - rounded[a]));
    let stepIndex = 0;
    while (drift !== 0 && stepIndex < 6) {
      const key = order[stepIndex % order.length];
      const step = drift > 0 ? 1 : -1;
      if (rounded[key] + step >= 0) {
        rounded[key] += step;
        drift -= step;
      }
      stepIndex += 1;
    }
    state.rankMix.qs = rounded.qs;
    state.rankMix.the = rounded.the;
    state.rankMix.usnews = rounded.usnews;
  }

  function jobChips() {
    const lines = state.lang === "en"
      ? [["soe", "energy"], ["internet", "foreign"]]
      : [JOB_PATHS.map((job) => job.key)];
    const wrap = document.createElement("div");
    wrap.className = "job-lines";
    lines.forEach((keys) => {
      const box = document.createElement("div");
      box.className = "chips job-chips";
      keys.forEach((key) => {
        const job = JOB_PATHS.find((item) => item.key === key);
        const label = document.createElement("label");
        label.className = "chip";
        const input = document.createElement("input");
        input.type = "checkbox";
        input.checked = state.jobs.includes(job.key);
        input.addEventListener("change", () => {
          if (input.checked) {
            if (!state.jobs.includes(job.key)) state.jobs.push(job.key);
          } else {
            state.jobs = state.jobs.filter((item) => item !== job.key);
          }
          applyJobRankMix();
          persist();
          renderWeights();
          render();
        });
        const name = document.createElement("span");
        name.textContent = t(job.label);
        label.append(input, name);
        box.appendChild(label);
      });
      wrap.appendChild(box);
    });
    return wrap;
  }

  function placeChips() {
    const lines = state.lang === "en"
      ? [["town", "city", "downtown"], ["district", "rural"]]
      : [PLACE_OPTIONS.map((option) => option.key)];
    const wrap = document.createElement("div");
    wrap.className = "job-lines";
    lines.forEach((keys) => {
      const box = document.createElement("div");
      box.className = "chips job-chips";
      keys.forEach((key) => {
        const option = PLACE_OPTIONS.find((item) => item.key === key);
        const label = document.createElement("label");
        label.className = "chip";
        const input = document.createElement("input");
        input.type = "checkbox";
        input.checked = state.settings.includes(option.key);
        input.addEventListener("change", () => {
          if (input.checked) {
            if (!state.settings.includes(option.key)) state.settings.push(option.key);
          } else {
            state.settings = state.settings.filter((item) => item !== option.key);
          }
          persist();
          render();
        });
        const name = document.createElement("span");
        name.textContent = t(option.label);
        label.append(input, name);
        box.appendChild(label);
      });
      wrap.appendChild(box);
    });
    return wrap;
  }

  function nested(items, bag, group, shown) {
    const box = document.createElement("div");
    box.className = "nested";
    const ranked = group === "rank";
    const parts = ranked ? share(shown || bag) : null;
    items.forEach((item) => {
      const row = document.createElement("div");
      row.className = "slider-row";
      const label = document.createElement("span");
      label.textContent = t(item.label);
      const pct = document.createElement("span");
      pct.className = "num";
      pct.dataset.share = group + ":" + item.key;
      pct.textContent = ranked ? percentText(parts[item.key]) : Math.round(Number(bag[item.key])) + "%";
      row.append(label, pct);
      box.appendChild(row);
      box.appendChild(slider(bag, item.key, t(item.label), false, !ranked));
    });
    return box;
  }

  function weightRoom(key) {
    return Object.keys(state.weights).reduce((sum, item) => {
      return sum + (item === key ? 0 : Number(state.weights[item]));
    }, 0);
  }

  function absorbNext(bag, key, value) {
    const keys = Object.keys(bag);
    const index = keys.indexOf(key);
    const absorber = keys[index < keys.length - 1 ? index + 1 : index - 1];
    const fixedSum = keys.reduce((sum, item) => {
      if (item === key || item === absorber) return sum;
      return sum + Number(bag[item]);
    }, 0);
    const next = Math.max(0, Math.min(100 - fixedSum, Math.round(Number(value))));
    bag[key] = next;
    bag[absorber] = 100 - fixedSum - next;
    return absorber;
  }

  function lockPair(bag, aKey, bKey) {
    let a = Math.round(Number(bag[aKey]));
    let b = Math.round(Number(bag[bKey]));
    if (!Number.isFinite(a)) a = 50;
    if (!Number.isFinite(b)) b = 50;
    a = Math.max(0, Math.min(100, a));
    b = Math.max(0, Math.min(100, b));
    const sum = a + b;
    if (sum === 100) return { [aKey]: a, [bKey]: b };
    if (sum <= 0) return { [aKey]: 50, [bKey]: 50 };
    const scaled = Math.max(0, Math.min(100, Math.round((a / sum) * 100)));
    return { [aKey]: scaled, [bKey]: 100 - scaled };
  }

  function slider(bag, key, label, accent, cappedMix) {
    const input = document.createElement("input");
    input.type = "range";
    input.min = "0";
    input.max = "100";
    input.step = "1";
    input.value = String(bag[key]);
    input.className = accent ? "accent" : "";
    input.dataset.mixKey = key;
    input.setAttribute("aria-label", label);
    input.addEventListener("input", () => {
      let value = Number(input.value);
      if (cappedMix) {
        const absorber = absorbNext(bag, key, value);
        input.value = String(bag[key]);
        const sibling = input.parentElement.querySelector('input[data-mix-key="' + absorber + '"]');
        if (sibling) sibling.value = String(bag[absorber]);
      } else if (accent) {
        const cap = Math.max(0, 100 - weightRoom(key));
        if (value > cap) {
          value = cap;
          input.value = String(value);
        }
        bag[key] = value;
      } else {
        bag[key] = value;
      }
      if (bag === state.rankMix && key !== "subject" && state.jobs.length) {
        state.jobs = [];
        document.querySelectorAll(".job-chips input").forEach((node) => {
          node.checked = false;
        });
      }
      persist();
      syncReadouts();
      render();
    });
    return input;
  }

  function syncReadouts() {
    const tables = {
      weight: weightFraction(),
      rank: share(rankBag()),
      lab: mixFraction(state.labMix),
    };
    document.querySelectorAll("[data-share]").forEach((node) => {
      const splitAt = node.dataset.share.indexOf(":");
      const group = node.dataset.share.slice(0, splitAt);
      const key = node.dataset.share.slice(splitAt + 1);
      node.textContent = percentText(tables[group][key]);
    });
  }

  function render() {
    const weightShare = weightFraction();
    const rankShare = share(rankBag());
    const rows = rankSchools(weightShare, rankShare);

    mix.replaceChildren();
    CRITERIA.forEach((criterion) => {
      const piece = document.createElement("i");
      piece.style.width = Number(state.weights[criterion.key]) + "%";
      piece.style.background = COLORS[criterion.key];
      mix.appendChild(piece);
    });

    countEl.textContent = state.lang === "en" ? rows.length + " schools" : rows.length + " 所";

    list.replaceChildren();
    if (!rows.length) {
      const empty = document.createElement("p");
      empty.className = "empty";
      empty.textContent = t("empty");
      list.appendChild(empty);
      return;
    }
    rows.forEach((row, index) => list.appendChild(card(row, index + 1)));
  }

  function card(row, index) {
    const school = row.school;
    const place = DATA.places[school.country];
    const article = document.createElement("li");
    article.className = "card" + (openId === school.id ? " open" : "");
    article.dataset.id = school.id;

    const top = document.createElement("div");
    top.className = "card-top";
    const who = document.createElement("div");
    who.className = "who";
    const num = document.createElement("div");
    num.className = "index";
    num.textContent = String(index).padStart(2, "0");
    const names = document.createElement("div");
    const primary = document.createElement("h3");
    primary.className = "zh";
    primary.textContent = state.lang === "en" ? school.en : school.zh;
    const where = document.createElement("p");
    where.className = "place";
    const settingName = school.setting && school.setting !== "unknown" ? t(school.setting) : "";
    where.textContent = (state.lang === "en" ? place.en : place.zh) + (settingName ? " · " + settingName : "");
    if (state.lang === "en") {
      names.append(primary, where);
    } else {
      const secondary = document.createElement("p");
      secondary.className = "en";
      secondary.textContent = school.en;
      names.append(primary, secondary, where);
    }
    who.append(num, names);

    const scoreWrap = document.createElement("div");
    scoreWrap.className = "score-wrap";
    const score = document.createElement("div");
    score.className = "score";
    score.textContent = row.total.toFixed(1);
    const scoreLabel = document.createElement("p");
    scoreLabel.className = "score-label";
    scoreLabel.textContent = t("score");
    scoreWrap.append(score, scoreLabel);
    top.append(who, scoreWrap);

    const badges = document.createElement("div");
    badges.className = "badges";
    [["QS", school.qs == null ? school.qsBand : school.qs], ["THE", school.the], ["U.S. News", school.usnews]].forEach(([name, value]) => {
      const badge = document.createElement("span");
      badge.className = "badge";
      badge.textContent = name + " " + (value == null ? "—" : value);
      badges.appendChild(badge);
    });
    if (state.subject) {
      const badge = document.createElement("span");
      badge.className = "badge";
      badge.textContent = t("qsSubject") + " " + (row.subjectRank == null ? "—" : row.subjectRank);
      badges.appendChild(badge);
    }

    const bar = document.createElement("div");
    bar.className = "bar";
    CRITERIA.forEach((criterion) => {
      const piece = document.createElement("i");
      piece.style.flex = String(Math.max(row.contrib[criterion.key], 0));
      piece.style.background = COLORS[criterion.key];
      bar.appendChild(piece);
    });

    const toggle = document.createElement("button");
    toggle.type = "button";
    toggle.className = "card-toggle";
    const opened = openId === school.id;
    toggle.setAttribute("aria-expanded", opened ? "true" : "false");
    toggle.setAttribute("aria-label", opened ? t("close") : t("open"));
    const icon = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    icon.setAttribute("viewBox", "0 0 20 20");
    icon.setAttribute("width", "18");
    icon.setAttribute("height", "18");
    icon.setAttribute("aria-hidden", "true");
    const shaft = document.createElementNS("http://www.w3.org/2000/svg", "path");
    shaft.setAttribute("d", "M10 4v9M6 10l4 5 4-5");
    shaft.setAttribute("fill", "none");
    shaft.setAttribute("stroke", "currentColor");
    shaft.setAttribute("stroke-width", "1.6");
    shaft.setAttribute("stroke-linecap", "round");
    shaft.setAttribute("stroke-linejoin", "round");
    icon.appendChild(shaft);
    toggle.appendChild(icon);

    const detail = document.createElement("div");
    detail.className = "detail";
    detailRows(row).forEach((line) => {
      const breakRow = document.createElement("div");
      breakRow.className = "break-row";
      const label = document.createElement("b");
      label.textContent = line.label;
      const meta = document.createElement("span");
      meta.className = "num";
      meta.textContent = line.meta;
      breakRow.append(label, meta);
      detail.appendChild(breakRow);
    });

    article.append(top, badges, bar, toggle, detail);
    return article;
  }

  function detailRows(row) {
    const rankMeta = row.scores.rank == null
      ? t("missing")
      : "QS " + num(row.parts.qs) + " · THE " + num(row.parts.the) + " · U.S. News " + num(row.parts.usnews) + (state.subject ? " · " + t("qsSubject") + " " + (row.subjectRank == null ? "—" : row.subjectRank) : "") + " → " + row.scores.rank.toFixed(1) + " × " + percentText(row.used.rank) + " = " + row.contrib.rank.toFixed(1);
    return [
      { label: t("rank"), meta: rankMeta },
      { label: t("lab"), meta: mixMeta(row, "lab", [[t("env"), row.parts.env], [t("faculty"), row.parts.faculty]]) },
      { label: t("industry"), meta: factorMeta(row, "industry") },
      { label: t("place"), meta: placeMeta(row) },
      { label: t("price"), meta: priceMeta(row) },
    ];
  }

  function placeMeta(row) {
    if (!state.settings.length) return t("placeNeed");
    const setting = row.school.setting;
    if (!setting || setting === "unknown" || row.scores.place == null) return t("placeUnknown");
    const hit = state.settings.includes(setting);
    return t(setting) + " · " + (hit ? t("placeHit") : t("placeMiss")) + " → " + row.scores.place.toFixed(1) + " × " + percentText(row.used.place) + " = " + row.contrib.place.toFixed(1);
  }

  function priceMeta(row) {
    const cost = publishedCost(row.school);
    if (!(Number(state.priceMax) > 0)) return t("priceNeed");
    if (!cost || row.scores.price == null) return t("missing");
    const unit = state.lang === "en" ? "" : "万";
    return cost.tuition + unit + " · " + t("priceMax") + " " + state.priceMax + unit + " → " + row.scores.price.toFixed(1) + " × " + percentText(row.used.price) + " = " + row.contrib.price.toFixed(1);
  }

  function mixMeta(row, key, pieces) {
    if (row.scores[key] == null) return t("missing");
    const head = pieces.map(([label, value]) => label + " " + num(value)).join(" · ");
    return head + " → " + row.scores[key].toFixed(1) + " × " + percentText(row.used[key]) + " = " + row.contrib[key].toFixed(1);
  }

  function factorMeta(row, key) {
    if (row.scores[key] == null) return t("missing");
    return row.scores[key].toFixed(1) + " × " + percentText(row.used[key]) + " = " + row.contrib[key].toFixed(1);
  }

  function num(value) {
    return value == null ? "—" : value.toFixed(1);
  }

  function rankSchools(weightShare, rankShare) {
    const selected = new Set(state.selected);
    const query = state.query.trim().toLowerCase();
    const rows = DATA.schools.filter((school) => {
      if (!selected.has(school.region)) return false;
      if (!query) return true;
      const place = DATA.places[school.country];
      return (school.zh + " " + school.en + " " + place.zh + " " + place.en).toLowerCase().includes(query);
    }).map((school) => scoreSchool(school, weightShare, rankShare));

    const rankValue = (school, key) => (school[key] == null ? 100000 : school[key]);
    const sorters = {
      score: (a, b) => b.total - a.total || rankValue(a.school, "qs") - rankValue(b.school, "qs"),
      qs: (a, b) => rankValue(a.school, "qs") - rankValue(b.school, "qs"),
      the: (a, b) => rankValue(a.school, "the") - rankValue(b.school, "the"),
      usnews: (a, b) => rankValue(a.school, "usnews") - rankValue(b.school, "usnews"),
      subject: (a, b) => (a.subjectRank == null ? 100000 : a.subjectRank) - (b.subjectRank == null ? 100000 : b.subjectRank) || b.total - a.total,
    };
    rows.sort(sorters[state.sort] || sorters.score);
    return rows;
  }

  function scoreSchool(school, weightShare, rankShare) {
    const subjectRank = state.subject ? window.NAIVE_SUBJECTS.ranks[state.subject][school.id] ?? null : null;
    const parts = {
      qs: school.qs == null ? null : rankScore(school.qs),
      the: school.the == null ? null : rankScore(school.the),
      usnews: school.usnews == null ? null : rankScore(school.usnews),
      subject: subjectRank == null ? null : rankScore(subjectRank),
      env: school.researchEnv,
      faculty: school.faculty,
    };
    const scores = {
      rank: blend([
        { weight: rankShare.qs, value: parts.qs },
        { weight: rankShare.the, value: parts.the },
        { weight: rankShare.usnews, value: parts.usnews },
        { weight: rankShare.subject || 0, value: parts.subject },
      ].filter((item) => item.weight > 0)),
      lab: mixScore([
        { weight: state.labMix.env, value: parts.env },
        { weight: state.labMix.faculty, value: parts.faculty },
      ]),
      industry: school.industry,
      place: placeScore(school),
      price: priceScore(publishedCost(school)),
    };
    const used = {};
    const contrib = {};
    let total = 0;
    CRITERIA.forEach((criterion) => {
      const value = scores[criterion.key];
      used[criterion.key] = value == null ? 0 : weightShare[criterion.key];
      contrib[criterion.key] = value == null ? 0 : value * weightShare[criterion.key];
      total += contrib[criterion.key];
    });
    return { school, parts, scores, used, contrib, total, subjectRank };
  }

  function publishedCost(school) {
    const tuition = school.tuition == null ? null : Number(school.tuition);
    if (tuition == null || !Number.isFinite(tuition)) return null;
    return { tuition };
  }

  function placeScore(school) {
    if (!state.settings.length) return null;
    if (!school.setting || school.setting === "unknown") return null;
    return state.settings.includes(school.setting) ? 100 : PLACE_MISS;
  }

  function priceScore(cost) {
    const max = Number(state.priceMax);
    if (!(max > 0) || !cost) return null;
    if (cost.tuition > max) return 0;
    return ((max - cost.tuition) / max) * 100;
  }

  function mixScore(parts) {
    const ready = parts.filter((item) => item.value != null && item.weight > 0);
    if (!ready.length) return null;
    return ready.reduce((sum, item) => sum + item.value * (Number(item.weight) / 100), 0);
  }

  function blend(parts) {
    const ready = parts.filter((item) => item.value != null && item.weight > 0);
    if (!ready.length) {
      const fallback = parts.filter((item) => item.value != null);
      if (!fallback.length) return null;
      const even = 1 / fallback.length;
      return fallback.reduce((sum, item) => sum + item.value * even, 0);
    }
    const sum = ready.reduce((total, item) => total + item.weight, 0);
    return ready.reduce((total, item) => total + item.value * (item.weight / sum), 0);
  }

  function rankScore(rank) {
    const value = Number(rank);
    if (!Number.isFinite(value) || value < 1) return 0;
    const cleared = [50, 100, 150, 200, 500].reduce((count, edge) => {
      return count + (value <= edge ? 1 : 0);
    }, 0);
    const bands = [[1, 50], [51, 100], [101, 150], [151, 200], [201, 500], [501, 1000]];
    const band = bands.find(([start, end]) => value >= start && value <= end);
    const within = band ? ((band[1] - value) / (band[1] - band[0])) * 6 : 0;
    return Math.round(((cleared * 18 + within) / 96) * 1000) / 10;
  }

  function mixFraction(bag) {
    const out = {};
    Object.keys(bag).forEach((key) => {
      out[key] = Number(bag[key]) / 100;
    });
    return out;
  }

  function weightFraction() {
    const out = {};
    Object.keys(state.weights).forEach((key) => {
      out[key] = Number(state.weights[key]) / 100;
    });
    return out;
  }

  function share(bag) {
    const keys = Object.keys(bag);
    const sum = keys.reduce((total, key) => total + Number(bag[key]), 0);
    const out = {};
    keys.forEach((key) => {
      out[key] = sum > 0 ? Number(bag[key]) / sum : 1 / keys.length;
    });
    return out;
  }

  function percentText(fraction) {
    return Math.round((fraction || 0) * 100) + "%";
  }

  function mountWake() {
    const scroller = document.querySelector(".results-scroll");
    const rail = document.getElementById("wake-scroll");
    const BARS = 36;
    const REST = 0.45;
    const REACH = 6;
    const SKEW = 0.6;
    const FULL_SPEED = 320;
    const MIN_REACH = 1.5;
    const FLAT = 0.002;
    const bars = [];
    for (let i = 0; i < BARS; i += 1) {
      const bar = document.createElement("span");
      bar.className = "wake-scroll__bar";
      rail.appendChild(bar);
      bars.push(bar);
    }

    let target = 0;
    let head = 0;
    let headV = 0;
    let speed = 0;
    let speedV = 0;
    let lastAmp = 0;
    let lastTime = performance.now();
    let dragging = false;
    const w0 = 9.23 / 0.3;
    const kHead = w0 * w0;
    const dHead = 2 * w0;
    const wv = 2000 / 100;
    const kSpeed = wv * wv;
    const dSpeed = 2.5 * wv;

    const clamp = (v, lo, hi) => Math.min(hi, Math.max(lo, v));
    const maxScroll = () => Math.max(0, scroller.scrollHeight - scroller.clientHeight);
    const readPct = () => {
      const max = maxScroll();
      return max > 0 ? (scroller.scrollTop / max) * 100 : 0;
    };

    function paint() {
      const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      const h = (head / 100) * (BARS - 1);
      const amp = reduce ? 0 : (s => s * s * (3 - 2 * s))(clamp((Math.abs(speed)) / FULL_SPEED, 0, 1));
      const dir = Math.sign(speed) || 1;
      const reach = MIN_REACH + (REACH - MIN_REACH) * amp;
      const behind = reach * (1 + SKEW);
      const ahead = reach * (1 - 0.5 * SKEW);
      const lit = Math.round(h);
      const flat = amp < FLAT && lastAmp < FLAT;
      bars.forEach((el, i) => {
        const on = i <= lit ? "true" : "false";
        if (el.dataset.on !== on) el.dataset.on = on;
        if (flat) return;
        const d = i - h;
        const span = d * dir < 0 ? behind : ahead;
        const lift = Math.abs(d) < span ? amp * Math.cos((Math.PI * d) / (2 * span)) ** 2 : 0;
        el.style.transform = "scaleX(" + (REST + lift * (1 - REST)) + ")";
      });
      lastAmp = amp;
      rail.setAttribute("aria-valuenow", String(Math.round(readPct())));
    }

    function tick(now) {
      const dt = Math.min(0.05, (now - lastTime) / 1000);
      lastTime = now;
      const narrow = window.matchMedia("(max-width: 900px)").matches;
      const overflow = maxScroll() > 1 && !narrow;
      rail.classList.toggle("is-off", !overflow);
      if (!dragging) target = readPct();
      const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      if (reduce) {
        head = target;
        speed = 0;
      } else {
        headV += (-kHead * (head - target) - dHead * headV) * dt;
        head += headV * dt;
        speedV += (-kSpeed * (speed - headV) - dSpeed * speedV) * dt;
        speed += speedV * dt;
      }
      if (overflow) paint();
      requestAnimationFrame(tick);
    }

    function commitFromY(y) {
      const rect = rail.getBoundingClientRect();
      if (!rect.height) return;
      const ratio = clamp((y - rect.top) / rect.height, 0, 1);
      scroller.scrollTop = ratio * maxScroll();
      target = ratio * 100;
      head = target;
      headV = 0;
    }

    rail.addEventListener("pointerdown", (event) => {
      dragging = true;
      rail.setPointerCapture(event.pointerId);
      commitFromY(event.clientY);
    });
    rail.addEventListener("pointermove", (event) => {
      if (dragging) commitFromY(event.clientY);
    });
    const endDrag = () => { dragging = false; };
    rail.addEventListener("pointerup", endDrag);
    rail.addEventListener("pointercancel", endDrag);
    rail.addEventListener("wheel", (event) => {
      if (rail.classList.contains("is-off")) return;
      scroller.scrollTop += event.deltaY;
      event.preventDefault();
    }, { passive: false });
    rail.addEventListener("keydown", (event) => {
      const max = maxScroll();
      const page = scroller.clientHeight * 0.9;
      const jumps = {
        ArrowDown: scroller.scrollTop + 80,
        ArrowUp: scroller.scrollTop - 80,
        PageDown: scroller.scrollTop + page,
        PageUp: scroller.scrollTop - page,
        Home: 0,
        End: max,
      };
      if (!(event.key in jumps)) return;
      event.preventDefault();
      scroller.scrollTop = clamp(jumps[event.key], 0, max);
    });

    requestAnimationFrame(tick);
  }

  mountWake();
})();
