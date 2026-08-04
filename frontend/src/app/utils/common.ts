import { APP_USER_URLS } from "../constants/urls";

export const IsServer = typeof window === "undefined";

export const getApiResponseErrorMessage = (object: any) => {
  if (object?.detail) return object?.detail?.[0]?.msg;
  else if (Array.isArray(object?.errors)) {
    return object?.errors?.join(" ");
  }
  return "Something went wrong";
};

export const getResponseFromApiResponse = (object: any): any => {
  const { data, status, headers } = object;
  if (data?.meta || data?.data?.length || data?.data?.length == 0) {
    return { data: data?.detail?.[0]?.data, meta: data?.meta };
  }
  const response = data?.detail?.[0]?.data;
  return response;
};

export const redirectToUrl = (endpoint: string | null = null) => {
  return endpoint ? (window.location.href = `/${endpoint}`) : null;
};

export const getAuthRoute = () => {
  return `${APP_USER_URLS.login}`;
};

export const toastOptions = {
  duration: 4000,
  success: {
    style: {
      background: "#F3FCF4",
      border: "1px solid #4FD564",
      borderRadius: "4px",
    },
  },
  error: {
    style: {
      background: "#FDF6F6",
      border: "1px solid #EC4140",
      borderRadius: "4px",
    },
  },
};

export const ClientType: any = {
  client: "Client",
  freelancer: "Freelancer",
  agency: "Agency",
};

export const ProjectType = (scope: string) => {
  return scope === "small"
    ? "One Time Project"
    : scope === "medium"
    ? "Ongoing Project"
    : "Complex Project";
};
