import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import { pinia } from './store';
import './assets/styles/tailwind.css'
import { useAuthStore } from '@/store/auth';

const app = createApp(App);
app.use(router);
app.use(pinia);

// Initialize auth before mounting to prevent Guest flicker and keep session after F5
const init = async () => {
	const auth = useAuthStore();
	await auth.initialize();
	app.mount('#app');
};

init();
