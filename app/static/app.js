function $(id) { return document.getElementById(id); }
function _v(id) { const e = $(id); return e ? e.value : ''; }

class APIClient {
  constructor(base) { this.base = base || ''; }
  async req(method, p, body) {
    const o = { method, headers: {} };
    if (body) { o.headers['Content-Type'] = 'application/json'; o.body = JSON.stringify(body); }
    const r = await fetch(this.base + p, o);
    const t = await r.text();
    try { return { ok: r.ok, status: r.status, data: JSON.parse(t) }; }
    catch { return { ok: r.ok, status: r.status, data: t }; }
  }
  get(p) { return this.req('GET', p); }
  post(p, b) { return this.req('POST', p, b); }
  patch(p, b) { return this.req('PATCH', p, b); }
  del(p) { return this.req('DELETE', p); }
}

const _EP_MAP = {
  person:   { add: ['post','POST','/v1/people'],                             edit: ['patch','PATCH','/v1/people/{uuid_person}'],                    delete: ['delete','DELETE','/v1/people/{uuid_person}'] },
  address:  { add: ['post','POST','/v1/people/{uuid_person}/addresses'],     edit: ['patch','PATCH','/v1/people/addresses/{uuid_address}'],         delete: ['delete','DELETE','/v1/people/addresses/{uuid_address}'] },
  email:    { add: ['post','POST','/v1/people/{uuid_person}/emails'],        edit: ['patch','PATCH','/v1/people/emails/{uuid_email}'],              delete: ['delete','DELETE','/v1/people/emails/{uuid_email}'] },
  phone:    { add: ['post','POST','/v1/people/{uuid_person}/phones'],        edit: ['patch','PATCH','/v1/people/phones/{uuid_phone}'],              delete: ['delete','DELETE','/v1/people/phones/{uuid_phone}'] },
  identity: { add: ['post','POST','/v1/people/{uuid_person}/identifiers'],   edit: ['patch','PATCH','/v1/people/identifiers/{uuid_identifier}'],    delete: ['delete','DELETE','/v1/people/identifiers/{uuid_identifier}'] },
  social:   { add: ['post','POST','/v1/people/{uuid_person}/emergency-contacts'], edit: ['patch','PATCH','/v1/people/emergency-contacts/{uuid_emergency}'], delete: ['delete','DELETE','/v1/people/emergency-contacts/{uuid_emergency}'] },
};

class CoreUI {
  constructor() {
    this.msg = $('msg');
    this.api = new APIClient();
    this._tab = null;
    this._mode = null;
    this._nav();
    this._person();
    this._address();
    this._email();
    this._phone();
    this._identity();
    this._social();
    this._validation();
  }
  say(t, c) { this.msg.textContent = t; this.msg.style.color = c || '#00ff88'; }

  _nav() {
    document.querySelectorAll('.topbar nav button').forEach(b => b.onclick = () => {
      document.querySelectorAll('.topbar nav button').forEach(x => x.classList.remove('active'));
      document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
      b.classList.add('active');
      $('sec-' + b.dataset.section).classList.add('active');
    });
  }

  _open(mode, tab, fetchFn) {
    this._mode = mode;
    this._tab = tab;
    const pnl = $('side-panel'), ovl = $('overlay');
    const close = () => { ovl.classList.remove('show'); pnl.classList.remove('show'); };
    ovl.onclick = close;
    $('panel-close').onclick = close;
    $(tab + '-cancel').onclick = close;

    // Show only the current tab's content wrap, hide the rest
    ['person', 'address', 'email', 'phone', 'identity', 'social'].forEach(t => {
      const w = $(t + '-panel-wrap');
      if (w) w.style.display = (t === tab) ? 'block' : 'none';
    });

    $('panel-title').textContent = tab.toUpperCase() + ' — MANAGE';

    const ep = _EP_MAP[tab]?.[mode];
    const footer = $(tab + '-endpoint-footer');
    if (footer && ep) footer.innerHTML = `<span class="verb ${ep[0]}">${ep[1]}</span><span class="path">${ep[2]}</span>`;

    $(tab + '-mode').style.display = 'block';
    $(tab + '-mode').style.color = {add:'var(--color-green)',edit:'var(--color-amber)',delete:'var(--color-red)'}[mode];
    $(tab + '-mode').textContent = 'MODE: ' + mode.toUpperCase();

    const editSec = $(tab + '-edit-section');
    if (editSec) editSec.style.display = (mode === 'add') ? 'none' : 'block';
    $(tab + '-save').textContent = {add:'SAVE',edit:'UPDATE',delete:'DELETE'}[mode];

    const body = $(tab + '-panel-body');
    body.querySelectorAll('input, select').forEach(i => {
      i.value = i.getAttribute('data-init') || '';
      i.readOnly = (mode === 'delete');
    });
    const uuidInp = $(tab + '-edit-uuid');
    if (uuidInp) uuidInp.value = '';

    pnl.classList.add('show');
    ovl.classList.add('show');
  }

