class APIClient {
  constructor(base = '') { this.base = base; }
  async req(method, p, body) {
    const opts = { method, headers: {} };
    if (body) { opts.headers['Content-Type'] = 'application/json'; opts.body = JSON.stringify(body); }
    const r = await fetch(`${this.base}${p}`, opts);
    const text = await r.text();
    try { return { ok: r.ok, status: r.status, data: JSON.parse(text) }; }
    catch { return { ok: r.ok, status: r.status, data: text }; }
  }
  get(p) { return this.req('GET', p); }
  post(p, b) { return this.req('POST', p, b); }
  patch(p, b) { return this.req('PATCH', p, b); }
}

class CoreUI {
  constructor() {
    this.msg = document.getElementById('msg');
    this.api = new APIClient();
    this._bindNav();
    this._bindPerson();
    this._bindContact();
    this._bindIdentity();
    this._bindSocial();
  }
  say(t, c = '#00ff88') { this.msg.textContent = t; this.msg.style.color = c; }

  _bindNav() {
    document.querySelectorAll('.topbar nav button').forEach(b => b.onclick = () => {
      document.querySelectorAll('.topbar nav button').forEach(x => x.classList.remove('active'));
      document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
      b.classList.add('active');
      document.getElementById('sec-' + b.dataset.section).classList.add('active');
    });
  }

  async _loadList(btnId, outId, path) {
    const btn = document.getElementById(btnId);
    const pre = document.getElementById(outId);
    const orig = btn.textContent;
    btn.textContent = '...'; pre.textContent = 'Loading...';
    const res = await this.api.get(path);
    if (res.ok) { const items = res.data.data || []; pre.textContent = JSON.stringify(items, null, 2); this.say(`${items.length} items.`); }
    else { pre.textContent = `ERROR ${res.status}:\n${JSON.stringify(res.data, null, 2)}`; this.say(`Error ${res.status}`, '#ff4444'); }
    btn.textContent = orig;
  }

  async _create(btnId, outId, path, dto, label) {
    const btn = document.getElementById(btnId);
    const pre = document.getElementById(outId);
    const orig = btn.textContent;
    btn.textContent = '...';
    const res = await this.api.post(path, dto);
    if (res.ok) { pre.textContent = JSON.stringify(res.data, null, 2); this.say(`${label} created.`); }
    else { pre.textContent = `ERROR ${res.status}:\n${JSON.stringify(res.data, null, 2)}`; this.say(`${label} failed`, '#ff4444'); }
    btn.textContent = orig;
  }

  _bindPerson() {
    document.getElementById('get-btn').onclick = () => {
      const uuid = document.getElementById('get-uuid').value;
      if (!uuid) return this.say('Enter UUID.', '#ff4444');
      this._loadList('get-btn', 'out-person', `/v1/people/persons/${uuid}`);
    };
    document.getElementById('create-btn').onclick = () => {
      const dto = {
        email: document.getElementById('c-email').value,
        phone_code: '+52', phone_number: '5500000000',
        first_name: document.getElementById('c-fname').value || 'Test',
        last_name: document.getElementById('c-lname').value || 'User',
        birth_date: '1990-01-01', key_birth_country: 'MX',
      };
      if (!dto.email) return this.say('Email required.', '#ff4444');
      this._create('create-btn', 'out-person', '/v1/people/persons', dto, 'Person');
    };
    document.getElementById('check-btn').onclick = () => {
      const email = document.getElementById('check-email').value;
      if (!email) return this.say('Enter email.', '#ff4444');
      this._loadList('check-btn', 'out-person', `/v1/people/persons/check-exists?email=${encodeURIComponent(email)}`);
    };
    document.getElementById('status-btn').onclick = async () => {
      const uuid = document.getElementById('stat-uuid').value;
      const status = document.getElementById('stat-val').value;
      if (!uuid) return this.say('Enter UUID.', '#ff4444');
      const btn = document.getElementById('status-btn'); const pre = document.getElementById('out-person');
      btn.textContent = '...';
      const res = await this.api.patch(`/v1/people/persons/${uuid}/status`, { verification_status: status });
      if (res.ok) { pre.textContent = JSON.stringify(res.data, null, 2); this.say('Status updated.'); }
      else { pre.textContent = `ERROR ${res.status}:\n${JSON.stringify(res.data, null, 2)}`; this.say('Error', '#ff4444'); }
      btn.textContent = 'UPDATE';
    };
  }

