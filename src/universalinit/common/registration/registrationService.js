'use strict';

/**
 * Async/await refactor of a callback-heavy Node.js registration flow.
 *
 * Notes:
 * - This module intentionally avoids hard-coded secrets; configure via environment variables.
 * - Uses mysql's callback API but wraps it into Promises for async/await usage.
 *
 * Environment variables expected:
 * - MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE
 * - SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, SMTP_FROM
 * - REGISTRATION_TEMPLATE_PATH (optional) - defaults to "<this_dir>/templates/welcome.html"
 * - REGISTRATION_LOG_PATH (optional) - defaults to "<this_dir>/logs/registrations.log"
 */

const fs = require('fs');
const fsp = fs.promises;
const path = require('path');
const crypto = require('crypto');
const nodemailer = require('nodemailer');
const mysql = require('mysql');

/**
 * Custom error type used to carry an error code and optional metadata.
 */
class RegistrationError extends Error {
  constructor(message, { code, cause, meta } = {}) {
    super(message);
    this.name = 'RegistrationError';
    this.code = code || 'REGISTRATION_ERROR';
    this.cause = cause;
    this.meta = meta;
  }
}

/**
 * Ensure a directory exists (mkdir -p).
 *
 * @param {string} dirPath
 * @returns {Promise<void>}
 */
async function ensureDir(dirPath) {
  await fsp.mkdir(dirPath, { recursive: true });
}

/**
 * Wrap mysql connection.query into a Promise.
 *
 * @param {import('mysql').Connection} conn
 * @param {string} sql
 * @param {any[]} params
 * @returns {Promise<any>}
 */
function queryAsync(conn, sql, params) {
  return new Promise((resolve, reject) => {
    conn.query(sql, params, (err, results) => {
      if (err) return reject(err);
      resolve(results);
    });
  });
}

/**
 * Wrap mysql connection.connect into a Promise.
 *
 * @param {import('mysql').Connection} conn
 * @returns {Promise<void>}
 */
function connectAsync(conn) {
  return new Promise((resolve, reject) => {
    conn.connect((err) => {
      if (err) return reject(err);
      resolve();
    });
  });
}

/**
 * Wrap mysql connection.end into a Promise.
 *
 * @param {import('mysql').Connection} conn
 * @returns {Promise<void>}
 */
function endAsync(conn) {
  return new Promise((resolve) => {
    // mysql end() callback signature: (err) => void, but we don't want to throw during cleanup.
    conn.end(() => resolve());
  });
}

/**
 * Generate a cryptographically secure random token.
 *
 * @param {number} bytes
 * @returns {Promise<string>} hex token
 */
async function generateTokenHex(bytes = 32) {
  const buf = await crypto.randomBytes(bytes);
  return buf.toString('hex');
}

/**
 * Hash a password using sha256 (matches the original code’s behavior).
 *
 * IMPORTANT: In real apps, prefer bcrypt/argon2. Kept as-is to preserve behavior from the authoritative input.
 *
 * @param {string} password
 * @returns {string}
 */
function hashPasswordSha256(password) {
  return crypto.createHash('sha256').update(password).digest('hex');
}

/**
 * Load a template file and replace placeholders.
 *
 * @param {string} templatePath
 * @param {Record<string, string | number>} variables
 * @returns {Promise<string>}
 */
async function renderTemplateFromFile(templatePath, variables) {
  const template = await fsp.readFile(templatePath, 'utf8');
  let html = template;

  // Simple handlebars-like replacement compatible with original code.
  for (const [key, value] of Object.entries(variables)) {
    html = html.replace(new RegExp(`{{\\s*${escapeRegExp(key)}\\s*}}`, 'g'), String(value));
  }

  return html;
}

