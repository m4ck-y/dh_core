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
  del(p) { return this.req('DELETE', p); }
}

class CoreUI {
  constructor() {
    this.msg = document.getElementById('msg');
    this.api = new APIClient();
    this._bindNav();
    this._bindPerson();
    this._bindAddress();
    this._bindContact();
    this._bindIdentity();
    this._bindSocial();
    this._bindValidation();
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
    if (res.ok) { const items = res.data.data || []; pre.textContent = JSON.stringify(items, null, 2); this.say(`${Array.isArray(items) ? items.length : 1} item(s).`); }
    else { pre.textContent = `ERROR ${res.status}:\n${JSON.stringify(res.data, null, 2)}`; this.say(`Error ${res.status}`, '#ff4444'); }
    btn.textContent = orig;
  }

  async _mutate(method, btnId, outId, path, dto, label) {
    const btn = document.getElementById(btnId);
    const pre = document.getElementById(outId);
    const orig = btn.textContent;
    btn.textContent = '...';
    const res = await this.api[method](path, dto);
    if (res.ok) { pre.textContent = res.status === 204 ? 'No content.' : JSON.stringify(res.data, null, 2); this.say(`${label} OK.`); }
    else { pre.textContent = `ERROR ${res.status}:\n${JSON.stringify(res.data, null, 2)}`; this.say(`${label} failed`, '#ff4444'); }
    btn.textContent = orig;
  }

  _bindPerson() {
    document.getElementById('list-btn').onclick = () => {
      this._loadList('list-btn', 'out-person', '/v1/people');
    };
    document.getElementById('get-btn').onclick = () => {
      const uuid = document.getElementById('get-uuid').value;
      if (!uuid) return this.say('Enter UUID.', '#ff4444');
      this._loadList('get-btn', 'out-person', `/v1/people/${uuid}`);
    };
    document.getElementById('create-btn').onclick = () => {
      const dto = {
        email: document.getElementById('c-email').value,
        phone_code: '+52', phone_number: '5500000000',
        first_name: document.getElementById('c-fname').value || 'Test',
        last_name: document.getElementById('c-lname').value || 'User',
        birth_date: '1990-01-01', key_birth_country: 'MX',
        personal_identifier: (() => {
          const val = document.getElementById('pi-value').value;
          return val ? { type: document.getElementById('pi-type').value, value: val } : null;
        })(),
      };
      if (!dto.email) return this.say('Email required.', '#ff4444');
      this._mutate('post', 'create-btn', 'out-person', '/v1/people', dto, 'Person');
    };
    document.getElementById('update-btn').onclick = () => {
      const uuid = document.getElementById('upd-uuid').value;
      if (!uuid) return this.say('Enter UUID.', '#ff4444');
      const dto = {};
      const fn = document.getElementById('upd-fname').value; if (fn) dto.first_name = fn;
      const ln = document.getElementById('upd-lname').value; if (ln) dto.last_name = ln;
      this._mutate('patch', 'update-btn', 'out-person', `/v1/people/${uuid}`, dto, 'Person');
    };
    document.getElementById('status-btn').onclick = () => {
      const uuid = document.getElementById('stat-uuid').value;
      const status = document.getElementById('stat-val').value;
      if (!uuid) return this.say('Enter UUID.', '#ff4444');
      this._mutate('patch', 'status-btn', 'out-person', `/v1/people/${uuid}/status`, { verification_status: status }, 'Status');
    };
    document.getElementById('delete-btn').onclick = () => {
      const uuid = document.getElementById('del-uuid').value;
      if (!uuid) return this.say('Enter UUID.', '#ff4444');
      this._mutate('del', 'delete-btn', 'out-person', `/v1/people/${uuid}`, null, 'Delete');
    };
  }

