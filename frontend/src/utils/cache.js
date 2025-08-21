const DEFAULT_TTL_MS = 60 * 60 * 1000; // 1 hour
const SCHEDULE_DETAIL_TTL_MS = 24 * 60 * 60 * 1000; // 24 hours

export function getCacheKey(key, userId) {
  return `cs_${userId || 'anon'}_${key}`;
}

export function setCached(key, userId, data, ttlMs = DEFAULT_TTL_MS) {
  const expires = Date.now() + ttlMs;
  try {
    localStorage.setItem(getCacheKey(key, userId), JSON.stringify({ data, expires }));
  } catch {}
}

export function getCached(key, userId) {
  try {
    const raw = localStorage.getItem(getCacheKey(key, userId));
    if (!raw) return null;
    const parsed = JSON.parse(raw);
    if (!parsed.expires || parsed.expires < Date.now()) {
      localStorage.removeItem(getCacheKey(key, userId));
      return null;
    }
    return parsed.data;
  } catch {
    return null;
  }
}

export function deleteCached(key, userId) {
  try { localStorage.removeItem(getCacheKey(key, userId)); } catch {}
}

export function setStaleCached(key, userId, data) {
  try {
    localStorage.setItem(
      getCacheKey(key, userId),
      JSON.stringify({ data, expires: Date.now() - 1 })
    );
  } catch {}
}

export function scheduleDetailKey(userId, scheduleId) {
  return `cs_${userId}_schedule_${scheduleId}`;
}

export function setScheduleDetail(userId, scheduleId, scheduleObj, ttlMs = SCHEDULE_DETAIL_TTL_MS) {
  if (!userId || !scheduleId) return;
  try {
    const payload = {
      data: scheduleObj,
      expires: Date.now() + ttlMs
    };
    localStorage.setItem(scheduleDetailKey(userId, scheduleId), JSON.stringify(payload));
  } catch {}
}

export function getScheduleDetail(userId, scheduleId) {
  if (!userId || !scheduleId) return null;
  try {
    const raw = localStorage.getItem(scheduleDetailKey(userId, scheduleId));
    if (!raw) return null;
    const parsed = JSON.parse(raw);
    if (!parsed.expires || parsed.expires < Date.now()) {
      localStorage.removeItem(scheduleDetailKey(userId, scheduleId));
      return null;
    }
    return parsed.data;
  } catch {
    return null;
  }
}

export function deleteScheduleDetail(userId, scheduleId) {
  try {
    localStorage.removeItem(scheduleDetailKey(userId, scheduleId));
  } catch {}
}