function escapeRegExp(str) {
  return String(str).replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

/**
 * Create a nodemailer transporter from environment variables.
 *
 * @returns {import('nodemailer').Transporter}
 */
function createMailTransporterFromEnv() {
  const host = process.env.SMTP_HOST;
  const portRaw = process.env.SMTP_PORT;
  const user = process.env.SMTP_USER;
  const pass = process.env.SMTP_PASS;

  if (!host || !portRaw || !user || !pass) {
    throw new RegistrationError('SMTP configuration is missing', {
      code: 'SMTP_CONFIG_MISSING',
      meta: {
        missing: [
          !host ? 'SMTP_HOST' : null,
          !portRaw ? 'SMTP_PORT' : null,
          !user ? 'SMTP_USER' : null,
          !pass ? 'SMTP_PASS' : null,
        ].filter(Boolean),
      },
    });
  }

  const port = Number(portRaw);
  if (!Number.isFinite(port)) {
    throw new RegistrationError('SMTP_PORT must be a number', {
      code: 'SMTP_CONFIG_INVALID',
      meta: { SMTP_PORT: portRaw },
    });
  }

  return nodemailer.createTransport({
    host,
    port,
    auth: { user, pass },
  });
}

/**
 * Send a verification/welcome email.
 *
 * @param {object} params
 * @param {string} params.to
 * @param {string} params.subject
 * @param {string} params.html
 * @returns {Promise<void>}
 */
async function sendMail({ to, subject, html }) {
  const transporter = createMailTransporterFromEnv();
  const from = process.env.SMTP_FROM || process.env.SMTP_USER;

  await transporter.sendMail({
    from,
    to,
    subject,
    html,
  });
}

/**
 * Append a registration event line to the registration log.
 *
 * @param {string} logPath
 * @param {string} line
 * @returns {Promise<void>}
 */
async function appendRegistrationLog(logPath, line) {
  await ensureDir(path.dirname(logPath));
  await fsp.appendFile(logPath, line, 'utf8');
}

/**
 * Create a mysql connection from environment variables.
 *
 * @returns {import('mysql').Connection}
 */
function createDbConnectionFromEnv() {
  const host = process.env.MYSQL_HOST;
  const user = process.env.MYSQL_USER;
  const password = process.env.MYSQL_PASSWORD;
  const database = process.env.MYSQL_DATABASE;

  if (!host || !user || !password || !database) {
    throw new RegistrationError('MySQL configuration is missing', {
      code: 'DB_CONFIG_MISSING',
      meta: {
        missing: [
          !host ? 'MYSQL_HOST' : null,
          !user ? 'MYSQL_USER' : null,
          !password ? 'MYSQL_PASSWORD' : null,
          !database ? 'MYSQL_DATABASE' : null,
        ].filter(Boolean),
      },
    });
  }

  return mysql.createConnection({ host, user, password, database });
}

/**
 * PUBLIC_INTERFACE
 * Process a user registration end-to-end with async/await, extracted helpers, and improved error handling.
 *
 * Preserves the original functional behavior:
 * - checks email uniqueness
 * - generates verification token
 * - sha256-hashes password
 * - inserts user with created_at NOW()
 * - loads welcome.html template, replaces {{email}}, {{token}}, {{userId}}
 * - sends email
 * - appends a line to logs/registrations.log
 *
 * @param {{email: string, password: string}} userData
 * @returns {Promise<{userId: number, token: string}>} summary
 */
async function processUserRegistration(userData) {
  validateUserData(userData);

  const conn = createDbConnectionFromEnv();
  const templatePath =
    process.env.REGISTRATION_TEMPLATE_PATH || path.join(__dirname, 'templates', 'welcome.html');
  const logPath =
    process.env.REGISTRATION_LOG_PATH || path.join(__dirname, 'logs', 'registrations.log');

  try {
    await connectAsync(conn);

    const existing = await queryAsync(conn, 'SELECT id FROM users WHERE email = ?', [userData.email]);
    if (Array.isArray(existing) && existing.length > 0) {
      throw new RegistrationError('email exists', { code: 'EMAIL_EXISTS', meta: { email: userData.email } });
    }

    const token = await generateTokenHex(32);
    const hash = hashPasswordSha256(userData.password);

    const insertResult = await queryAsync(
      conn,
      'INSERT INTO users (email, password_hash, verification_token, created_at) VALUES (?, ?, ?, NOW())',
      [userData.email, hash, token]
    );

    const userId = insertResult && insertResult.insertId;
    if (!userId) {
      throw new RegistrationError('Insert succeeded but did not return insertId', {
        code: 'DB_INSERT_NO_ID',
        meta: { insertResult },
      });
    }

    const html = await renderTemplateFromFile(templatePath, {
      email: userData.email,
      token,
      userId,
    });

    await sendMail({
      to: userData.email,
      subject: 'Welcome - verify your email',
      html,
    });

    await appendRegistrationLog(
      logPath,
      `${new Date().toISOString()} - registered: ${userData.email} (id: ${userId})\n`
    );

    return { userId, token };
  } catch (err) {
    // Normalize unknown errors into RegistrationError for consistent upstream handling.
    if (err instanceof RegistrationError) {
      throw err;
    }
    throw new RegistrationError('Registration failed', { code: 'REGISTRATION_FAILED', cause: err });
  } finally {
    await endAsync(conn);
  }
}

/**
 * Validate registration inputs early to avoid failing deep in the flow.
 *
 * @param {{email: string, password: string}} userData
 */
function validateUserData(userData) {
  if (!userData || typeof userData !== 'object') {
    throw new RegistrationError('userData must be an object', { code: 'INVALID_INPUT' });
  }
  const { email, password } = userData;

  if (typeof email !== 'string' || email.trim() === '') {
    throw new RegistrationError('email is required', { code: 'INVALID_EMAIL' });
  }
  // Minimal email format check to avoid obvious bad inputs.
  if (!email.includes('@')) {
    throw new RegistrationError('email is invalid', { code: 'INVALID_EMAIL' });
  }
  if (typeof password !== 'string' || password.length < 1) {
    throw new RegistrationError('password is required', { code: 'INVALID_PASSWORD' });
  }
}

module.exports = {
  processUserRegistration,
  RegistrationError,

  // Export helpers for reuse/testing (if needed by consumers).
  createDbConnectionFromEnv,
  queryAsync,
  connectAsync,
  endAsync,
  generateTokenHex,
  hashPasswordSha256,
  renderTemplateFromFile,
  sendMail,
  appendRegistrationLog,
};
