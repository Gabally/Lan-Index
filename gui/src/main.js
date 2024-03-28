import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'

import WaveUI from 'wave-ui'
import 'wave-ui/dist/wave-ui.css'
import '@mdi/font/css/materialdesignicons.min.css'

createApp(App).use(WaveUI, { theme: 'dark' }).mount('#app')
