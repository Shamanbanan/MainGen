let token = "";
let treeId = null;

async function post(url, data) {
  const res = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { token } : {}),
    },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text);
  }
  return res.json();
}

document.getElementById("signup-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const email = document.getElementById("signup-email").value;
  const password = document.getElementById("signup-password").value;
  const data = await post("/auth/signup", { email, password });
  token = data.access_token;
  document.getElementById("token").textContent = token;
});

document.getElementById("signin-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const email = document.getElementById("signin-email").value;
  const password = document.getElementById("signin-password").value;
  const data = await post("/auth/signin", { email, password });
  token = data.access_token;
  document.getElementById("token").textContent = token;
});

document.getElementById("tree-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const name = document.getElementById("tree-name").value;
  const data = await post("/trees", { name });
  treeId = data.id;
  document.getElementById("tree-id").textContent = treeId;
  await listPeople();
});

document.getElementById("person-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  if (!treeId) {
    alert("Create a tree first");
    return;
  }
  const first_name = document.getElementById("person-first").value;
  const last_name = document.getElementById("person-last").value;
  await post(`/trees/${treeId}/persons`, { first_name, last_name, gender: "unknown" });
  await listPeople();
});

async function listPeople() {
  if (!treeId) return;
  const res = await fetch(`/trees/${treeId}/persons`, {
    headers: token ? { token } : {},
  });
  if (!res.ok) return;
  const data = await res.json();
  const list = document.getElementById("people-list");
  list.innerHTML = "";
  data.forEach((p) => {
    const li = document.createElement("li");
    li.textContent = `${p.id}: ${p.first_name} ${p.last_name}`;
    list.appendChild(li);
  });
}