  _out(preId, res, label) {
    const pre = $(preId);
    if (res.ok) {
      const items = res.data.data !== undefined ? res.data.data : res.data;
      pre.textContent = res.status === 204 ? 'No content.' : JSON.stringify(items, null, 2);
      this.say(label + ' OK.');
    } else {
      pre.textContent = `ERROR ${res.status}:\n${JSON.stringify(res.data, null, 2)}`;
      this.say(label + ' failed', '#ff4444');
    }
  }

  _done(ok, preId, label) {
    $(this._tab + '-save').textContent = '...';
    if (!ok) $(this._tab + '-save').textContent = 'ERROR';
  }

  // ── PERSON ──────────────────────────────────────────────────
  _person() {
    const T = 'person';
    $(T + '-list-btn').onclick = () => this.api.get('/v1/people').then(r => this._out('out-' + T, r, 'List'));
    $(T + '-fetch-btn').onclick = () => {
      const u = _v(T + '-fetch-uuid');
      if (!u) return this.say('UUID required.', '#ff4444');
      this.api.get('/v1/people/' + u).then(r => this._out('out-' + T, r, 'Fetch'));
    };
    $(T + '-add-btn').onclick = () => this._open('add', T, null);
    $(T + '-edit-btn').onclick = () => this._open('edit', T, null);
    $(T + '-delete-btn').onclick = () => this._open('delete', T, null);

    $(T + '-edit-fetch-btn').onclick = () => {
      const u = _v(T + '-edit-uuid');
      if (!u) return this.say('UUID required.', '#ff4444');
      this.api.get('/v1/people/' + u).then(r => {
        if (!r.ok) return this._out('out-' + T, r, 'Fetch');
        const d = (r.data.data || r.data);
        $('p-email').value = d.email?.address || '';
        $('p-fname').value = d.first_name || '';
        $('p-lname').value = d.last_name || '';
        $('p-phone-code').value = d.phone?.code || '+52';
        $('p-phone-num').value = d.phone?.number || '';
        $('p-birth').value = d.birth?.date || '1990-01-01';
        $('p-birth-country').value = d.birth?.key_country || 'MX';
        if (d.personal_identifier) {
          $('p-id-type').value = d.personal_identifier.type || 'NATIONAL_ID';
          $('p-id-value').value = d.personal_identifier.value || '';
        }
        this.say('Data loaded.');
      });
    };

    $(T + '-save').onclick = async () => {
      const m = this._mode;
      if (m === 'delete') {
        const u = _v(T + '-edit-uuid');
        if (!u) return this.say('Fetch UUID first.', '#ff4444');
        if (!confirm('Delete person ' + u + '?')) return;
        const r = await this.api.del('/v1/people/' + u);
        this._out('out-' + T, r, 'Delete');
        return $('panel-close').click();
      }
      const email = _v('p-email');
      if (!email) return this.say('Email required.', '#ff4444');
      const dto = {
        email: { address: email, type: 'PERSONAL' },
        phone: { code: _v('p-phone-code') || '+52', number: _v('p-phone-num') || '5500000000', type: 'MOBILE' },
        first_name: _v('p-fname') || 'Test', last_name: _v('p-lname') || 'User',
        birth: { date: $('p-birth').value || '1990-01-01', key_country: _v('p-birth-country') || 'MX' },
      };
      const pv = _v('p-id-value');
      if (pv) dto.personal_identifier = { type: _v('p-id-type') || 'NATIONAL_ID', value: pv };
      if (m === 'add') {
        const r = await this.api.post('/v1/people', dto);
        this._out('out-' + T, r, 'Create');
        $('panel-close').click();
      } else {
        const u = _v(T + '-edit-uuid');
        if (!u) return this.say('Fetch UUID first.', '#ff4444');
        const r = await this.api.patch('/v1/people/' + u, dto);
        this._out('out-' + T, r, 'Update');
        $('panel-close').click();
      }
    };
  }

