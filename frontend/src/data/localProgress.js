const STORAGE_KEY = "data-literacy-game-state";

export function getDefaultUserId() {
  return import.meta.env.VITE_DEFAULT_USER_ID || "test_user_001";
}

export function readLocalState() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : {};
  } catch {
    return {};
  }
}

export function writeLocalState(state) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

export function mergeLocalState(patch) {
  const nextState = {
    ...readLocalState(),
    ...patch
  };

  writeLocalState(nextState);
  return nextState;
}

export function clearLocalState() {
  localStorage.removeItem(STORAGE_KEY);
}