  _bindContact() {
    document.getElementById('em-list-btn').onclick = () => {
      const uuid = document.getElementById('em-list-uuid').value;
      if (!uuid) return this.say('Enter UUID.', '#ff4444');
      this._loadList('em-list-btn', 'out-emails', `/v1/people/persons/${uuid}/emails`);
    };
    document.getElementById('em-create-btn').onclick = () => {
      const uuid = document.getElementById('em-uuid').value;
      const email = document.getElementById('em-email').value;
      if (!uuid || !email) return this.say('UUID and email required.', '#ff4444');
      this._create('em-create-btn', 'out-emails', `/v1/people/persons/${uuid}/emails`, { email, type_email: 'PERSONAL' }, 'Email');
    };
    document.getElementById('ph-list-btn').onclick = () => {
      const uuid = document.getElementById('ph-list-uuid').value;
      if (!uuid) return this.say('Enter UUID.', '#ff4444');
      this._loadList('ph-list-btn', 'out-phones', `/v1/people/persons/${uuid}/phones`);
    };
    document.getElementById('ph-create-btn').onclick = () => {
      const uuid = document.getElementById('ph-uuid').value;
      const code = document.getElementById('ph-code').value || '+52';
      const num = document.getElementById('ph-num').value;
      if (!uuid || !num) return this.say('UUID and number required.', '#ff4444');
      this._create('ph-create-btn', 'out-phones', `/v1/people/persons/${uuid}/phones`, { code, number: num, type_phone: 'MOBILE' }, 'Phone');
    };
  }

  _bindIdentity() {
    document.getElementById('id-list-btn').onclick = () => {
      const uuid = document.getElementById('id-list-uuid').value;
      if (!uuid) return this.say('Enter UUID.', '#ff4444');
      this._loadList('id-list-btn', 'out-ids', `/v1/people/persons/${uuid}/identifiers`);
    };
    document.getElementById('id-create-btn').onclick = () => {
      const uuid = document.getElementById('id-uuid').value;
      const type = document.getElementById('id-type').value;
      const val = document.getElementById('id-val').value;
      if (!uuid || !val) return this.say('UUID and value required.', '#ff4444');
      this._create('id-create-btn', 'out-ids', `/v1/people/persons/${uuid}/identifiers`, { id_identifier_type: type, identifier_value: val }, 'Identifier');
    };
  }

  _bindSocial() {
    document.getElementById('ec-list-btn').onclick = () => {
      const uuid = document.getElementById('ec-list-uuid').value;
      if (!uuid) return this.say('Enter UUID.', '#ff4444');
      this._loadList('ec-list-btn', 'out-ec', `/v1/people/persons/${uuid}/emergency-contacts`);
    };
    document.getElementById('ec-create-btn').onclick = () => {
      const uuid = document.getElementById('ec-uuid').value;
      const fn = document.getElementById('ec-fname').value || 'Contact';
      const ln = document.getElementById('ec-lname').value || 'Person';
      const phone = document.getElementById('ec-phone').value || null;
      const email = document.getElementById('ec-email').value || null;
      const rel = document.getElementById('ec-rel').value;
      if (!uuid) return this.say('Enter UUID.', '#ff4444');
      this._create('ec-create-btn', 'out-ec', `/v1/people/persons/${uuid}/emergency-contacts`, {
        first_name: fn, last_name: ln, phone_number: phone, email: email, relationship_type: rel,
      }, 'Emergency Contact');
    };
  }
}

document.addEventListener('DOMContentLoaded', () => { new CoreUI(); });
