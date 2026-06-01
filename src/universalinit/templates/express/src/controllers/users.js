const usersService = require('../services/users');

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
    const { name, email } = req.body;

    const existing = usersService.findByEmail(email);
    if (existing) {
      return res.status(409).json({
        status: 'error',
        message: 'A user with this email already exists',
      });
    }

    const user = usersService.createUser({ name, email });
    return res.status(201).json({
      status: 'ok',
      data: user,
    });
  }

  /**
   * List all users.
   *
   * @param {import('express').Request} req
   * @param {import('express').Response} res
   */
  list(req, res) {
    const users = usersService.listUsers();
    return res.status(200).json({
      status: 'ok',
      data: users,
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
    const { name, email } = req.body;

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

    const updated = usersService.updateUser(id, { name, email });
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
