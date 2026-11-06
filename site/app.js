// CQ Wiki – SPA thuần, dữ liệu trong window.CQ (sinh bởi scripts/build.py)
const D = window.CQ, $ = s => document.querySelector(s), main = $('#main');
const H = Object.fromEntries(D.heroes.map(h => [h.name, h]));
const CLS_VI = {Warrior: 'Chiến binh', Paladin: 'Hiệp sĩ', Archer: 'Cung thủ', Hunter: 'Thợ săn', Wizard: 'Pháp sư', Priest: 'Mục sư'};
const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]));
const href = n => '#/hero/' + encodeURIComponent(n);
const hl = n => H[n] ? `<a href="${href(n)}">${esc(n)}</a>` : esc(n);
// Ảnh: icon hero, skill, sigil (tên riêng giữ nguyên làm alt)
const IMG = D.images || {skill: {}, sigil: {}, src: {}};
const hic = (n, cl = 'hi') => H[n]?.img?.icon ? `<img class="${cl}" src="${H[n].img.icon}" alt="" loading="lazy">` : '';
const hli = n => H[n] ? `<a class="hl" href="${href(n)}">${hic(n)}${esc(n)}</a>` : esc(n);
const ski = s => `${IMG.skill[s] ? `<img class="si" src="${IMG.skill[s]}" alt="" loading="lazy">` : ''}${esc(s)}`;
const sgi = s => `${IMG.sigil[s] ? `<img class="gi" src="${IMG.sigil[s]}" alt="" loading="lazy">` : ''}${esc(s)}`;
const sigs = a => a.map(sgi).join(' + ');
const rich = s => esc(s).replace(/\*\*(.+?)\*\*/g, '<b>$1</b>').replace(/\[\[([^\]]+)\]\]/g, (m, n) => H[n] ? hli(n) : `<b>${n}</b>`);
const rtxt = s => `<div class="pre">${rich(s)}</div>`;
const bar = v => { const n = parseFloat(v); return isNaN(n) ? esc(v) : `<span class="score"><i style="width:${n * 10}%"></i></span> <b>${esc(v)}</b>/10`; };
const rk = r => `<span class="r r-${esc(r || '')}">${esc(r || '–')}</span>`;
// Hạng hero: hạng tự xếp (hero mới, dựa trên BWiki) có dấu * và tooltip
const rkh = h => h.rankAuto ? `<span title="Hạng tự xếp dựa trên đánh giá BWiki (hero chưa có trong tier list EN)">${rk(h.rank)}<sup class="auto">*</sup></span>` : rk(h.rank);
const cls = c => c ? `<a href="#/class/${c}">${c}</a>` : '–';
const txt = s => `<span class="pre">${esc(s)}</span>`;
// linkify: tô link cho tên hero xuất hiện nguyên văn trong ô
const linkCell = s => H[s] ? hl(s) : txt(s);

