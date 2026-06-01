const express = require('express');
const usersController = require('../controllers/users');
const { validateCreateUserBody, validateUpdateUserBody } = require('../middleware');

const router = express.Router();

/**
 * @swagger
 * tags:
 *   - name: Users
 *     description: User management
 */

/**
 * @swagger
 * components:
 *   schemas:
 *     UsersTableUser:
 *       type: object
 *       properties:
 *         id:
 *           type: string
 *           example: 1a2b3c4d-1111-2222-3333-abcdefabcdef
 *         firstName:
 *           type: string
 *           example: Ada
 *         lastName:
 *           type: string
 *           example: Lovelace
 *         email:
 *           type: string
 *           format: email
 *           example: ada@example.com
 *         createdAt:
 *           type: string
 *           format: date-time
 *     PaginatedUsersTableUser:
 *       type: object
 *       properties:
 *         items:
 *           type: array
 *           items:
 *             $ref: '#/components/schemas/UsersTableUser'
 *         page:
 *           type: integer
 *           example: 1
 *         pageSize:
 *           type: integer
 *           example: 10
 *         totalItems:
 *           type: integer
 *           example: 57
 *         totalPages:
 *           type: integer
 *           example: 6
 *     CreateUserRequest:
 *       type: object
 *       required: [firstName, lastName, email]
 *       properties:
 *         firstName:
 *           type: string
 *           example: Ada
 *         lastName:
 *           type: string
 *           example: Lovelace
 *         email:
 *           type: string
 *           format: email
 *           example: ada@example.com
 *     UpdateUserRequest:
 *       type: object
 *       required: [firstName, lastName, email]
 *       properties:
 *         firstName:
 *           type: string
 *           example: Grace
 *         lastName:
 *           type: string
 *           example: Hopper
 *         email:
 *           type: string
 *           format: email
 *           example: grace@example.com
 */

/**
 * @swagger
 * /users:
 *   get:
 *     tags: [Users]
 *     summary: List users (paginated)
 *     description: Server-side pagination, sorting, and filtering for a Users table.
 *     parameters:
 *       - in: query
 *         name: page
 *         schema:
 *           type: integer
 *           default: 1
 *         description: 1-based page index.
 *       - in: query
 *         name: pageSize
 *         schema:
 *           type: integer
 *           default: 10
 *         description: Number of rows per page.
 *       - in: query
 *         name: sortBy
 *         schema:
 *           type: string
 *           enum: [id, firstName, lastName, email, createdAt]
 *           default: createdAt
 *       - in: query
 *         name: sortDir
 *         schema:
 *           type: string
 *           enum: [asc, desc]
 *           default: desc
 *       - in: query
 *         name: q
 *         schema:
 *           type: string
 *         description: Full-text search across firstName, lastName, and email.
 *       - in: query
 *         name: firstName
 *         schema:
 *           type: string
 *         description: Filter by firstName (contains, case-insensitive).
 *       - in: query
 *         name: lastName
 *         schema:
 *           type: string
 *         description: Filter by lastName (contains, case-insensitive).
 *       - in: query
 *         name: email
 *         schema:
 *           type: string
 *         description: Filter by email (contains, case-insensitive).
 *       - in: query
 *         name: createdAfter
 *         schema:
 *           type: string
 *           format: date-time
 *         description: createdAt >= createdAfter (ISO date string).
 *       - in: query
 *         name: createdBefore
 *         schema:
 *           type: string
 *           format: date-time
 *         description: createdAt <= createdBefore (ISO date string).
 *     responses:
 *       200:
 *         description: Paginated users
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 status:
 *                   type: string
 *                   example: ok
 *                 data:
 *                   $ref: '#/components/schemas/PaginatedUsersTableUser'
 */
router.get('/', usersController.list.bind(usersController));

/**
 * @swagger
 * /users:
 *   post:
 *     tags: [Users]
 *     summary: Create user
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/CreateUserRequest'
 *     responses:
 *       201:
 *         description: Created user
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 status:
 *                   type: string
 *                   example: ok
 *                 data:
 *                   $ref: '#/components/schemas/UsersTableUser'
 *       400:
 *         description: Invalid request body
 *       409:
 *         description: Email already exists
 */
router.post('/', validateCreateUserBody(), usersController.create.bind(usersController));

/**
 * @swagger
 * /users/{id}:
 *   get:
 *     tags: [Users]
 *     summary: Get user by id
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: string
 *     responses:
 *       200:
 *         description: User
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 status:
 *                   type: string
 *                   example: ok
 *                 data:
 *                   $ref: '#/components/schemas/UsersTableUser'
 *       404:
 *         description: User not found
 */
router.get('/:id', usersController.getById.bind(usersController));

/**
 * @swagger
 * /users/{id}:
 *   put:
 *     tags: [Users]
 *     summary: Replace user
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: string
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/UpdateUserRequest'
 *     responses:
 *       200:
 *         description: Updated user
 *       400:
 *         description: Invalid request body
 *       404:
 *         description: User not found
 *       409:
 *         description: Email already exists
 */
router.put('/:id', validateUpdateUserBody(), usersController.update.bind(usersController));

/**
 * @swagger
 * /users/{id}:
 *   delete:
 *     tags: [Users]
 *     summary: Delete user
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: string
 *     responses:
 *       204:
 *         description: Deleted
 *       404:
 *         description: User not found
 */
router.delete('/:id', usersController.delete.bind(usersController));

module.exports = router;