  _bindAddress() {
    document.getElementById('addr-list-btn').onclick = () => {
      const uuid = document.getElementById('addr-list-uuid').value;
      if (!uuid) return this.say('Enter UUID.', '#ff4444');
      this._loadList('addr-list-btn', 'out-address', `/v1/people/${uuid}/address`);
    };
    document.getElementById('addr-create-btn').onclick = () => {
      const uuid = document.getElementById('addr-uuid').value;
      if (!uuid) return this.say('Enter UUID.', '#ff4444');
      const dto = {
        address: document.getElementById('addr-street').value || 'Test Street 123',
        postal_code: document.getElementById('addr-zip').value || '06600',
        key_state: 'CMX', key_municipality: '016',
      };
      this._mutate('post', 'addr-create-btn', 'out-address', `/v1/people/${uuid}/address`, dto, 'Address');
    };
    document.getElementById('addr-update-btn').onclick = () => {
      const uuid = document.getElementById('addr-upd-uuid').value;
      if (!uuid) return this.say('Enter UUID.', '#ff4444');
      const dto = {};
      const addr = document.getElementById('addr-upd-street').value; if (addr) dto.address = addr;
      this._mutate('patch', 'addr-update-btn', 'out-address', `/v1/people/${uuid}/address`, dto, 'Address');
    };
    document.getElementById('addr-delete-btn').onclick = () => {
      const uuid = document.getElementById('addr-del-uuid').value;
      if (!uuid) return this.say('Enter UUID.', '#ff4444');
      this._mutate('del', 'addr-delete-btn', 'out-address', `/v1/people/${uuid}/address`, null, 'Address');
    };
  }

  _bindContact() {
    // Emails
    document.getElementById('em-list-btn').onclick = () => {
      const uuid = document.getElementById('em-list-uuid').value;
      if (!uuid) return this.say('Enter UUID.', '#ff4444');
      this._loadList('em-list-btn', 'out-emails', `/v1/people/${uuid}/emails`);
    };
    document.getElementById('em-create-btn').onclick = () => {
      const uuid = document.getElementById('em-uuid').value;
      const email = document.getElementById('em-email').value;
      if (!uuid || !email) return this.say('UUID and email required.', '#ff4444');
      this._mutate('post', 'em-create-btn', 'out-emails', `/v1/people/${uuid}/emails`, { email, type_email: 'PERSONAL' }, 'Email');
    };
    document.getElementById('em-update-btn').onclick = () => {
      const uuid = document.getElementById('em-upd-uuid').value;
      if (!uuid) return this.say('Enter UUID.', '#ff4444');
      this._mutate('patch', 'em-update-btn', 'out-emails', `/v1/people/${uuid}/emails`, { type_email: 'WORK' }, 'Email');
    };
    document.getElementById('em-delete-btn').onclick = () => {
      const uuid = document.getElementById('em-del-uuid').value;
      if (!uuid) return this.say('Enter UUID.', '#ff4444');
      this._mutate('del', 'em-delete-btn', 'out-emails', `/v1/people/${uuid}/emails`, null, 'Email');
    };
    // Phones
    document.getElementById('ph-list-btn').onclick = () => {
      const uuid = document.getElementById('ph-list-uuid').value;
      if (!uuid) return this.say('Enter UUID.', '#ff4444');
      this._loadList('ph-list-btn', 'out-phones', `/v1/people/${uuid}/phones`);
    };
    document.getElementById('ph-create-btn').onclick = () => {
      const uuid = document.getElementById('ph-uuid').value;
      const code = document.getElementById('ph-code').value || '+52';
      const num = document.getElementById('ph-num').value;
      if (!uuid || !num) return this.say('UUID and number required.', '#ff4444');
      this._mutate('post', 'ph-create-btn', 'out-phones', `/v1/people/${uuid}/phones`, { code, number: num, type_phone: 'MOBILE' }, 'Phone');
    };
    document.getElementById('ph-update-btn').onclick = () => {
      const uuid = document.getElementById('ph-upd-uuid').value;
      if (!uuid) return this.say('Enter UUID.', '#ff4444');
      const dto = {};
      const num = document.getElementById('ph-upd-num').value; if (num) dto.number = num;
      this._mutate('patch', 'ph-update-btn', 'out-phones', `/v1/people/${uuid}/phones`, dto, 'Phone');
    };
    document.getElementById('ph-delete-btn').onclick = () => {
      const uuid = document.getElementById('ph-del-uuid').value;
      if (!uuid) return this.say('Enter UUID.', '#ff4444');
      this._mutate('del', 'ph-delete-btn', 'out-phones', `/v1/people/${uuid}/phones`, null, 'Phone');
    };
  }

