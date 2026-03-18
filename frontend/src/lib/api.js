const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:3000/api";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {})
    },
    ...options
  });

  const payload = await response.json().catch(() => null);

  if (!response.ok) {
    throw new Error(payload?.message || `Request failed with status ${response.status}`);
  }

  return payload;
}

export async function fetchLevels() {
  const payload = await request("/levels");
  return payload.data || [];
}

export async function fetchLevel(levelId) {
  const payload = await request(`/levels/${levelId}`);
  return payload.data;
}

export async function saveProgress(progress) {
  return request("/progress", {
    method: "POST",
    body: JSON.stringify(progress)
  });
}

export async function fetchProgress(userId) {
  const payload = await request(`/progress/${userId}`);
  return payload.data;
}

export async function submitResult(result) {
  return request("/results", {
    method: "POST",
    body: JSON.stringify(result)
  });
}

export async function fetchCertificate(userId) {
  const payload = await request(`/certificate/${userId}`);
  return payload.data;
}
