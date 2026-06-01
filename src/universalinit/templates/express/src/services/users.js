const { randomUUID } = require('crypto');

/**
 * Users table fields for the template:
 * - id
 * - firstName
 * - lastName
 * - email
 * - createdAt
 *
 * Simple in-memory user store.
 *
 * NOTE: This is intentionally ephemeral and resets on server restart.
 * It is suitable for template/demo use only.
 */
class UsersService {
  constructor() {
    /** @type {Map<string, {id: string, firstName: string, lastName: string, email: string, createdAt: string}>} */
    this.usersById = new Map();

    // Seed a handful of deterministic demo users for table UX.
    this._seed();
  }

  _seed() {
    const now = new Date();
    const seed = [
      ['Ada', 'Lovelace', 'ada@example.com'],
      ['Grace', 'Hopper', 'grace@example.com'],
      ['Alan', 'Turing', 'alan@example.com'],
      ['Katherine', 'Johnson', 'katherine@example.com'],
      ['Donald', 'Knuth', 'donald@example.com'],
      ['Margaret', 'Hamilton', 'margaret@example.com'],
      ['Barbara', 'Liskov', 'barbara@example.com'],
      ['Edsger', 'Dijkstra', 'edsger@example.com'],
      ['Linus', 'Torvalds', 'linus@example.com'],
      ['Guido', 'van Rossum', 'guido@example.com'],
      ['Tim', 'Berners-Lee', 'tim@example.com'],
      ['Ken', 'Thompson', 'ken@example.com'],
      ['Dennis', 'Ritchie', 'dennis@example.com'],
      ['James', 'Gosling', 'james@example.com'],
      ['Brendan', 'Eich', 'brendan@example.com'],
    ];

    seed.forEach(([firstName, lastName, email], idx) => {
      const createdAt = new Date(now.getTime() - idx * 24 * 60 * 60 * 1000).toISOString();
      const user = {
        id: randomUUID(),
        firstName,
        lastName,
        email,
        createdAt,
      };
      this.usersById.set(user.id, user);
    });
  }

  /**
   * @param {{firstName: string, lastName: string, email: string}} input
   * @returns {{id: string, firstName: string, lastName: string, email: string, createdAt: string}}
   */
  createUser(input) {
    const user = {
      id: randomUUID(),
      firstName: input.firstName,
      lastName: input.lastName,
      email: input.email,
      createdAt: new Date().toISOString(),
    };

    this.usersById.set(user.id, user);
    return user;
  }

  /**
   * @returns {Array<{id: string, firstName: string, lastName: string, email: string, createdAt: string}>}
   */
  listUsers() {
    return Array.from(this.usersById.values());
  }

  /**
   * @param {string} id
   * @returns {{id: string, firstName: string, lastName: string, email: string, createdAt: string} | null}
   */
  getUserById(id) {
    return this.usersById.get(id) ?? null;
  }

  /**
   * @param {string} id
   * @param {{firstName?: string, lastName?: string, email?: string}} patch
   * @returns {{id: string, firstName: string, lastName: string, email: string, createdAt: string} | null}
   */
  updateUser(id, patch) {
    const existing = this.getUserById(id);
    if (!existing) return null;

    const updated = {
      ...existing,
      ...(patch.firstName !== undefined ? { firstName: patch.firstName } : {}),
      ...(patch.lastName !== undefined ? { lastName: patch.lastName } : {}),
      ...(patch.email !== undefined ? { email: patch.email } : {}),
      // Keep createdAt stable for demo simplicity.
    };

    this.usersById.set(id, updated);
    return updated;
  }

  /**
   * @param {string} id
   * @returns {boolean} true if deleted, false if not found
   */
  deleteUser(id) {
    return this.usersById.delete(id);
  }

  /**
   * @param {string} email
   * @param {string=} excludeId
   * @returns {{id: string, firstName: string, lastName: string, email: string, createdAt: string} | null}
   */
  findByEmail(email, excludeId) {
    for (const user of this.usersById.values()) {
      if (user.email === email && user.id !== excludeId) return user;
    }
    return null;
  }

  /**
   * Server-side pagination/sorting/filtering for the Users table.
   *
   * @param {{
   *   page: number,
   *   pageSize: number,
   *   sortBy: 'id'|'firstName'|'lastName'|'email'|'createdAt',
   *   sortDir: 'asc'|'desc',
   *   filters: {q?: string, firstName?: string, lastName?: string, email?: string, createdAfter?: string, createdBefore?: string}
   * }} input
   * @returns {{
   *   items: Array<{id: string, firstName: string, lastName: string, email: string, createdAt: string}>,
   *   page: number,
   *   pageSize: number,
   *   totalItems: number,
   *   totalPages: number
   * }}
   */
  listUsersPaged(input) {
    const page = Number.isFinite(input.page) && input.page > 0 ? Math.floor(input.page) : 1;
    const pageSize =
      Number.isFinite(input.pageSize) && input.pageSize > 0 ? Math.floor(input.pageSize) : 10;

    const sortBy = input.sortBy ?? 'createdAt';
    const sortDir = input.sortDir ?? 'desc';
    const filters = input.filters ?? {};

    const normalize = (v) => (typeof v === 'string' ? v.trim().toLowerCase() : '');

    const q = normalize(filters.q);
    const firstName = normalize(filters.firstName);
    const lastName = normalize(filters.lastName);
    const email = normalize(filters.email);

    const createdAfter = typeof filters.createdAfter === 'string' ? Date.parse(filters.createdAfter) : NaN;
    const createdBefore = typeof filters.createdBefore === 'string' ? Date.parse(filters.createdBefore) : NaN;

    let rows = this.listUsers();

    // Filtering
    rows = rows.filter((u) => {
      if (firstName && !u.firstName.toLowerCase().includes(firstName)) return false;
      if (lastName && !u.lastName.toLowerCase().includes(lastName)) return false;
      if (email && !u.email.toLowerCase().includes(email)) return false;

      if (q) {
        const haystack = `${u.firstName} ${u.lastName} ${u.email}`.toLowerCase();
        if (!haystack.includes(q)) return false;
      }

      const createdAtTs = Date.parse(u.createdAt);
      if (Number.isFinite(createdAfter) && createdAtTs < createdAfter) return false;
      if (Number.isFinite(createdBefore) && createdAtTs > createdBefore) return false;

      return true;
    });

    // Sorting
    rows.sort((a, b) => {
      const dir = sortDir === 'asc' ? 1 : -1;

      /** @type {string|number} */
      let av = a[sortBy];
      /** @type {string|number} */
      let bv = b[sortBy];

      // Ensure createdAt sorts chronologically.
      if (sortBy === 'createdAt') {
        av = Date.parse(a.createdAt);
        bv = Date.parse(b.createdAt);
      }

      if (av < bv) return -1 * dir;
      if (av > bv) return 1 * dir;
      return 0;
    });

    const totalItems = rows.length;
    const totalPages = Math.max(1, Math.ceil(totalItems / pageSize));
    const safePage = Math.min(page, totalPages);
    const start = (safePage - 1) * pageSize;
    const end = start + pageSize;

    return {
      items: rows.slice(start, end),
      page: safePage,
      pageSize,
      totalItems,
      totalPages,
    };
  }
}

module.exports = new UsersService();