  // ── ADDRESS ─────────────────────────────────────────────────
  _address() {
    const T = 'address';
    $(T + '-fetch-btn').onclick = () => {
      const u = _v(T + '-fetch-uuid');
      if (!u) return this.say('UUID required.', '#ff4444');
      this.api.get('/v1/people/' + u + '/address').then(r => this._out('out-' + T, r, 'Fetch'));
    };
    $(T + '-add-btn').onclick = () => this._open('add', T);
    $(T + '-edit-btn').onclick = () => this._open('edit', T);
    $(T + '-delete-btn').onclick = () => this._open('delete', T);

    $(T + '-edit-fetch-btn').onclick = () => {
      const u = _v(T + '-edit-uuid');
      if (!u) return this.say('UUID required.', '#ff4444');
      this.api.get('/v1/people/addresses/' + u).then(r => {
        if (!r.ok) return this._out('out-' + T, r, 'Fetch');
        const d = r.data.data || r.data;
        $('a-street').value = d.address || '';
        $('a-zip').value = d.postal_code || '';
        $('a-state').value = d.key_state || 'CMX';
        $('a-mun').value = d.key_municipality || '016';
        this.say('Data loaded.');
      });
    };

    $(T + '-save').onclick = async () => {
      const m = this._mode;
      if (m === 'delete') {
        const u = _v(T + '-edit-uuid');
        if (!u) return this.say('UUID address required.', '#ff4444');
        if (!confirm('Delete address ' + u + '?')) return;
        const r = await this.api.del('/v1/people/addresses/' + u);
        this._out('out-' + T, r, 'Delete');
        return $('panel-close').click();
      }
      const dto = { address: _v('a-street') || 'Test Street 123', postal_code: _v('a-zip') || '06600', key_state: _v('a-state') || 'CMX', key_municipality: _v('a-mun') || '016' };
      if (m === 'add') {
        const u = _v(T + '-fetch-uuid');
        if (!u) return this.say('Enter person UUID.', '#ff4444');
        const r = await this.api.post('/v1/people/' + u + '/addresses', dto);
        this._out('out-' + T, r, 'Create');
        $('panel-close').click();
      } else {
        const u = _v(T + '-edit-uuid');
        if (!u) return this.say('UUID address required.', '#ff4444');
        const r = await this.api.patch('/v1/people/addresses/' + u, dto);
        this._out('out-' + T, r, 'Update');
        $('panel-close').click();
      }
    };
  }

  // ── EMAIL ───────────────────────────────────────────────────
  _email() {
    const T = 'email';
    $(T + '-fetch-btn').onclick = () => {
      const u = _v(T + '-fetch-uuid');
      if (!u) return this.say('UUID required.', '#ff4444');
      this.api.get('/v1/people/' + u + '/emails').then(r => this._out('out-' + T, r, 'Fetch emails'));
    };
    $(T + '-add-btn').onclick = () => this._open('add', T);
    $(T + '-edit-btn').onclick = () => this._open('edit', T);
    $(T + '-delete-btn').onclick = () => this._open('delete', T);

    $(T + '-edit-fetch-btn').onclick = () => {
      const u = _v(T + '-edit-uuid');
      if (!u) return this.say('UUID required.', '#ff4444');
      this.api.get('/v1/people/emails/' + u).then(r => {
        if (!r.ok) return this._out('out-' + T, r, 'Fetch');
        const d = r.data.data || r.data;
        $('em-addr').value = d.email || '';
        $('em-type').value = d.type_email || 'PERSONAL';
        this.say('Data loaded.');
      });
    };

    $(T + '-save').onclick = async () => {
      const m = this._mode;
      if (m === 'delete') {
        const u = _v(T + '-edit-uuid');
        if (!u) return this.say('UUID email required.', '#ff4444');
        if (!confirm('Delete email ' + u + '?')) return;
        const r = await this.api.del('/v1/people/emails/' + u);
        this._out('out-' + T, r, 'Delete');
        return $('panel-close').click();
      }
      const addr = _v('em-addr');
      if (!addr) return this.say('Email required.', '#ff4444');
      const dto = { email: addr, type_email: _v('em-type') || 'PERSONAL' };
      if (m === 'add') {
        const u = _v(T + '-fetch-uuid');
        if (!u) return this.say('Enter person UUID.', '#ff4444');
        const r = await this.api.post('/v1/people/' + u + '/emails', dto);
        this._out('out-' + T, r, 'Create');
        $('panel-close').click();
      } else {
        const u = _v(T + '-edit-uuid');
        if (!u) return this.say('UUID email required.', '#ff4444');
        const r = await this.api.patch('/v1/people/emails/' + u, dto);
        this._out('out-' + T, r, 'Update');
        $('panel-close').click();
      }
    };
  }