function table(head, rows, sortable = true) {
  return `<div class="tbl-wrap"><table class="${sortable ? 'sort' : ''}"><thead><tr>${head.map(h => `<th>${h}</th>`).join('')}</tr></thead><tbody>${
    rows.map(r => `<tr>${r.map(c => typeof c === 'object' && c ? `<td class="${c.c || ''}">${c.v}</td>` : `<td>${c ?? ''}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`;
}
const num = v => ({v: esc(v), c: 'num'});

// Bảng lưới giữ nguyên bố cục sheet (colspan/rowspan)
function grid(g) {
  const occ = new Set(), n = g.cols.length;
  let html = '<div class="tbl-wrap"><table class="grid">';
  g.rows.forEach((row, r) => {
    if (!row) {
      const covered = [...Array(n).keys()].filter(i => occ.has(r + ':' + i)).length;
      if (covered) html += '<tr>' + '<td></td>'.repeat(n - covered) + '</tr>';
      return;
    }
    html += '<tr>';
    let i = 0;
    for (const [col, t, cs, rs, imgs] of row) {
      const idx = g.cols.indexOf(col);
      for (; i < idx; i++) if (!occ.has(r + ':' + i)) html += '<td></td>';
      const im = imgs.map(s => `<img src="${s}" alt="">`).join('');
      html += `<td${cs > 1 ? ` colspan="${cs}"` : ''}${rs > 1 ? ` rowspan="${rs}"` : ''}>${im}${linkCell(t)}</td>`;
      for (let a = 1; a < rs; a++) for (let b = 0; b < cs; b++) occ.add((r + a) + ':' + (idx + b));
      i = idx + cs;
    }
    html += '</tr>';
  });
  return html + '</table></div>';
}

const pages = {
  '': () => {
    const cnt = r => D.heroes.filter(h => h.rank === r).length;
    return `<h1>Crusaders Quest Wiki</h1>
    <p>Wiki tiếng Việt tổng hợp từ bảng tier list & hướng dẫn cộng đồng <i>Crusaders Quest</i> (nhóm Foehn, Fizz, Navii...). Gồm <b>${D.heroes.length}</b> hero, <b>${D.dps.length}</b> mục DPS, <b>${D.archive.length}</b> ghi chép thay đổi qua các bản cập nhật.</p>
    ${D.announce.map(a => `<div class="notice">${esc(a)}</div>`).join('')}
    <h2>Thang xếp hạng</h2>
    ${table(['Hạng', 'Tên', 'Tỉ lệ hero', 'Số hero', 'Mô tả'], D.grades.map(g => [rk(g.g), esc(g.name), num(g.pct), num(cnt(g.g)), esc(g.desc)]), false)}
    <h2>Hero theo class</h2>
    <div class="cards">${D.classes.map(c => `<div class="card"><h3><a href="#/class/${c}">${c}</a> <span class="mute">(${CLS_VI[c]})</span></h3>
      <div class="mute">${D.heroes.filter(h => h.cls === c).length} hero · hạng S/A: ${D.heroes.filter(h => h.cls === c && /^(S|A|OP)$/.test(h.rank)).map(h => hli(h.name)).join(' ') || '–'}</div></div>`).join('')}</div>
    <h2>Mục lục</h2>
    <div class="chips">${[...document.querySelectorAll('#nav a')].map(a => `<a class="chip" href="${a.getAttribute('href')}">${a.textContent}</a>`).join('')}</div>`;
  },

  tier: () => `<h1>Tier List tổng</h1>
    <div class="notice">${esc(D.announce[1] || '')}</div>
    ${D.tiers.map(t => `<div class="tier-row"><b class="r-${t.tier}">${esc(t.tier === 'Unlock' ? 'Mở khóa' : t.tier)}</b><div>${t.heroes.map(n => `<a class="chip hl" href="${href(n)}">${hic(n)}${esc(n)}</a>`).join('')}${
      D.heroes.filter(h => h.rankAuto && h.rank === t.tier && !t.heroes.includes(h.name)).map(h => `<a class="chip hl auto" href="${href(h.name)}" title="Hạng tự xếp (hero mới, dựa trên BWiki)">${hic(h.name)}${esc(h.name)}<sup class="auto">*</sup></a>`).join('')}</div></div>`).join('')}
    <p class="mute">Tier list tổng (General Tierlist) – xếp hạng tổng thể. <sup class="auto">*</sup> = hero mới chưa có trong sheet EN, hạng do wiki này tự xếp dựa trên điểm đánh giá BWiki. Xếp hạng chi tiết theo từng hero nằm ở <a href="#/heroes">danh sách hero</a>.</p>`,

  heroes: (c) => {
    const ranks = ['OP', 'S', 'A', 'B', 'C', 'F', 'Unlock'];
    setTimeout(() => {
      const f = () => {
        const q = $('#fq').value.toLowerCase(), cl = $('#fc').value, r = $('#fr').value;
        document.querySelectorAll('#ht tbody tr').forEach(tr => {
          const h = H[tr.dataset.n];
          tr.hidden = !((!q || (h.name + ' ' + (h.note || '')).toLowerCase().includes(q)) && (!cl || h.cls === cl) && (!r || h.rank === r));
        });
      };
      ['#fq', '#fc', '#fr'].forEach(s => $(s).oninput = f); f();
    });
    const list = D.heroes.filter(h => h.name);
    return `<h1>${c ? `${c} <span class="mute">(${CLS_VI[c]})</span>` : 'Danh sách hero'}</h1>
    ${c && D.classNote[c] ? `<div class="notice">${esc(D.classNote[c])}</div>` : ''}
    <div class="filters"><input id="fq" placeholder="Lọc theo tên / nội dung..."><select id="fc"><option value="">Mọi class</option>${D.classes.map(x => `<option ${x === c ? 'selected' : ''}>${x}</option>`).join('')}</select>
    <select id="fr"><option value="">Mọi hạng</option>${ranks.map(x => `<option>${x}</option>`).join('')}</select></div>
    <div class="tbl-wrap"><table id="ht" class="sort"><thead><tr><th>Hero</th><th>Class</th><th>Hạng</th><th>Tier tổng</th><th>Nhận xét</th></tr></thead><tbody>
    ${list.map(h => `<tr data-n="${esc(h.name)}"><td>${hli(h.name)}</td><td>${cls(h.cls)}</td><td>${rkh(h)}</td><td>${h.tier ? rk(h.tier) : ''}</td><td>${esc(h.note || '')}</td></tr>`).join('')}
    </tbody></table></div>`;
  },

  class: c => pages.heroes(c),

  hero: name => {
    const h = H[name];
    if (!h) return `<h1>Không tìm thấy</h1><p>Không có hero tên “${esc(name)}”.</p>`;
    const d = (h.dps || [])[0];
    const rows = [['Class', cls(h.cls) + (h.cls ? ` <span class="mute">(${CLS_VI[h.cls]})</span>` : '')], ...(h.rank ? [['Xếp hạng', rkh(h) + (h.rankAuto ? ' <span class="mute">tự xếp (hero mới)</span>' : '')]] : []), ...(h.tier ? [['Tier tổng', rk(h.tier)]] : []),
      ['Skill SP khuyên dùng', (h.skills?.length ? h.skills : (h.bw?.skills || []).map(x => x.name)).map(ski).join('<br>') || '–'],
      ['Skin (Legacy)', (h.skins || []).map(s => `${s.img ? `<img class="sk" src="${s.img}" alt="" loading="lazy"><br>` : ''}${esc(s.name)} <span class="mute">${esc(s.stat)}</span>`).join('<br>') || '–']];
    if (d) rows.push(['DPS (thường)', esc(d.reg)], ['DPS (Champion)', esc(d.champ)]);
    if (h.guide) rows.push(['Có cần không?', `<b>${esc(h.guide.need)}</b> <span class="mute">${esc(h.guide.purpose)}</span>`]);
    const bw = h.bw || {};
    if (bw.tags) rows.push(['Đặc điểm', `<div class="chips">${bw.tags.map(t => `<span class="chip tag">${esc(t)}</span>`).join('')}</div>`]);
    const builds = (h.builds || []).map((b, i) => `<h3>${b.alt ? 'Build thay thế (ALT.)' : 'Build chính'}</h3>
      <table>${[['Nâng cấp SBW', b.slot.map(esc).join(' + ')], ['CRF (AA / AF / AA+SP)', esc(b.crf.join(' / '))], ['Set sigil', esc(b.set || '–')],
        ['Sigil cuối game', sigs(b.end)], ['Sigil giữa game', sigs(b.mid)], ['Sigil đầu game', sigs(b.early)]]
        .map(([k, v]) => `<tr><th>${k}</th><td>${v}</td></tr>`).join('')}</table>
      ${b.note ? `<p class="pre">${esc(b.note)}</p>` : ''}`).join('');
    const logs = (h.log || []).map(i => D.archive[i]).map(e => `<div class="log"><div class="mute"><b>${esc(e.type)}</b> · ${esc(e.date)} · bản ${esc(e.patch)}</div>${txt(e.note)}</div>`).join('');
    return `<h1>${esc(h.name)}</h1>
    <table class="infobox"><caption>${esc(h.name)}</caption>${h.img?.art || h.img?.icon ? `<tr><td colspan="2" class="art"><img src="${h.img.art || h.img.icon}" alt="${esc(h.name)}"></td></tr>` : ''}${rows.filter(([, v]) => v !== '–').map(([k, v]) => `<tr><th>${k}</th><td>${v}</td></tr>`).join('')}</table>
    ${h.note ? `<h2>Đánh giá <span class="mute">(${h.rankAuto ? 'tự xếp hạng – tổng hợp từ điểm BWiki, hero chưa có trong tier list EN' : 'tier list cộng đồng EN'})</span></h2><p>${esc(h.note)}</p>` : (h.bw ? '' : '<h2>Đánh giá</h2><p class="mute">Chưa có nhận xét.</p>')}
    ${(h.rankNote || []).map(n => `<p class="mute">Ghi chú: ${esc(n)}</p>`).join('')}
    ${h.skillNote ? `<p class="mute pre">${esc(h.skillNote)}</p>` : ''}
    ${h.guide ? `<div class="notice"><b>Có cần hero này?</b> ${esc(h.guide.need)} · <i>${esc(h.guide.purpose)}</i><br>${esc(h.guide.note)}</div>` : ''}
    ${bwSection(h)}
    <div style="clear:both"></div>
    ${builds ? `<h2>Build vũ khí & sigil <span class="mute">(tier list cộng đồng EN)</span></h2>${builds}` : ''}
    ${h.dps ? `<h2>DPS</h2>${dpsTable(h.dps)}` : ''}
    ${logs ? `<h2>Lịch sử thay đổi</h2>${logs}` : ''}
    ${h.img?.src ? `<p class="mute">Nguồn ảnh: <a href="${h.img.src}" target="_blank" rel="noopener">BWiki – ${esc(h.img.zh)}</a></p>` : ''}
    <div style="clear:both"></div>`;
  },

  dps: () => `<h1>Bảng DPS</h1>
    <p class="mute">DPS tính trên mục tiêu tiêu chuẩn. <b>Thường</b>: không tạo block; <b>Champion</b>: có tạo block từ champion; <b>Vô hạn</b>: block vô hạn. “Hit” = số hit/giây. “Block/phút” = lượng block tối đa hero tiêu thụ mỗi phút. “Tỉ lệ” = DPS so với Nebula. Bấm tiêu đề cột để sắp xếp.</p>
    <div class="filters"><select id="dc"><option value="">Mọi class</option>${D.classes.map(x => `<option>${x}</option>`).join('')}</select></div>
    <div id="dt">${dpsTable(D.dps)}</div>`,

  sigils: () => `<h1>Set sigil</h1><p class="mute">Các bộ sigil được dùng trong phần build hero, theo từng giai đoạn. “Số hero dùng” = số hero được khuyên dùng set này.</p>
    ${table(['Set', 'Cuối game', 'Giữa game', 'Đầu game', 'Số hero dùng'], D.sigilsets.map(s => [esc(s.name), s.end.map(sgi).join('<br>'), s.mid.map(sgi).join('<br>'), s.early.map(sgi).join('<br>'), num(s.used)]))}`,

  equip: () => {
    const fmt = (k, v) => typeof v === 'number' && v < 1 && !['HP', 'HAP', 'Arm', 'Res', 'APen', 'Rpen'].includes(k) ? `${(v * 100).toFixed(2).replace(/\.?0+$/, '')}%` : v;
    return `<h1>Tùy chọn trang bị</h1><p class="mute">Giá trị chỉ số của các tùy chọn vũ khí linh hồn (A = Tấn công, D = Phòng thủ, F = Chức năng), nhẫn/phụ và hiệu ứng phụ kiện.</p>
    ${table(['Tùy chọn', 'Loại', 'Chỉ số', 'Hiệu ứng'], D.equip.map(e => [esc(e.opt), esc(e.type), Object.entries(e.stats).map(([k, v]) => `${k}: <b>${esc(fmt(k, v))}</b>`).join(', '), esc(e.note)]))}`;
  },

  skins: () => `<h1>Skin (Legacy)</h1><p class="mute">Trừ khi bạn mê tối ưu, hãy chọn skin vì đẹp, không phải vì chỉ số. (+ = tăng nhẹ, ++ = tăng nhiều)</p>
    ${table(['Hero', 'Class', 'Lựa chọn 1', 'Chỉ số', 'Lựa chọn 2', 'Chỉ số'], D.heroes.filter(h => h.skins).map(h => [hli(h.name), cls(h.cls), skinCell(h.skins[0]), esc(h.skins[0].stat), skinCell(h.skins[1]), esc(h.skins[1]?.stat || '')]))}`,

  challenge: () => `<h1>Chỉ số Challenge & Raid</h1><p class="mute">Chỉ số boss của các màn Challenge (C1–C16H), FoRS và Raid 1–5. Mỗi màn có tối đa 4 boss: HP, xuyên giáp (A/RPen), giáp/kháng phép, DR, né tránh, CR. Ô #REF! là dữ liệu đã hỏng sẵn trong sheet gốc.</p>${grid(D.grids['Challenge Stat'])}`,
  totalwar: () => `<h1>Hướng dẫn Total War</h1>${grid(D.grids['Total War Guide'])}`,
  ep6: () => `<h1>Hướng dẫn Challenge EP6 <span class="mute">(đang soạn – WIP)</span></h1>${grid(D.grids['EP6 Challenge Guide'])}`,
  changelog: () => `<h1>Change Log</h1>${grid(D.grids['Change Log'])}`,

  guide: k => {
    const T = {coupons: ['Coupon đang hoạt động', 'Active Coupons'], gloss2: ['Thuật ngữ chung (bản mới)', 'General Glossary'], sp: ['Thuật ngữ skill SP', 'SP Skills Glossary'],
      picking: ['Chọn hero (contract)', 'Picking Heroes'], promo: ['Hero promo/legend đáng dùng', 'Useful Promo/Legend Heroes'], seasonal: ['Lịch hero theo mùa', 'Seasonal Schedule'],
      resources: ['Tài nguyên', 'Resources'], maths: ['Toán CQ 101', 'CQ Maths 101'], rings: ['Hướng dẫn nhẫn', 'Ring Guide'], goddess: ['Goddess', 'Goddesses'],
      gift: ['Lịch quà hằng ngày', 'Daily Surprise Gift Schedule'], map: ['Bản đồ thế giới', 'World Map'], story: ['Bí mật Story Mode', 'Story Mode Secrets'], credits2: ['Ghi công & tài liệu thêm', 'Credits']}[k];
    if (!T) return pages['']();
    return `<h1>${T[0]}</h1><p class="mute">Nguồn: sheet “CQ Guide to Almost Everything” (tab ${esc(T[1])}).</p>${grid(D.grids[T[1]])}`;
  },

  glossary: () => `<h1>Thuật ngữ</h1>${table(['Thuật ngữ', 'Định nghĩa'], D.glossary.map(g => [`<b>${esc(g.term)}</b>`, txt(g.def)]), false)}`,

  archive: () => {
    const types = [...new Set(D.archive.map(a => a.type).filter(Boolean))].sort();
    setTimeout(() => {
      const f = () => {
        const q = $('#aq').value.toLowerCase(), t = $('#at').value;
        $('#al').innerHTML = D.archive.filter(a => (!t || a.type === t) && (!q || (a.hero + ' ' + a.note + ' ' + a.patch).toLowerCase().includes(q)))
          .map(a => `<div class="log"><div class="mute"><b>${hl(a.hero)}</b> · ${esc(a.type)} · ${esc(a.date)} · bản ${esc(a.patch)}</div>${txt(a.note)}</div>`).join('') || '<p class="mute">Không có kết quả.</p>';
      };
      $('#aq').oninput = $('#at').onchange = f; f();
    });
    return `<h1>Lưu trữ thay đổi</h1><p class="mute">Toàn bộ ghi chép thay đổi tier list, DPS, cân bằng hero từ 2020 đến 2023.</p>
    <div class="filters"><input id="aq" placeholder="Lọc theo hero / nội dung / bản cập nhật..."><select id="at"><option value="">Mọi loại</option>${types.map(t => `<option>${esc(t)}</option>`).join('')}</select></div><div id="al"></div>`;
  },

  credits: () => `<h1>Ghi công</h1><p>Dữ liệu gốc: bảng tính tier list cộng đồng Crusaders Quest. Bản tiếng Việt này chỉ dịch nội dung, tên riêng giữ nguyên.</p>
    ${table(['Người đóng góp', 'Vai trò'], D.contrib.map(c => [esc(c.name), esc(c.desc)]), false)}
    <h2>Nguồn hình ảnh</h2>
    <p>Hình ảnh hero, skill, sigil và skin thuộc bản quyền LoadComplete / NHN (Hangame). Wiki này chỉ dùng để tham khảo, phi thương mại.</p>
    <ul>
      <li>Icon & ảnh chân dung hero, ảnh sigil, ảnh skin, một phần icon skill: <a href="https://wiki.biligame.com/cq/" target="_blank" rel="noopener">克鲁赛德战记 BWIKI (wiki.biligame.com/cq)</a>. Mỗi trang hero có link tới trang nguồn tương ứng.</li>
      <li>Phần lớn icon skill SP: <a href="https://crusadersquest.fandom.com/wiki/Special_Skills" target="_blank" rel="noopener">Crusaders Quest Wiki (Fandom)</a>.</li>
      <li>Icon trong bảng DPS / Challenge Stat: lấy từ chính bảng tính gốc.</li>
    </ul>`,
};

// Phần đánh giá cập nhật từ BWiki (CN) – đã Việt hóa
function bwSection(h) {
  const b = h.bw;
  if (!b) return '';
  const sec = (t, v) => v ? `<h3>${t}</h3>${rtxt(v)}` : '';
  return `<h2>Đánh giá cập nhật <span class="mute">(BWiki CN)</span></h2>
    ${b.review ? rtxt(b.review) : ''}
    ${b.scores?.length ? `<h3>Điểm theo nội dung</h3>${table(['Nội dung', 'Điểm', 'Lý do'], b.scores.map(x => [esc(x.k), {v: bar(x.v), c: 'nowrap'}, rich(x.why)]), false)}` : ''}
    ${b.kit ? `<details><summary><b>Bộ kỹ năng chi tiết</b></summary>${rtxt(b.kit)}</details>` : ''}
    ${b.skills?.length ? `<h3>Skill SP khuyên dùng</h3>${table(['Skill', 'Lý do'], b.skills.map(x => [ski(x.name), rich(x.why)]), false)}` : ''}
    ${b.builds?.length ? `<h3>Build SBW & sigil khuyên dùng</h3>${table(['Cấu hình', 'Nâng cấp SBW', 'Nhẫn', 'Set sigil', 'Ghi chú'], b.builds.map(x => [esc(x.label || '–'), esc(x.slot.join(' + ')), esc(x.ring), esc(x.set), rich(x.note)]), false)}` : ''}
    ${sec('Nhẫn khuyên dùng', b.ring)}${sec('Phụ kiện khuyên dùng', b.acc)}
    ${sec('Đội hình gợi ý', b.team)}${sec('Đánh giá SBW', b.sbw)}${sec('Cơ chế block', b.block)}${sec('Kế thừa', b.inherit)}
    <p class="mute">Nguồn: <a href="${b.src}" target="_blank" rel="noopener">BWiki – ${esc(b.zh)}</a> (dịch từ tiếng Trung).</p>`;
}

const skinCell = s => s ? `<div class="skc">${s.img ? `<img class="sk" src="${s.img}" alt="" loading="lazy">` : ''}<span>${esc(s.name)}</span></div>` : '';

function dpsTable(list) {
  return table(['Hero', 'Class', 'DPS thường', 'Hit', 'DPS Champion', 'Hit', 'DPS vô hạn', 'Hit', 'Block/phút', 'Điều kiện', 'Tỉ lệ (thường/champ/vô hạn)', 'Pen', 'Ghi chú'],
    list.map(d => [`${hli(d.name)}${d.icon ? ` <img class="ic" src="${d.icon}" alt="" title="Biểu tượng loại sát thương">` : ''}`, cls(d.cls), num(d.reg), num(d.regHit), num(d.champ), num(d.champHit), num(d.inf), num(d.infHit),
      txt(d.bpm), txt(d.cond), num(d.scale.join(' / ')), esc(d.pen), txt([d.note, ...d.tips].filter(Boolean).join('\n'))]));
}

// Sắp xếp bảng khi bấm tiêu đề
main.addEventListener('click', e => {
  const th = e.target.closest('table.sort th');
  if (!th) return;
  const tb = th.closest('table').tBodies[0], i = th.cellIndex, dir = th.dataset.d = th.dataset.d === '1' ? '-1' : '1';
  const key = tr => { const t = tr.cells[i]?.textContent.trim() || ''; const n = parseFloat(t.replace(/,/g, '')); return isNaN(n) ? t.toLowerCase() : n; };
  [...tb.rows].sort((a, b) => { const x = key(a), y = key(b); return (typeof x === typeof y ? (x > y ? 1 : x < y ? -1 : 0) : typeof x === 'number' ? -1 : 1) * dir; }).forEach(r => tb.appendChild(r));
});
main.addEventListener('change', e => {
  if (e.target.id === 'dc') $('#dt').innerHTML = dpsTable(D.dps.filter(d => !e.target.value || d.cls === e.target.value));
});

function route() {
  const [, p = '', arg] = location.hash.split('/');
  const fn = pages[p] || pages[''];
  main.innerHTML = fn(arg && decodeURIComponent(arg));
  document.querySelectorAll('#nav a').forEach(a => a.classList.toggle('on', a.getAttribute('href') === location.hash || (a.getAttribute('href') === '#/' && !p)));
  document.title = (main.querySelector('h1')?.textContent || 'CQ Wiki') + ' – Crusaders Quest Wiki';
  $('#nav').classList.remove('open');
  $('#sugg').hidden = true; $('#q').value = '';
  scrollTo(0, 0);
}
$('#clsNav').innerHTML = D.classes.map(c => `<a href="#/class/${c}">${c} <span class="mute">(${CLS_VI[c]})</span></a>`).join('');
$('#menuBtn').onclick = () => $('#nav').classList.toggle('open');

// Tìm kiếm nhanh: hero + trang
const idx = [...D.heroes.map(h => ({t: h.name, s: `${h.cls || ''} ${h.rank ? '· hạng ' + h.rank : ''}`, h: href(h.name)})),
  ...[...document.querySelectorAll('#nav a')].map(a => ({t: a.textContent, s: 'trang', h: a.getAttribute('href')}))];
let sel = 0;
$('#q').oninput = () => {
  const q = $('#q').value.trim().toLowerCase(), box = $('#sugg');
  const res = q ? idx.filter(x => x.t.toLowerCase().includes(q)).sort((a, b) => a.t.toLowerCase().indexOf(q) - b.t.toLowerCase().indexOf(q)).slice(0, 12) : [];
  sel = 0; box.hidden = !res.length;
  box.innerHTML = res.map((x, i) => `<a href="${x.h}" class="${i ? '' : 'on'}">${esc(x.t)} <span class="mute">${esc(x.s)}</span></a>`).join('');
};
$('#q').onkeydown = e => {
  const a = [...$('#sugg').children];
  if (!a.length) return;
  if (e.key === 'ArrowDown' || e.key === 'ArrowUp') { e.preventDefault(); a[sel].classList.remove('on'); sel = (sel + (e.key === 'ArrowDown' ? 1 : a.length - 1)) % a.length; a[sel].classList.add('on'); }
  if (e.key === 'Enter') { location.hash = a[sel].getAttribute('href'); $('#q').blur(); }
};
$('#sugg').onclick = () => setTimeout(() => $('#q').blur());
$('#q').onblur = () => setTimeout(() => { $('#sugg').hidden = true; $('#q').value = ''; }, 150);

addEventListener('hashchange', route);
route();
