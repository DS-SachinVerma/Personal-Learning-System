import axios from 'axios';

const BASE = 'http://127.0.0.1:8000';

const api = axios.create({ baseURL: BASE });

export const getDomains = () => api.get('/tasks/domains').then((r) => r.data);
export const getTasks = (params = {}) => api.get('/tasks/', { params }).then((r) => r.data);
export const getTask = (idOrSlug) => api.get(`/tasks/${idOrSlug}`).then((r) => r.data);

export const getTechniques = (params = {}) => api.get('/techniques/', { params }).then((r) => r.data);
export const getTechnique = (id) => api.get(`/techniques/${id}`).then((r) => r.data);

export const getResources = (params = {}) => api.get('/resources/', { params }).then((r) => r.data);
export const getResource = (id) => api.get(`/resources/${id}`).then((r) => r.data);

export const getInsights = (params = {}) => api.get('/insights/', { params }).then((r) => r.data);
export const getExperiments = (params = {}) => api.get('/experiments/', { params }).then((r) => r.data);
export const getDigest = (params = {}) => api.get('/digest/', { params }).then((r) => r.data);

export default api;
