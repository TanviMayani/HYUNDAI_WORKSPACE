import axios, {
  AxiosError,
  AxiosInstance,
  InternalAxiosRequestConfig,
} from "axios";
import toast from "react-hot-toast";
import {
  getApiResponseErrorMessage,
  getResponseFromApiResponse,
} from "./common";
import { tokenDecrypt } from "./tokenEncrypter.js";

const axiosInstance: AxiosInstance = axios.create();

axios.defaults.baseURL = "";

axiosInstance.interceptors.request.use(
  (config: InternalAxiosRequestConfig): InternalAxiosRequestConfig => {
    const userSessionActive = sessionStorage.getItem("token");
    const decryptedToken = userSessionActive && tokenDecrypt(userSessionActive);
    if (config.headers) {
      if (!config.headers["Content-Type"] && !(config.data instanceof FormData)) {
        config.headers["Content-Type"] = "application/json";
      }
      // config.withCredentials = true;
      if (userSessionActive && config.headers) {
        config.headers["Authorization"] = `Bearer ${decryptedToken}`;
      }
    }
    return config;
  }
);

axiosInstance.interceptors.response.use(
  (response): any => getResponseFromApiResponse(response),
  (error: AxiosError): Promise<never> => {
    if (error.message && error.message === "Network error" && !error.response) {
      toast.error("Newtwork error - Make Sure Api is runnung");
    }
    if (error.response) {
      const { status, data }: any = error.response;
      const message = getApiResponseErrorMessage(data);
      if (status === 404 && message) {
        toast.error(message);
      } else if (status === 403) {
        toast.error("Something went wrong!");
      } else if (status === 500) {
        toast.error("Internal Server Error");
      } else if (status === 502) {
        toast.error("Bad Gateway");
      } else if (status === 503) {
        toast.error(" Service Unavailable");
      } else if (status === 504) {
        toast.error("Gateway Timeout");
      } else if (status === 417) {
        if (data.errors?.service) {
          const errors = Object.values(data?.errors?.service);
          if (errors) {
            //errors?.map((value: any) => toast.error(value));
          }
        } else {
          //message && toast.error(message);
        }
      } else {
        // message && toast.error(message);
      }
    }
    return Promise.reject({
      status: error?.response?.status,
      message: getApiResponseErrorMessage(error?.response?.data),
    });
  }
);
export default axiosInstance;
