const backendUrl = import.meta.env.VITE_BACKEND_URL || "http://localhost:8002/v1/hiib";

export const COMMON_API_URL = {
  baseUrl: backendUrl,
  login: `${backendUrl}/login`,
  register: `${backendUrl}/signup`,
  forgotPassword: `${backendUrl}/forgot-password`,
  resetPassword: `${backendUrl}/reset-password`,
  getUserProfile: `${backendUrl}/v1/idp/members/profile`,
  updateUserProfile: `${backendUrl}/v1/idp/members/profile`,
  getJobs: `${backendUrl}/job`,
  searchJobs: `${backendUrl}/job/search/`,
  listMethod: `${backendUrl}/job/method/`,
  filterJobs: `${backendUrl}/job/filter/`,
  createJob: `${backendUrl}/job/invoice`,
  getAllDocs: `${backendUrl}/job/document`,
  getDoc: `${backendUrl}/jobs/document`,
  moduleList: `${backendUrl}/module/module_list`,
  getSample: `${backendUrl}/module/module_samples`,
  tokenCheck: `${backendUrl}/token_check`,
};
