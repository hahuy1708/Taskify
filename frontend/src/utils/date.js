// src/utils/date.js

/**
 * Format a date-like input to a locale date string.
 * @param {string|number|Date|null|undefined} d
 * @param {{ locale?: string, fallback?: string }} [opts]
 * @returns {string}
 */
export function formatDate(d, opts = {}) {
  const { locale, fallback = '-' } = opts;
  if (!d) return fallback;
  try {
    const dt = new Date(d);
    if (Number.isNaN(dt.getTime())) return fallback;
    return dt.toLocaleDateString(locale);
  } catch (_) {
    return fallback;
  }
}

/**
 * Humanize days until a deadline.
 * @param {string|number|Date|null|undefined} d
 * @param {Date} [now]
 * @returns {string}
 */
export function dueInDays(d, now = new Date()) {
  if (!d) return '';
  try {
    const dt = new Date(d);
    if (Number.isNaN(dt.getTime())) return '';
    const diffDays = Math.ceil((dt - now) / (1000 * 60 * 60 * 24));
    if (diffDays < 0) return `${Math.abs(diffDays)}d overdue`;
    return `in ${diffDays}d`;
  } catch (_) {
    return '';
  }
}
