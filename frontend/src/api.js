const API = import.meta.env.VITE_API_URL || "http://127.0.0.1:5000/api";

async function request(path, options = {}) {
  const token = localStorage.getItem("token")
  const authHeader = token ? { Authorization: `Bearer ${token}` } : {}
  const response = await fetch(`${API}${path}`, {
    headers: {"Content-Type": "application/json", ...(options.headers || {}), ...authHeader},
    ...options
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.error || "Request failed");
  return data;
}

export const analyzeMessage = (message) =>
  request("/ai/analyze", {method: "POST", body: JSON.stringify({message})});

export const createComplaint = (payload) =>
  request("/complaints", {method: "POST", body: JSON.stringify(payload)});

export const getComplaint = (id) => request(`/complaints/${encodeURIComponent(id)}`);

export const getComplaints = () => request("/complaints");

export const updateComplaint = (id, status) =>
  request(`/complaints/${encodeURIComponent(id)}`, {
    method: "PATCH",
    body: JSON.stringify({status})
  });

// Authentication
export const register = (payload) => request("/auth/register", {method: "POST", body: JSON.stringify(payload)});
export const login = (payload) => request("/auth/login", {method: "POST", body: JSON.stringify(payload)});
export const me = () => request("/auth/me");
export const myComplaints = () => request("/complaints/my");
