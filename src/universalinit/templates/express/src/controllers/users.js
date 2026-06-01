const usersService = require('../services/users');

const ALLOWED_SORT_FIELDS = new Set(['id', 'firstName', 'lastName', 'email', 'createdAt']);
const ALLOWED_SORT_DIRS = new Set(['asc', 'desc']);

class UsersController {
  /**
   * Create a user.
   *
   * Enforces email uniqueness within the in-memory store.
   *
   * @param {import('express').Request} req
   * @param {import('express').Response} res
   */
  create(req, res) {
    const { firstName, lastName, email } = req.body;

    const existing = usersService.findByEmail(email);
    if (existing) {
      return res.status(409).json({
        status: 'error',
        message: 'A user with this email already exists',
      });
    }

    const user = usersService.createUser({ firstName, lastName, email });
    return res.status(201).json({
      status: 'ok',
      data: user,
    });
  }

  /**
   * List users (paginated/sorted/filtered).
   *
   * Query params:
   * - page (number, default 1)
   * - pageSize (number, default 10)
   * - sortBy (id|firstName|lastName|email|createdAt; default createdAt)
   * - sortDir (asc|desc; default desc)
   * - q (string) full-text search across firstName/lastName/email
   * - firstName, lastName, email (string) field filters (contains, case-insensitive)
   * - createdAfter, createdBefore (ISO dates) createdAt range filters
   *
   * @param {import('express').Request} req
   * @param {import('express').Response} res
   */
  list(req, res) {
    const pageRaw = req.query.page;
    const pageSizeRaw = req.query.pageSize;
    const sortByRaw = req.query.sortBy;
    const sortDirRaw = req.query.sortDir;

    const page = typeof pageRaw === 'string' ? parseInt(pageRaw, 10) : 1;
    const pageSize = typeof pageSizeRaw === 'string' ? parseInt(pageSizeRaw, 10) : 10;

    const sortBy =
      typeof sortByRaw === 'string' && ALLOWED_SORT_FIELDS.has(sortByRaw) ? sortByRaw : 'createdAt';

    const sortDir =
      typeof sortDirRaw === 'string' && ALLOWED_SORT_DIRS.has(sortDirRaw) ? sortDirRaw : 'desc';

    const filters = {
      q: typeof req.query.q === 'string' ? req.query.q : undefined,
      firstName: typeof req.query.firstName === 'string' ? req.query.firstName : undefined,
      lastName: typeof req.query.lastName === 'string' ? req.query.lastName : undefined,
      email: typeof req.query.email === 'string' ? req.query.email : undefined,
      createdAfter: typeof req.query.createdAfter === 'string' ? req.query.createdAfter : undefined,
      createdBefore: typeof req.query.createdBefore === 'string' ? req.query.createdBefore : undefined,
    };

    const result = usersService.listUsersPaged({
      page,
      pageSize,
      sortBy,
      sortDir,
      filters,
    });

    return res.status(200).json({
      status: 'ok',
      data: result,
    });
  }

  /**
   * Get a user by id.
   *
   * @param {import('express').Request} req
   * @param {import('express').Response} res
   */
  getById(req, res) {
    const { id } = req.params;

    const user = usersService.getUserById(id);
    if (!user) {
      return res.status(404).json({
        status: 'error',
        message: 'User not found',
      });
    }

    return res.status(200).json({
      status: 'ok',
      data: user,
    });
  }

  /**
   * Replace a user (PUT).
   *
   * @param {import('express').Request} req
   * @param {import('express').Response} res
   */
  update(req, res) {
    const { id } = req.params;
    const { firstName, lastName, email } = req.body;

    const existing = usersService.getUserById(id);
    if (!existing) {
      return res.status(404).json({
        status: 'error',
        message: 'User not found',
      });
    }

    const emailOwner = usersService.findByEmail(email, id);
    if (emailOwner) {
      return res.status(409).json({
        status: 'error',
        message: 'A user with this email already exists',
      });
    }

    const updated = usersService.updateUser(id, { firstName, lastName, email });
    return res.status(200).json({
      status: 'ok',
      data: updated,
    });
  }

  /**
   * Delete a user.
   *
   * @param {import('express').Request} req
   * @param {import('express').Response} res
   */
  delete(req, res) {
    const { id } = req.params;

    const deleted = usersService.deleteUser(id);
    if (!deleted) {
      return res.status(404).json({
        status: 'error',
        message: 'User not found',
      });
    }

    return res.status(204).send();
  }
}

module.exports = new UsersController();
