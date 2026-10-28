
const API_BASE = localStorage.getItem("SABOROSO_API_BASE") || "http://localhost:8000/api";

const state = {
  orders: [],
  products: [],
  customers: [],
  settings: {},
  users: [],
  selectedOrderId: null
};

const titles = {
  dashboard: ["Dashboard", "Visão geral da loja"],
  orders: ["Pedidos", "Gerencie os pedidos realizados pelos clientes"],
  products: ["Produtos", "Gerencie catálogo, imagens, tamanhos e preços"],
  customers: ["Clientes", "Histórico e informações dos clientes"],
  reports: ["Relatórios", "Indicadores de vendas e operação"],
  settings: ["Configurações", "Dados e regras da loja"],
  users: ["Usuários", "Controle de acesso ao painel"]
};

const $ = (id) => document.getElementById(id);

function money(value) {
  return Number(value || 0).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

function esc(value) {
  return String(value ?? "").replace(/[&<>"']/g, c => ({
    "&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#039;"
  }[c]));
}

function statusLabel(status) {
  const labels = {
    pendente:"Pendente", confirmado:"Confirmado", preparando:"Preparando",
    pronto:"Pronto", saiu_entrega:"Saiu para entrega", entregue:"Entregue", cancelado:"Cancelado"
  };
  return labels[status] || status || "Sem status";
}

function statusBadge(status) {
  return `<span class="status status-${esc(status)}">${esc(statusLabel(status))}</span>`;
}

function toast(message) {
  const el = $("toast");
  el.textContent = message;
  el.classList.add("show");
  setTimeout(() => el.classList.remove("show"), 2500);
}

function getToken() {
  return localStorage.getItem("access_token") || localStorage.getItem("token") || "";
}

