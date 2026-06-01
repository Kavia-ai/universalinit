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
 *     User:
 *       type: object
 *       properties:
 *         id:
 *           type: string
 *           example: 1a2b3c4d-1111-2222-3333-abcdefabcdef
 *         name:
 *           type: string
 *           example: Ada Lovelace
 *         email:
 *           type: string
 *           format: email
 *           example: ada@example.com
 *         createdAt:
 *           type: string
 *           format: date-time
 *         updatedAt:
 *           type: string
 *           format: date-time
 *     CreateUserRequest:
 *       type: object
 *       required: [name, email]
 *       properties:
 *         name:
 *           type: string
 *           example: Ada Lovelace
 *         email:
 *           type: string
 *           format: email
 *           example: ada@example.com
 *     UpdateUserRequest:
 *       type: object
 *       required: [name, email]
 *       properties:
 *         name:
 *           type: string
 *           example: Grace Hopper
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
 *     summary: List users
 *     responses:
 *       200:
 *         description: List of users
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 status:
 *                   type: string
 *                   example: ok
 *                 data:
 *                   type: array
 *                   items:
 *                     $ref: '#/components/schemas/User'
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
 *                   $ref: '#/components/schemas/User'
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
 *                   $ref: '#/components/schemas/User'
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