  _bindIdentity() {
    document.getElementById('id-list-btn').onclick = () => {
      const uuid = document.getElementById('id-list-uuid').value;
      if (!uuid) return this.say('Enter UUID.', '#ff4444');
      this._loadList('id-list-btn', 'out-ids', `/v1/people/${uuid}/identifiers`);
    };
    document.getElementById('id-create-btn').onclick = () => {
      const uuid = document.getElementById('id-uuid').value;
      const type = document.getElementById('id-type').value;
      const val = document.getElementById('id-val').value;
      if (!uuid || !val) return this.say('UUID and value required.', '#ff4444');
      this._mutate('post', 'id-create-btn', 'out-ids', `/v1/people/${uuid}/identifiers`, { id_identifier_type: type, identifier_value: val }, 'Identifier');
    };
    document.getElementById('id-update-btn').onclick = () => {
      const uuid = document.getElementById('id-upd-uuid').value;
      if (!uuid) return this.say('Enter UUID.', '#ff4444');
      const dto = {};
      const val = document.getElementById('id-upd-val').value; if (val) dto.identifier_value = val;
      this._mutate('patch', 'id-update-btn', 'out-ids', `/v1/people/${uuid}/identifiers`, dto, 'Identifier');
    };
    document.getElementById('id-delete-btn').onclick = () => {
      const uuid = document.getElementById('id-del-uuid').value;
      if (!uuid) return this.say('Enter UUID.', '#ff4444');
      this._mutate('del', 'id-delete-btn', 'out-ids', `/v1/people/${uuid}/identifiers`, null, 'Identifier');
    };
  }

  _bindSocial() {
    document.getElementById('ec-list-btn').onclick = () => {
      const uuid = document.getElementById('ec-list-uuid').value;
      if (!uuid) return this.say('Enter UUID.', '#ff4444');
      this._loadList('ec-list-btn', 'out-ec', `/v1/people/${uuid}/emergency-contacts`);
    };
    document.getElementById('ec-create-btn').onclick = () => {
      const uuid = document.getElementById('ec-uuid').value;
      const fn = document.getElementById('ec-fname').value || 'Contact';
      const ln = document.getElementById('ec-lname').value || 'Person';
      const phone = document.getElementById('ec-phone').value || null;
      const email = document.getElementById('ec-email').value || null;
      const rel = document.getElementById('ec-rel').value;
      if (!uuid) return this.say('Enter UUID.', '#ff4444');
      this._mutate('post', 'ec-create-btn', 'out-ec', `/v1/people/${uuid}/emergency-contacts`, {
        first_name: fn, last_name: ln, phone_number: phone, email: email, relationship_type: rel,
      }, 'Emergency Contact');
    };
    document.getElementById('ec-update-btn').onclick = () => {
      const uuid = document.getElementById('ec-upd-uuid').value;
      if (!uuid) return this.say('Enter UUID.', '#ff4444');
      const dto = {};
      const fn = document.getElementById('ec-upd-fname').value; if (fn) dto.first_name = fn;
      const phone = document.getElementById('ec-upd-phone').value; if (phone) dto.phone_number = phone;
      this._mutate('patch', 'ec-update-btn', 'out-ec', `/v1/people/${uuid}/emergency-contacts`, dto, 'EC');
    };
    document.getElementById('ec-delete-btn').onclick = () => {
      const uuid = document.getElementById('ec-del-uuid').value;
      if (!uuid) return this.say('Enter UUID.', '#ff4444');
      this._mutate('del', 'ec-delete-btn', 'out-ec', `/v1/people/${uuid}/emergency-contacts`, null, 'EC');
    };
  }

  _bindValidation() {
    document.getElementById('check-btn').onclick = () => {
      const email = document.getElementById('check-email').value;
      if (!email) return this.say('Enter email.', '#ff4444');
      let url = `/v1/people/check-exists?email=${encodeURIComponent(email)}`;
      const pid = document.getElementById('check-pid').value;
      if (pid) url += `&personal_id=${encodeURIComponent(pid)}`;
      this._loadList('check-btn', 'out-validation', url);
    };
  }
}

document.addEventListener('DOMContentLoaded', () => { new CoreUI(); });
