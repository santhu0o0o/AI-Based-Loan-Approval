// sessionStorage helpers that never throw (private mode, blocked storage, etc.).
export function load(key, fallback = null) {
  try {
    const raw = window.sessionStorage.getItem(key);
    return raw ? JSON.parse(raw) : fallback;
  } catch {
    return fallback;
  }
}

export function save(key, value) {
  try {
    window.sessionStorage.setItem(key, JSON.stringify(value));
  } catch {
    /* storage unavailable: the app still works, it just forgets on reload */
  }
}

export function remove(key) {
  try {
    window.sessionStorage.removeItem(key);
  } catch {
    /* ignore */
  }
}

export const KEYS = { answers: 'loanwise:answers', step: 'loanwise:step', result: 'loanwise:result' };
