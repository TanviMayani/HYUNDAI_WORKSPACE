import { createApi } from "@reduxjs/toolkit/query/react";
import { COMMON_API_URL } from "../../constants/apiUrls";
import { axiosBaseQuery } from "../../utils/helper";

export const commonApis = createApi({
  baseQuery: axiosBaseQuery({
    baseUrl: "",
  }),
  keepUnusedDataFor: 5,
  refetchOnMountOrArgChange: true,
  reducerPath: "commonapi",
  endpoints: (builder) => ({
    login: builder.mutation({
      query: (data) => {
        return {
          url: `${COMMON_API_URL.login}`,
          method: "POST",
          data,
        };
      },
    }),
    forgotPassword: builder.mutation({
      query: (data) => {
        return {
          url: `${COMMON_API_URL.forgotPassword}`,
          method: "POST",
          data,
        };
      },
    }),
    resetPassword: builder.mutation({
      query: (data) => {
        return {
          url: `${COMMON_API_URL.resetPassword}`,
          method: "POST",
          data,
        };
      },
    }),
    createApiKey: builder.mutation({
      query: (data) => {
        return {
          url: `${COMMON_API_URL.createApiKey}`,
          method: "POST",
          data,
        };
      },
    }),
    receiveApiKey: builder.query({
      query: () => {
        return {
          method: "GET",
          url: `${COMMON_API_URL.receiveApiKey}`,
        };
      },
    }),

    tokenCheck: builder.query({
      query: () => {
        return {
          method: "GET",
          url: `${COMMON_API_URL.tokenCheck}`,
        };
      },
    }),

    serviceList: builder.query({
      query: () => {
        return {
          method: "GET",
          url: `${COMMON_API_URL.serviceList}`,
        };
      },
    }),

    moduleList: builder.query({
      query: () => {
        return {
          method: "GET",
          url: `${COMMON_API_URL.moduleList}`,
        };
      },
    }),

    getSample: builder.query({
      query: (data) => {
        return {
          method: "GET",
          url: `${COMMON_API_URL.getSample}/${data?.id}?method_id=${data?.method_id}`,
        };
      },
    }),

    getWorkDocExtraction: builder.query({
      query: (data) => {
        return {
          method: "GET",
          url: `${COMMON_API_URL.getDocExtraction}/${data}`,
        };
      },
    }),

    workflowReport: builder.query({
      query: (data) => {
        return {
          method: "GET",
          url: `${COMMON_API_URL.reportComparison}/${data}`,
        };
      },
    }),

    fetchWorkflow: builder.query({
      query: (data) => {
        return {
          method: "GET",
          url: `${COMMON_API_URL.workflowReport}/${data}`,
        };
      },
    }),

    startService: builder.mutation({
      query: (data) => {
        return {
          url: `${COMMON_API_URL.serviceList}/${data}/start`,
          method: "POST",
          data,
        };
      },
    }),

    stopService: builder.mutation({
      query: (data) => {
        return {
          url: `${COMMON_API_URL.serviceList}/${data}/stop`,
          method: "POST",
          data,
        };
      },
    }),

    createWorkflow: builder.mutation({
      query: (data) => {
        return {
          url: `${COMMON_API_URL.createWorkflow}`,
          method: "POST",
          data,
        };
      },
    }),

    createProposer: builder.mutation({
      query: ({ workId, formData }) => {
        return {
          url: `${COMMON_API_URL.createWorkflow}/${workId}`,
          method: "PATCH",
          data: formData,
        };
      },
    }),

    addFileWorkflow: builder.mutation({
      query: ({ workId, formData }) => {
        return {
          url: `${COMMON_API_URL.createWorkflow}/${workId}`,
          method: "POST",
          data: formData,
          headers: {
            "Content-Type": "multipart/form-data",
          },
        };
      },
    }),
  }),
});
export const {
  useResetPasswordMutation,
  useAddFileWorkflowMutation,
  useServiceListQuery,
  useForgotPasswordMutation,
  useReceiveApiKeyQuery,
  useCreateApiKeyMutation,
  useLoginMutation,
  useStartServiceMutation,
  useModuleListQuery,
  useStopServiceMutation,
  useGetSampleQuery,
  useCreateWorkflowMutation,
  useGetWorkDocExtractionQuery,
  useWorkflowReportQuery,
  useFetchWorkflowQuery,
  useCreateProposerMutation,
  useTokenCheckQuery,
} = commonApis;
