const { randomUUID } = require('crypto');

/**
 * Simple in-memory user store.
 *
 * NOTE: This is intentionally ephemeral and resets on server restart.
 * It is suitable for template/demo use only.
 */
class UsersService {
  constructor() {
    /** @type {Map<string, {id: string, name: string, email: string, createdAt: string, updatedAt: string}>} */
    this.usersById = new Map();
  }

  /**
   * @param {{name: string, email: string}} input
   * @returns {{id: string, name: string, email: string, createdAt: string, updatedAt: string}}
   */
  createUser(input) {
    const now = new Date().toISOString();
    const user = {
      id: randomUUID(),
      name: input.name,
      email: input.email,
      createdAt: now,
      updatedAt: now,
    };

    this.usersById.set(user.id, user);
    return user;
  }

  /**
   * @returns {Array<{id: string, name: string, email: string, createdAt: string, updatedAt: string}>}
   */
  listUsers() {
    return Array.from(this.usersById.values());
  }

  /**
   * @param {string} id
   * @returns {{id: string, name: string, email: string, createdAt: string, updatedAt: string} | null}
   */
  getUserById(id) {
    return this.usersById.get(id) ?? null;
  }

  /**
   * @param {string} id
   * @param {{name?: string, email?: string}} patch
   * @returns {{id: string, name: string, email: string, createdAt: string, updatedAt: string} | null}
   */
  updateUser(id, patch) {
    const existing = this.getUserById(id);
    if (!existing) return null;

    const updated = {
      ...existing,
      ...(patch.name !== undefined ? { name: patch.name } : {}),
      ...(patch.email !== undefined ? { email: patch.email } : {}),
      updatedAt: new Date().toISOString(),
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
   * @returns {{id: string, name: string, email: string, createdAt: string, updatedAt: string} | null}
   */
  findByEmail(email, excludeId) {
    for (const user of this.usersById.values()) {
      if (user.email === email && user.id !== excludeId) return user;
    }
    return null;
  }
}

module.exports = new UsersService();