  // ── PHONE ───────────────────────────────────────────────────
  _phone() {
    const T = 'phone';
    $(T + '-fetch-btn').onclick = () => {
      const u = _v(T + '-fetch-uuid');
      if (!u) return this.say('UUID required.', '#ff4444');
      this.api.get('/v1/people/' + u + '/phones').then(r => this._out('out-' + T, r, 'Fetch phones'));
    };
    $(T + '-add-btn').onclick = () => this._open('add', T);
    $(T + '-edit-btn').onclick = () => this._open('edit', T);
    $(T + '-delete-btn').onclick = () => this._open('delete', T);

    $(T + '-edit-fetch-btn').onclick = () => {
      const u = _v(T + '-edit-uuid');
      if (!u) return this.say('UUID required.', '#ff4444');
      this.api.get('/v1/people/phones/' + u).then(r => {
        if (!r.ok) return this._out('out-' + T, r, 'Fetch');
        const d = r.data.data || r.data;
        $('ph-code').value = d.code || '+52';
        $('ph-num').value = d.number || '';
        $('ph-type').value = d.type_phone || 'MOBILE';
        this.say('Data loaded.');
      });
    };

    $(T + '-save').onclick = async () => {
      const m = this._mode;
      if (m === 'delete') {
        const u = _v(T + '-edit-uuid');
        if (!u) return this.say('UUID phone required.', '#ff4444');
        if (!confirm('Delete phone ' + u + '?')) return;
        const r = await this.api.del('/v1/people/phones/' + u);
        this._out('out-' + T, r, 'Delete');
        return $('panel-close').click();
      }
      const num = _v('ph-num');
      if (!num) return this.say('Phone number required.', '#ff4444');
      const dto = { code: _v('ph-code') || '+52', number: num, type_phone: _v('ph-type') || 'MOBILE' };
      if (m === 'add') {
        const u = _v(T + '-fetch-uuid');
        if (!u) return this.say('Enter person UUID.', '#ff4444');
        const r = await this.api.post('/v1/people/' + u + '/phones', dto);
        this._out('out-' + T, r, 'Create');
        $('panel-close').click();
      } else {
        const u = _v(T + '-edit-uuid');
        if (!u) return this.say('UUID phone required.', '#ff4444');
        const r = await this.api.patch('/v1/people/phones/' + u, dto);
        this._out('out-' + T, r, 'Update');
        $('panel-close').click();
      }
    };
  }

  // ── IDENTITY ────────────────────────────────────────────────
  _identity() {
    const T = 'identity';
    $(T + '-fetch-btn').onclick = () => {
      const u = _v(T + '-fetch-uuid');
      if (!u) return this.say('UUID required.', '#ff4444');
      this.api.get('/v1/people/' + u + '/identifiers').then(r => this._out('out-' + T, r, 'Fetch'));
    };
    $(T + '-add-btn').onclick = () => this._open('add', T);
    $(T + '-edit-btn').onclick = () => this._open('edit', T);
    $(T + '-delete-btn').onclick = () => this._open('delete', T);

    $(T + '-edit-fetch-btn').onclick = () => {
      const u = _v(T + '-edit-uuid');
      if (!u) return this.say('UUID required.', '#ff4444');
      this.api.get('/v1/people/identifiers/' + u).then(r => {
        if (!r.ok) return this._out('out-' + T, r, 'Fetch');
        const d = r.data.data || r.data;
        $('i-type').value = d.type || 'NATIONAL_ID';
        $('i-val').value = d.value || '';
        this.say('Data loaded.');
      });
    };

    $(T + '-save').onclick = async () => {
      const m = this._mode;
      if (m === 'delete') {
        const u = _v(T + '-edit-uuid');
        if (!u) return this.say('UUID identifier required.', '#ff4444');
        if (!confirm('Delete identifier ' + u + '?')) return;
        const r = await this.api.del('/v1/people/identifiers/' + u);
        this._out('out-' + T, r, 'Delete');
        return $('panel-close').click();
      }
      const dto = { id_identifier_type: _v('i-type') || 'NATIONAL_ID', identifier_value: _v('i-val') };
      if (!dto.identifier_value) return this.say('Value required.', '#ff4444');
      if (m === 'add') {
        const u = _v(T + '-fetch-uuid');
        if (!u) return this.say('Enter person UUID.', '#ff4444');
        const r = await this.api.post('/v1/people/' + u + '/identifiers', dto);
        this._out('out-' + T, r, 'Create');
        $('panel-close').click();
      } else {
        const u = _v(T + '-edit-uuid');
        if (!u) return this.say('UUID identifier required.', '#ff4444');
        const r = await this.api.patch('/v1/people/identifiers/' + u, dto);
        this._out('out-' + T, r, 'Update');
        $('panel-close').click();
      }
    };
  }