async function api(path, options = {}) {
  const headers = { ...(options.headers || {}) };
  if (!(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;

  const response = await fetch(`${API_BASE}${path}`, { ...options, headers });

  if (response.status === 401) {
    localStorage.removeItem("access_token");
    localStorage.removeItem("token");
    toast("Sessão expirada. Faça login novamente.");
    throw new Error("Não autenticado");
  }

  if (!response.ok) {
    let message = `Erro HTTP ${response.status}`;
    try {
      const body = await response.json();
      if (typeof body.detail === "string") message = body.detail;
      else if (body.message) message = body.message;
      else if (typeof body === "object") {
        message = Object.entries(body)
          .map(([field, errors]) => `${field}: ${Array.isArray(errors) ? errors.join("; ") : String(errors)}`)
          .join(" | ");
      }
    } catch {}
    throw new Error(message);
  }

  if (response.status === 204) return null;
  return response.json();
}

/*
  Adaptador de endpoints.
  O painel já está separado da API para o backend Django.
  Se os paths finais do Django forem diferentes, altere somente este objeto.
*/
const endpoints = {
  orders: "/orders/orders/",
  products: "/products/products/",
  settings: "/store/store/",
  settingsCurrent: "/store/store/current/",
  users: "/users/",
  customers: "/users/customers/"
};

async function loadOrders() {
  try {
    const data = await api(endpoints.orders);
    state.orders = Array.isArray(data) ? data : (data.results || []);
  } catch (e) {
    console.warn("Pedidos:", e.message);
    state.orders = [];
  }
  renderOrders();
  renderDashboard();
  renderReports();
}

async function loadProducts() {
  try {
    const data = await api(endpoints.products);
    state.products = Array.isArray(data) ? data : (data.results || []);
  } catch (e) {
    console.warn("Produtos:", e.message);
    state.products = [];
  }
  renderProducts();
  renderDashboard();
  renderReports();
}

async function loadSettings() {
  try {
    state.settings = await api(endpoints.settings);
  } catch (e) {
    console.warn("Configurações:", e.message);
    state.settings = {};
  }
  fillSettings();
}

async function loadUsers() {
  try {
    const data = await api(endpoints.users);
    state.users = Array.isArray(data) ? data : (data.results || []);
  } catch (e) {
    console.warn("Usuários:", e.message);
    state.users = [];
  }
  renderUsers();
}

function normalizeOrder(order) {
  return {
    id: order.id,
    name: order.name ?? order.customer_name ?? "",
    email: order.email ?? order.customer_email ?? "",
    whatsapp: order.whatsapp ?? order.customer_whatsapp ?? "",
    delivery_date: order.delivery_date,
    delivery_method: order.delivery_method,
    address: order.address,
    address_rua: order.address_rua,
    address_bairro: order.address_bairro,
    address_numero: order.address_numero,
    address_complemento: order.address_complemento,
    address_referencia: order.address_referencia,
    total: Number(order.total || 0),
    status: order.status || "pendente",
    created_at: order.created_at,
    items: order.items || order.order_items || []
  };
}

function renderDashboard() {
  const orders = state.orders.map(normalizeOrder);
  const active = orders.filter(o => o.status !== "cancelado");
  const revenue = active.reduce((s, o) => s + o.total, 0);

  $("statOrders").textContent = orders.length;
  $("statRevenue").textContent = money(revenue);
  $("statPending").textContent = orders.filter(o => o.status === "pendente").length;
  $("statDelivered").textContent = orders.filter(o => o.status === "entregue").length;
  $("avgTicket").textContent = money(active.length ? revenue / active.length : 0);
  $("activeCustomers").textContent = new Set(orders.map(o => o.whatsapp || o.email).filter(Boolean)).size;
  $("activeProducts").textContent = state.products.length;

  const recent = orders.slice().sort((a,b) => new Date(b.created_at || 0) - new Date(a.created_at || 0)).slice(0,8);
  $("recentOrdersBody").innerHTML = recent.length ? recent.map(o => `
    <tr>
      <td>#${esc(o.id)}</td>
      <td>${esc(o.name)}</td>
      <td>${o.created_at ? new Date(o.created_at).toLocaleDateString("pt-BR") : "-"}</td>
      <td>${statusBadge(o.status)}</td>
      <td>${money(o.total)}</td>
      <td><button class="secondary-btn" onclick="openOrder('${esc(o.id)}')">Ver</button></td>
    </tr>`).join("") : `<tr><td colspan="6" class="empty">Nenhum pedido encontrado.</td></tr>`;

  const statuses = ["pendente","confirmado","preparando","pronto","entregue","cancelado"];
  $("statusSummary").innerHTML = statuses.map(s => `
    <div class="status-row">
      <div class="status-left"><span class="status-dot" style="background:${statusColor(s)}"></span>${statusLabel(s)}</div>
      <strong>${orders.filter(o => o.status === s).length}</strong>
    </div>`).join("");

  const delivery = orders.filter(o => o.delivery_method === "entrega").length;
  const pickup = orders.filter(o => o.delivery_method === "retirada").length;
  $("deliverySummary").innerHTML = `
    <div><span>Entrega</span><strong>${delivery}</strong></div>
    <div><span>Retirada</span><strong>${pickup}</strong></div>`;
}

function statusColor(s) {
  return {pendente:"#d99a00",confirmado:"#3977d2",preparando:"#c97900",pronto:"#6653b7",entregue:"#1f9d68",cancelado:"#d64b4b"}[s] || "#999";
}

function renderOrders() {
  const search = ($("orderSearch")?.value || "").toLowerCase();
  const status = $("orderStatusFilter")?.value || "";
  const method = $("orderMethodFilter")?.value || "";
  const date = $("orderDateFilter")?.value || "";

  const orders = state.orders.map(normalizeOrder).filter(o => {
    const hay = `${o.id} ${o.name} ${o.email} ${o.whatsapp}`.toLowerCase();
    const createdDate = o.created_at ? new Date(o.created_at).toISOString().slice(0,10) : "";
    return (!search || hay.includes(search))
      && (!status || o.status === status)
      && (!method || o.delivery_method === method)
      && (!date || createdDate === date);
  });

  $("ordersBody").innerHTML = orders.length ? orders.map(o => `
    <tr>
      <td>#${esc(o.id)}</td>
      <td><strong>${esc(o.name)}</strong><br><small>${esc(o.whatsapp)}</small></td>
      <td>${o.created_at ? new Date(o.created_at).toLocaleString("pt-BR") : "-"}</td>
      <td>${o.delivery_method === "entrega" ? "Entrega" : "Retirada"}</td>
      <td>${statusBadge(o.status)}</td>
      <td>${money(o.total)}</td>
      <td><button class="secondary-btn" onclick="openOrder('${esc(o.id)}')">Detalhes</button></td>
    </tr>`).join("") : `<tr><td colspan="7" class="empty">Nenhum pedido encontrado.</td></tr>`;
}

function renderProducts() {
  const search = ($("productSearch")?.value || "").toLowerCase();
  const products = state.products.filter(p => `${p.name} ${p.description || ""}`.toLowerCase().includes(search));

  $("productGrid").innerHTML = products.length ? products.map(p => `
    <article class="product-card">
      <img src="${esc(p.image || "assets/logo.png")}" alt="${esc(p.name)}" onerror="this.src='assets/logo.png'">
      <div class="product-card-body">
        <h3>${esc(p.name)}</h3>
        <p>${esc(p.description || "")}</p>
        <div class="size-tags">
          ${(p.sizes || []).map(s => `<span class="size-tag">${esc(s.label)}: ${money(s.price)}</span>`).join("")}
        </div>
        <div class="product-actions">
          <button class="secondary-btn" onclick="editProduct('${esc(p.id)}')">Editar</button>
          <button class="secondary-btn" onclick="deleteProduct('${esc(p.id)}')">Excluir</button>
        </div>
      </div>
    </article>`).join("") : `<div class="panel" style="padding:20px">Nenhum produto encontrado.</div>`;
}

function buildCustomers() {
  const map = new Map();
  state.orders.map(normalizeOrder).forEach(o => {
    const key = o.email || o.whatsapp || o.name;
    if (!key) return;
    if (!map.has(key)) map.set(key, { name:o.name, email:o.email, whatsapp:o.whatsapp, orders:0, total:0, items:[] });
    const c = map.get(key);
    c.orders++;
    c.total += o.status === "cancelado" ? 0 : o.total;
    c.items.push(o);
  });
  return [...map.values()];
}

function renderCustomers() {
  const search = ($("customerSearch")?.value || "").toLowerCase();
  const customers = buildCustomers().filter(c => `${c.name} ${c.email} ${c.whatsapp}`.toLowerCase().includes(search));
  state.customers = customers;

  $("customersBody").innerHTML = customers.length ? customers.map((c, i) => `
    <tr>
      <td><strong>${esc(c.name)}</strong></td>
      <td>${esc(c.email)}</td>
      <td>${esc(c.whatsapp)}</td>
      <td>${c.orders}</td>
      <td>${money(c.total)}</td>
      <td><button class="secondary-btn" onclick="openCustomer(${i})">Ver</button></td>
    </tr>`).join("") : `<tr><td colspan="6" class="empty">Nenhum cliente encontrado.</td></tr>`;
}

function renderReports() {
  const orders = state.orders.map(normalizeOrder);
  const active = orders.filter(o => o.status !== "cancelado");
  const revenue = active.reduce((s,o)=>s+o.total,0);

  $("reportRevenue").textContent = money(revenue);
  $("reportTicket").textContent = money(active.length ? revenue / active.length : 0);
  $("reportOrders").textContent = orders.length;
  $("reportCancelled").textContent = orders.filter(o=>o.status==="cancelado").length;

  const statuses = ["pendente","confirmado","preparando","pronto","entregue","cancelado"];
  const maxStatus = Math.max(1, ...statuses.map(s=>orders.filter(o=>o.status===s).length));
  $("reportStatusBars").innerHTML = statuses.map(s=>{
    const n = orders.filter(o=>o.status===s).length;
    return `<div class="bar-row"><div class="bar-label"><span>${statusLabel(s)}</span><strong>${n}</strong></div><div class="bar-track"><div class="bar-fill" style="width:${n/maxStatus*100}%"></div></div></div>`;
  }).join("");

  const methods = ["entrega","retirada"];
  const maxMethod = Math.max(1, ...methods.map(m=>orders.filter(o=>o.delivery_method===m).length));
  $("reportMethodBars").innerHTML = methods.map(m=>{
    const n = orders.filter(o=>o.delivery_method===m).length;
    return `<div class="bar-row"><div class="bar-label"><span>${m==="entrega"?"Entrega":"Retirada"}</span><strong>${n}</strong></div><div class="bar-track"><div class="bar-fill" style="width:${n/maxMethod*100}%"></div></div></div>`;
  }).join("");

  const products = new Map();
  orders.forEach(o => (o.items || []).forEach(item => {
    const name = item.product_name || item.products?.name || item.product?.name || "Produto";
    const q = Number(item.quantity || 0);
    const price = Number(item.price || 0);
    if (!products.has(name)) products.set(name,{name,quantity:0,revenue:0});
    const p = products.get(name);
    p.quantity += q;
    p.revenue += q * price;
  }));
  $("topProductsBody").innerHTML = [...products.values()].sort((a,b)=>b.quantity-a.quantity).slice(0,10).map(p=>`
    <tr><td>${esc(p.name)}</td><td>${p.quantity}</td><td>${money(p.revenue)}</td></tr>`).join("") || `<tr><td colspan="3">Sem dados.</td></tr>`;
}

function fillSettings() {
  const s = state.settings || {};
  $("setStoreName").value = s.loja_nome ?? s.store_name ?? s.name ?? "";
  $("setEmail").value = s.email ?? "";
  $("setPhone").value = s.telefone ?? s.phone ?? "";
  $("setAddress").value = s.endereco ?? s.address ?? "";
  $("setDeliveryFee").value = s.taxa_entrega ?? s.delivery_fee ?? 0;
  $("setDeliveryTime").value = s.tempo_entrega ?? s.delivery_time ?? "";
  $("setMinimumOrder").value = s.pedido_minimo ?? s.minimum_order ?? 0;
  $("setStoreOpen").checked = s.loja_aberta ?? s.store_open ?? true;
  $("storeStatusText").textContent = $("setStoreOpen").checked ? "Loja aberta" : "Loja fechada";
}

function renderUsers() {
  $("usersBody").innerHTML = state.users.length ? state.users.map(u=>`
    <tr>
      <td>${esc(u.nome_completo || u.name || u.username || "-")}</td>
      <td>${esc(u.email || "-")}</td>
      <td>${esc(u.tipo_usuario || u.role || "admin")}</td>
      <td>${u.is_active === false ? '<span class="status status-cancelado">Inativo</span>' : '<span class="status status-entregue">Ativo</span>'}</td>
      <td><button class="secondary-btn" onclick="toggleUser('${esc(u.id)}',${u.is_active === false})">${u.is_active === false ? "Ativar" : "Desativar"}</button></td>
    </tr>`).join("") : `<tr><td colspan="5">Nenhum usuário carregado.</td></tr>`;
}

function showPage(page) {
  document.querySelectorAll(".page").forEach(p=>p.classList.remove("active"));
  document.querySelector(`#page-${page}`).classList.add("active");
  document.querySelectorAll(".nav-item").forEach(b=>b.classList.toggle("active", b.dataset.page===page));
  $("pageTitle").textContent = titles[page][0];
  $("pageSubtitle").textContent = titles[page][1];
  $("sidebar").classList.remove("open");
  if (page === "customers") renderCustomers();
  if (page === "orders") renderOrders();
  if (page === "products") renderProducts();
  if (page === "reports") renderReports();
}

async function openOrder(id) {
  const order = state.orders.map(normalizeOrder).find(o=>String(o.id)===String(id));
  if (!order) return;

  state.selectedOrderId = id;
  $("orderModalTitle").textContent = `Pedido #${order.id}`;
  $("modalOrderStatus").value = order.status;

  $("orderDetails").innerHTML = `
    <div class="detail-grid">
      <div class="detail-box"><small>CLIENTE</small><strong>${esc(order.name)}</strong></div>
      <div class="detail-box"><small>WHATSAPP</small><strong>${esc(order.whatsapp)}</strong></div>
      <div class="detail-box"><small>E-MAIL</small><strong>${esc(order.email)}</strong></div>
      <div class="detail-box"><small>DATA DO PEDIDO</small><strong>${order.created_at ? new Date(order.created_at).toLocaleString("pt-BR") : "-"}</strong></div>
      <div class="detail-box"><small>DATA DE ENTREGA</small><strong>${esc(order.delivery_date || "-")}</strong></div>
      <div class="detail-box"><small>MÉTODO</small><strong>${order.delivery_method==="entrega"?"Entrega":"Retirada"}</strong></div>
      <div class="detail-box"><small>ENDEREÇO</small><strong>${esc([order.address_rua,order.address_numero,order.address_bairro,order.address_complemento].filter(Boolean).join(", ") || order.address || "-")}</strong></div>
      <div class="detail-box"><small>TOTAL</small><strong>${money(order.total)}</strong></div>
    </div>
    <div class="order-items">
      <strong style="font-size:11px">ITENS DO PEDIDO</strong>
      ${(order.items || []).map(i=>`<div class="order-item"><span>${esc(i.product_name || i.products?.name || i.product?.name || "Produto")} • ${esc(i.size || "")} x${Number(i.quantity||0)}</span><strong>${money(Number(i.price||0)*Number(i.quantity||0))}</strong></div>`).join("") || "<p class='help'>Itens não retornados pela API.</p>"}
    </div>`;
  $("orderModal").classList.add("show");
}

async function saveOrderStatus() {
  const id = state.selectedOrderId;
  const status = $("modalOrderStatus").value;
  if (!id) return;

  try {
    await api(`${endpoints.orders}${id}/`, {method:"PATCH", body:JSON.stringify({status})});
    const order = state.orders.find(o=>String(o.id)===String(id));
    if (order) order.status = status;
    renderOrders(); renderDashboard(); renderReports();
    $("orderModal").classList.remove("show");
    toast("Status atualizado.");
  } catch(e) {
    toast(`Não foi possível atualizar: ${e.message}`);
  }
}

function openProductModal(product=null) {
  $("productModalTitle").textContent = product ? "Editar produto" : "Novo produto";
  $("productId").value = product?.id || "";
  $("productName").value = product?.name || "";
  $("productDescription").value = product?.description || "";
  $("productImage").value = "";
  const sizes = product?.sizes?.length ? product.sizes : [{label:"",price:""}];
  $("sizesContainer").innerHTML = "";
  sizes.forEach(addSizeRow);
  $("productModal").classList.add("show");
}

function addSizeRow(size={label:"",price:""}) {
  const row = document.createElement("div");
  row.className = "size-row";
  row.innerHTML = `<input placeholder="Tamanho" value="${esc(size.label)}"><input type="number" step="0.01" min="0" placeholder="Preço" value="${esc(size.price)}"><button type="button">×</button>`;
  row.querySelector("button").onclick = () => row.remove();
  $("sizesContainer").appendChild(row);
}

function editProduct(id) {
  const p = state.products.find(x=>String(x.id)===String(id));
  if (p) openProductModal(p);
}

async function saveProduct(event) {
  event.preventDefault();
  const id = $("productId").value;
  const sizes = [...document.querySelectorAll("#sizesContainer .size-row")].map(row=>{
    const inputs = row.querySelectorAll("input");
    return {label:inputs[0].value.trim(),price:Number(inputs[1].value||0)};
  }).filter(s=>s.label && s.price > 0);

  const name = $("productName").value.trim();
  if (!name) {
    toast("Informe o nome do produto.");
    return;
  }
  if (!sizes.length) {
    toast("Adicione pelo menos um tamanho e preço válidos.");
    return;
  }

  const payload = new FormData();
  payload.append("name", name);
  payload.append("description", $("productDescription").value.trim());
  payload.append("is_active", "true");
  payload.append("sizes", JSON.stringify(sizes));
  const imageFile = $("productImage").files[0];
  if (imageFile) payload.append("image", imageFile);

  try {
    if (id) {
      await api(`${endpoints.products}${id}/`, {method:"PATCH",body:payload});
      toast("Produto atualizado.");
    } else {
      await api(endpoints.products,{method:"POST",body:payload});
      toast("Produto criado.");
    }
    $("productModal").classList.remove("show");
    await loadProducts();
  } catch(e) {
    toast(`Erro ao salvar produto: ${e.message}`);
  }
}

async function deleteProduct(id) {
  if (!confirm("Deseja realmente excluir este produto?")) return;
  try {
    await api(`${endpoints.products}${id}/`,{method:"DELETE"});
    state.products = state.products.filter(p=>String(p.id)!==String(id));
    renderProducts(); renderDashboard();
    toast("Produto excluído.");
  } catch(e) {
    toast(`Erro ao excluir: ${e.message}`);
  }
}

function openCustomer(index) {
  const c = state.customers[index];
  if (!c) return;
  $("customerModalTitle").textContent = c.name;
  $("customerDetails").innerHTML = `
    <div class="detail-grid">
      <div class="detail-box"><small>NOME</small><strong>${esc(c.name)}</strong></div>
      <div class="detail-box"><small>E-MAIL</small><strong>${esc(c.email)}</strong></div>
      <div class="detail-box"><small>WHATSAPP</small><strong>${esc(c.whatsapp)}</strong></div>
      <div class="detail-box"><small>PEDIDOS</small><strong>${c.orders}</strong></div>
      <div class="detail-box"><small>TOTAL GASTO</small><strong>${money(c.total)}</strong></div>
    </div>
    <div class="order-items">
      <strong style="font-size:11px">HISTÓRICO</strong>
      ${c.items.map(o=>`<div class="order-item"><span>#${esc(o.id)} • ${o.created_at ? new Date(o.created_at).toLocaleDateString("pt-BR") : "-"}</span><strong>${money(o.total)}</strong></div>`).join("")}
    </div>`;
  $("customerModal").classList.add("show");
}

async function saveSettings() {
  const payload = {
    name:$("setStoreName").value,
    phone:$("setPhone").value,
    address:$("setAddress").value,
    taxa_entrega:Number($("setDeliveryFee").value||0),
    pedido_minimo:Number($("setMinimumOrder").value||0),
    loja_aberta:$("setStoreOpen").checked
  };

  try {
    await api(endpoints.settingsCurrent, {method:"PATCH",body:JSON.stringify(payload)});
    state.settings = {...state.settings,...payload};
    fillSettings();
    toast("Configurações salvas.");
  } catch(e) {
    toast(`Erro ao salvar: ${e.message}`);
  }
}

async function toggleUser(id, activate) {
  try {
    await api(`${endpoints.users}${id}/`,{method:"PATCH",body:JSON.stringify({is_active:activate})});
    await loadUsers();
    toast("Usuário atualizado.");
  } catch(e) {
    toast(`Erro: ${e.message}`);
  }
}

async function createUser(event) {
  event.preventDefault();
  const payload = {
    nome_completo:$("userName").value,
    email:$("userEmail").value,
    password:$("userPassword").value,
    tipo_usuario:$("userRole").value
  };
  try {
    await api(endpoints.users,{method:"POST",body:JSON.stringify(payload)});
    $("userModal").classList.remove("show");
    $("userForm").reset();
    await loadUsers();
    toast("Usuário criado.");
  } catch(e) {
    toast(`Erro ao criar usuário: ${e.message}`);
  }
}

function exportCsv() {
  const orders = state.orders.map(normalizeOrder);
  const rows = [
    ["ID","Cliente","Email","WhatsApp","Data","Método","Status","Total"],
    ...orders.map(o=>[o.id,o.name,o.email,o.whatsapp,o.created_at,o.delivery_method,o.status,o.total])
  ];
  const csv = rows.map(r=>r.map(v=>`"${String(v??"").replaceAll('"','""')}"`).join(",")).join("\n");
  const blob = new Blob(["\ufeff"+csv],{type:"text/csv;charset=utf-8"});
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href=url; a.download="pedidos-saboroso-pudim.csv"; a.click();
  URL.revokeObjectURL(url);
}

async function refreshAll() {
  await Promise.all([loadOrders(),loadProducts(),loadSettings(),loadUsers()]);
  renderCustomers();
  renderReports();
}

document.querySelectorAll(".nav-item").forEach(btn=>btn.addEventListener("click",()=>showPage(btn.dataset.page)));
document.querySelectorAll("[data-page-link]").forEach(btn=>btn.addEventListener("click",()=>showPage(btn.dataset.pageLink)));
$("mobileMenu").addEventListener("click",()=>$("sidebar").classList.toggle("open"));
$("refreshBtn").addEventListener("click",refreshAll);
$("saveOrderStatusBtn").addEventListener("click",saveOrderStatus);
$("newProductBtn").addEventListener("click",()=>openProductModal());
$("productForm").addEventListener("submit",saveProduct);
$("addSizeBtn").addEventListener("click",()=>addSizeRow());
$("saveSettingsBtn").addEventListener("click",saveSettings);
$("newUserBtn").addEventListener("click",()=>$("userModal").classList.add("show"));
$("userForm").addEventListener("submit",createUser);
$("exportCsvBtn").addEventListener("click",exportCsv);
$("orderSearch").addEventListener("input",renderOrders);
$("orderStatusFilter").addEventListener("change",renderOrders);
$("orderMethodFilter").addEventListener("change",renderOrders);
$("orderDateFilter").addEventListener("change",renderOrders);
$("productSearch").addEventListener("input",renderProducts);
$("customerSearch").addEventListener("input",renderCustomers);
$("setStoreOpen").addEventListener("change",()=>{$("storeStatusText").textContent=$("setStoreOpen").checked?"Loja aberta":"Loja fechada"});
document.querySelectorAll("[data-close]").forEach(btn=>btn.addEventListener("click",()=>$(btn.dataset.close).classList.remove("show")));
document.querySelectorAll(".modal").forEach(modal=>modal.addEventListener("click",e=>{if(e.target===modal)modal.classList.remove("show")}));
$("logoutBtn").addEventListener("click",()=>{localStorage.removeItem("access_token");localStorage.removeItem("token");localStorage.removeItem("refresh_token");location.href="/"});

refreshAll().catch(console.error);
