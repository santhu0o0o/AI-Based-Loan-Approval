// Thin fetch wrapper: timeouts, JSON parsing, and plain-English errors.
// Every failure becomes an ApiError with a `kind` the UI can react to.

export const NETWORK_MESSAGE = "We couldn't reach the server. Is it running?";

export class ApiError extends Error {
  constructor(kind, message, extra = {}) {
    super(message);
    this.name = 'ApiError';
    this.kind = kind; // 'network' | 'timeout' | 'validation' | 'server' | 'bad-response'
    this.status = extra.status ?? 0;
    this.errors = extra.errors ?? {}; // field -> message (422 only)
  }
}

async function request(path, { method = 'GET', body, timeout = 15000 } = {}) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeout);
  let res;
  try {
    res = await fetch(path, {
      method,
      headers: body ? { 'Content-Type': 'application/json', Accept: 'application/json' } : { Accept: 'application/json' },
      body: body ? JSON.stringify(body) : undefined,
      signal: controller.signal,
    });
  } catch (err) {
    if (err?.name === 'AbortError') {
      throw new ApiError('timeout', 'The server is taking too long to answer. Please try again in a moment.');
    }
    throw new ApiError('network', NETWORK_MESSAGE);
  } finally {
    clearTimeout(timer);
  }

  let data = null;
  try {
    data = await res.json();
  } catch {
    data = null;
  }

  if (res.status === 422) {
    throw new ApiError('validation', data?.message || 'Some answers need fixing. Look for the red boxes.', {
      status: 422,
      errors: data?.errors || {},
    });
  }
  if (!res.ok || !data || data.ok === false) {
    // A proxy with no backend behind it usually answers 502/503/504.
    if ([502, 503, 504].includes(res.status)) throw new ApiError('network', NETWORK_MESSAGE, { status: res.status });
    if (res.status === 404 && !data) throw new ApiError('network', NETWORK_MESSAGE, { status: 404 });
    throw new ApiError(
      data ? 'server' : 'bad-response',
      data?.message || 'Something went wrong on our side. Please try again.',
      { status: res.status },
    );
  }
  return data;
}

export const api = {
  predict: (answers) => request('/api/predict', { method: 'POST', body: answers, timeout: 20000 }),
  sample: () => request('/api/sample'),
  history: (limit = 50) => request(`/api/history?limit=${limit}`),
  clearHistory: () => request('/api/history', { method: 'DELETE' }),
  modelInfo: () => request('/api/model-info'),
  health: () => request('/api/health', { timeout: 5000 }),
};