  // ── SOCIAL ──────────────────────────────────────────────────
  _social() {
    const T = 'social';
    $(T + '-fetch-btn').onclick = () => {
      const u = _v(T + '-fetch-uuid');
      if (!u) return this.say('UUID required.', '#ff4444');
      this.api.get('/v1/people/' + u + '/emergency-contacts').then(r => this._out('out-' + T, r, 'Fetch'));
    };
    $(T + '-add-btn').onclick = () => this._open('add', T);
    $(T + '-edit-btn').onclick = () => this._open('edit', T);
    $(T + '-delete-btn').onclick = () => this._open('delete', T);

    $(T + '-edit-fetch-btn').onclick = () => {
      const u = _v(T + '-edit-uuid');
      if (!u) return this.say('UUID required.', '#ff4444');
      this.api.get('/v1/people/emergency-contacts/' + u).then(r => {
        if (!r.ok) return this._out('out-' + T, r, 'Fetch');
        const d = r.data.data || r.data;
        $('s-fname').value = d.first_name || '';
        $('s-lname').value = d.last_name || '';
        $('s-phone').value = d.phone_number || '';
        $('s-email').value = d.email || '';
        $('s-rel').value = d.relationship_type || 'SPOUSE';
        this.say('Data loaded.');
      });
    };

    $(T + '-save').onclick = async () => {
      const m = this._mode;
      if (m === 'delete') {
        const u = _v(T + '-edit-uuid');
        if (!u) return this.say('UUID emergency contact required.', '#ff4444');
        if (!confirm('Delete emergency contact ' + u + '?')) return;
        const r = await this.api.del('/v1/people/emergency-contacts/' + u);
        this._out('out-' + T, r, 'Delete');
        return $('panel-close').click();
      }
      const dto = {
        first_name: _v('s-fname') || 'Contact', last_name: _v('s-lname') || 'Person',
        phone_number: _v('s-phone') || null, email: _v('s-email') || null,
        relationship_type: _v('s-rel') || 'SPOUSE',
      };
      if (!dto.phone_number && !dto.email) return this.say('Phone or email required.', '#ff4444');
      if (m === 'add') {
        const u = _v(T + '-fetch-uuid');
        if (!u) return this.say('Enter person UUID.', '#ff4444');
        const r = await this.api.post('/v1/people/' + u + '/emergency-contacts', dto);
        this._out('out-' + T, r, 'Create');
        $('panel-close').click();
      } else {
        const u = _v(T + '-edit-uuid');
        if (!u) return this.say('UUID emergency contact required.', '#ff4444');
        const r = await this.api.patch('/v1/people/emergency-contacts/' + u, dto);
        this._out('out-' + T, r, 'Update');
        $('panel-close').click();
      }
    };
  }

  _validation() {
    $('check-btn').onclick = () => {
      const e = _v('check-email');
      if (!e) return this.say('Enter email.', '#ff4444');
      let url = '/v1/people/check-exists?email=' + encodeURIComponent(e);
      const p = _v('check-pid');
      if (p) url += '&personal_id=' + encodeURIComponent(p);
      this.api.get(url).then(r => this._out('out-validation', r, 'Check'));
    };
  }
}

document.addEventListener('DOMContentLoaded', () => { new CoreUI(); });