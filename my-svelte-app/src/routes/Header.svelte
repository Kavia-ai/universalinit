<script lang="ts">
	import { page } from '$app/state';
	import logo from '$lib/images/svelte-logo.svg';

	// PUBLIC_INTERFACE
	/**
	 * Theme toggle state and event handler.
	 */
	import { onMount } from 'svelte';
	let isDark = false;

	onMount(() => {
		// On load, set theme based on saved setting or media query
		const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
		const saved = localStorage.getItem('theme');
		isDark = saved === 'dark' ? true : saved === 'light' ? false : prefersDark;
		updateTheme();
	});

	// PUBLIC_INTERFACE
	function toggleTheme() {
		isDark = !isDark;
		updateTheme();
	}

	function updateTheme() {
		const root = document.documentElement;
		const body = document.body;
		if (isDark) {
			root.classList.add('theme-dark');
			root.classList.remove('theme-light');
			body.classList.add('theme-dark');
			body.classList.remove('theme-light');
			localStorage.setItem('theme', 'dark');
		} else {
			root.classList.remove('theme-dark');
			root.classList.add('theme-light');
			body.classList.remove('theme-dark');
			body.classList.add('theme-light');
			localStorage.setItem('theme', 'light');
		}
	}
</script>

<header>
	<div class="corner">
		<a href="https://svelte.dev/docs/kit">
			<img src={logo} alt="SvelteKit" />
		</a>
	</div>

	<nav>
		<svg viewBox="0 0 2 3" aria-hidden="true">
			<path d="M0,0 L1,2 C1.5,3 1.5,3 2,3 L2,0 Z" />
		</svg>
		<ul>
			<li aria-current={page.url.pathname === '/' ? 'page' : undefined}>
				<a href="/">Home</a>
			</li>
			<li aria-current={page.url.pathname === '/about' ? 'page' : undefined}>
				<a href="/about">About</a>
			</li>
		</ul>
		<svg viewBox="0 0 2 3" aria-hidden="true">
			<path d="M0,0 L0,3 C0.5,3 0.5,3 1,2 L2,0 Z" />
		</svg>
	</nav>

	<div class="corner">
		<button
			class="theme-toggle"
			on:click={toggleTheme}
			aria-pressed={isDark}
			aria-label={isDark ? "Switch to light mode" : "Switch to dark mode"}
			title={isDark ? "Light mode" : "Dark mode"}
		>
			{#if isDark}
				<!-- Sun Icon -->
				<svg height="1.75em" viewBox="0 0 24 24" width="1.75em" aria-hidden="true">
					<circle cx="12" cy="12" r="5.5" fill="currentColor"/>
					<g stroke="currentColor">
						<line x1="12" y1="2" x2="12" y2="4"/>
						<line x1="12" y1="20" x2="12" y2="22"/>
						<line x1="2" y1="12" x2="4" y2="12"/>
						<line x1="20" y1="12" x2="22" y2="12"/>
						<line x1="5.6" y1="5.6" x2="7" y2="7"/>
						<line x1="17" y1="17" x2="18.4" y2="18.4"/>
						<line x1="5.6" y1="18.4" x2="7" y2="17"/>
						<line x1="17" y1="7" x2="18.4" y2="5.6"/>
					</g>
				</svg>
			{:else}
				<!-- Moon Icon -->
				<svg height="1.75em" viewBox="0 0 24 24" width="1.75em" aria-hidden="true">
					<path d="M21 12.79A9 9 0 0111.21 3 7.5 7.5 0 1021 12.79z" fill="currentColor" />
				</svg>
			{/if}
		</button>
	</div>
</header>

<style>
	header {
		display: flex;
		justify-content: space-between;
	}

	.corner {
		width: 3em;
		height: 3em;
	}

	.corner a {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 100%;
		height: 100%;
	}

	.corner img {
		width: 2em;
		height: 2em;
		object-fit: contain;
	}

	nav {
		display: flex;
		justify-content: center;
		--background: rgba(255, 255, 255, 0.7);
	}

	svg {
		width: 2em;
		height: 3em;
		display: block;
	}

	path {
		fill: var(--background);
	}

	ul {
		position: relative;
		padding: 0;
		margin: 0;
		height: 3em;
		display: flex;
		justify-content: center;
		align-items: center;
		list-style: none;
		background: var(--background);
		background-size: contain;
	}

	li {
		position: relative;
		height: 100%;
	}

	li[aria-current='page']::before {
		--size: 6px;
		content: '';
		width: 0;
		height: 0;
		position: absolute;
		top: 0;
		left: calc(50% - var(--size));
		border: var(--size) solid transparent;
		border-top: var(--size) solid var(--color-theme-1);
	}

	nav a {
		display: flex;
		height: 100%;
		align-items: center;
		padding: 0 0.5rem;
		color: var(--color-text);
		font-weight: 700;
		font-size: 0.8rem;
		text-transform: uppercase;
		letter-spacing: 0.1em;
		text-decoration: none;
		transition: color 0.2s linear;
	}

	a:hover {
		color: var(--color-theme-1);
	}
	.theme-toggle {
		background: none;
		border: none;
		cursor: pointer;
		color: var(--color-theme-1);
		display: flex;
		align-items: center;
		justify-content: center;
		width: 2em;
		height: 2em;
		padding: 0.25em;
		transition: color 0.2s;
		border-radius: 50%;
		outline: none;
	}
	.theme-toggle:focus,
	.theme-toggle:hover {
		background: var(--color-bg-2);
		color: var(--color-theme-2);
	}

	.theme-toggle svg {
		display: block;
		width: 1.3em;
		height: 1.3em;
	}

	.corner {
		position: relative;
	}

	@media (max-width: 520px) {
		.theme-toggle {
			width: 1.75em;
			height: 1.75em;
		}
	}
</style>
