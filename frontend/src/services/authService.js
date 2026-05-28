import api from './api';

const fallback = {
  loginEndpoint: '/api/auth/login',
  registerEndpoint: '/api/register',
};

const openApiCache = {
  initialized: false,
  spec: null,
  loginEndpoint: fallback.loginEndpoint,
  registerEndpoint: fallback.registerEndpoint,
};

const findEndpoint = (paths, keywords, preferredPaths = []) => {
  const normalizedKeys = keywords.map((keyword) => keyword.toLowerCase());
  for (const path of preferredPaths) {
    if (paths[path] && paths[path].post) {
      return path;
    }
  }

  for (const [path, methods] of Object.entries(paths)) {
    if (!methods.post) continue;
    const pathLower = path.toLowerCase();
    const { operationId = '', tags = [] } = methods.post;
    const operationText = `${operationId}`.toLowerCase();
    const tagsText = Array.isArray(tags) ? tags.join(' ').toLowerCase() : String(tags).toLowerCase();

    if (normalizedKeys.some((keyword) => pathLower.includes(`/${keyword}`))) {
      return path;
    }
    if (normalizedKeys.some((keyword) => operationText.includes(keyword))) {
      return path;
    }
    if (normalizedKeys.some((keyword) => tagsText.includes(keyword))) {
      return path;
    }
  }

  return null;
};

const detectAuthEndpoints = async () => {
  if (openApiCache.initialized) {
    return openApiCache;
  }

  try {
    const response = await api.get('/openapi.json');
    const paths = response?.data?.paths || {};
    openApiCache.spec = response.data;
    openApiCache.loginEndpoint =
      findEndpoint(paths, ['login', 'token'], [
        '/api/auth/login',
        '/auth/login',
        '/api/login',
        '/login',
        '/api/token',
        '/token',
      ]) || fallback.loginEndpoint;
    openApiCache.registerEndpoint =
      findEndpoint(paths, ['register', 'signup'], [
        '/api/register',
        '/register',
        '/api/auth/register',
        '/auth/register',
      ]) || fallback.registerEndpoint;
  } catch (error) {
    openApiCache.loginEndpoint = fallback.loginEndpoint;
    openApiCache.registerEndpoint = fallback.registerEndpoint;
  } finally {
    openApiCache.initialized = true;
  }

  return openApiCache;
};

const login = async (identifier, password) => {
  const { loginEndpoint } = await detectAuthEndpoints();
  const formData = new URLSearchParams();
  formData.append('username', identifier);
  formData.append('password', password);

  try {
    return await api.post(loginEndpoint, { email: identifier, password });
  } catch (error) {
    const status = error?.response?.status;
    if (status === 400 || status === 422) {
      return await api.post(loginEndpoint, formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });
    }
    throw error;
  }
};

const register = async (username, email, password) => {
  const { registerEndpoint } = await detectAuthEndpoints();
  return await api.post(registerEndpoint, {
    username,
    email,
    password,
  });
};

const logout = () => {
  localStorage.removeItem('access_token');
};

const getCurrentUser = async () => api.get('/api/me');

const updateProfile = async (payload) => api.put('/api/profile/update', payload);

export const authService = {
  login,
  register,
  logout,
  getCurrentUser,
  updateProfile,
};

export default authService;
