import { createApp } from 'vue'
import App from './App.vue'
import { setupI18n } from './locales'
import { setupAssets, setupScrollbarStyle } from './plugins'
import { setupStore } from './store'
import { setupRouter } from './router'
import axios from 'axios'

axios.defaults.timeout =  600000;
// axios.defaults.retry = 4;
// axios.defaults.retryDelay = 1000;

async function bootstrap() {
  const app = createApp(App)
  setupAssets()

  setupScrollbarStyle()

  setupStore(app)

  setupI18n(app)

  await setupRouter(app)

	//app.use(createPinia()).mount('#app');

  app.mount('#app')
}

bootstrap()
