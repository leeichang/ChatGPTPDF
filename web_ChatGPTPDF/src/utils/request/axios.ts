import axios, { type AxiosResponse } from 'axios'
import { useAppStore, useAuthStore } from '@/store'
const service = axios.create({
  baseURL: import.meta.env.VITE_GLOB_API_URL,
})

service.interceptors.request.use(
  (config) => {
    const token = useAuthStore().token
		const user_guid = useAppStore().user_guid
		if (token ){
      config.headers.Authorization = `Bearer ${token}`
		}

		if(user_guid){
      config.headers['X-GUID'] = user_guid
    }

    return config
  },
  (error) => {
    return Promise.reject(error.response)
  },
)

service.interceptors.response.use(
  (response: AxiosResponse): AxiosResponse => {
    if (response.status === 200)
      return response

    throw new Error(response.status.toString())
  },
  (error) => {
    return Promise.reject(error)
  },
)

// service.interceptors.response.use(undefined, function axiosRetryInterceptor(err) {
// 	var config = err.config;
// 	// If config does not exist or the retry option is not set, reject
// 	if(!config || !config.retry) return Promise.reject(err);

// 	// Set the variable for keeping track of the retry count
// 	config.__retryCount = config.__retryCount || 0;

// 	// Check if we've maxed out the total number of retries
// 	if(config.__retryCount >= config.retry) {
// 			// Reject with the error
// 			return Promise.reject(err);
// 	}

// 	// Increase the retry count
// 	config.__retryCount += 1;

// 	// Create new promise to handle exponential backoff
// 	var backoff = new Promise(function(resolve) {
// 			setTimeout(function() {
// 					resolve();
// 			}, config.retryDelay || 1);
// 	});

// 	// Return the promise in which recalls axios to retry the request
// 	return backoff.then(function() {
// 			return axios(config);
// 	});
// });

export default service
