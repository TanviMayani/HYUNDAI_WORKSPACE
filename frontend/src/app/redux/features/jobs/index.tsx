import { createApi } from "@reduxjs/toolkit/query/react";
import { COMMON_API_URL } from "../../../constants/apiUrls";
import { axiosBaseQuery } from "../../../utils/helper";

export const jobsApis = createApi({
  baseQuery: axiosBaseQuery({
    baseUrl: ``,
  }),
  reducerPath: "jobs",
  keepUnusedDataFor: 0,
  refetchOnMountOrArgChange: true,
  endpoints: (builder) => ({
    getJob: builder.query<any, any>({
      query: (args: any) => {
        return {
          method: "get",
          url: `${COMMON_API_URL.getJobs}/${args}`,
        };
      },
    }),
    getAllJobs: builder.query<any, any>({
      query: () => {
        return {
          method: "get",
          url: `${COMMON_API_URL.getJobs}`,
        };
      },
    }),
    searchJobs: builder.query<any, any>({
      query: (data) => {
        return {
          method: "get",
          url: `${COMMON_API_URL.searchJobs}?job_name=${data}`,
        };
      },
    }),

    filterJobs: builder.query<any, any>({
      query: (data) => {
        return {
          method: "get",
          url: `${COMMON_API_URL.filterJobs}?start_date=${data?.startDate}&end_date=${data?.endDate}`,
        };
      },
    }),

    listMethod: builder.query<any, any>({
      query: (data) => {
        return {
          method: "get",
          url: `${COMMON_API_URL.listMethod}`,
        };
      },
    }),

    getAllDocuments: builder.query<any, any>({
      query: (args: any) => {
        return {
          method: "get",
          url: `${COMMON_API_URL.getAllDocs}?job_id=${args.jobId}`,
        };
      },
    }),
    getDocument: builder.query<any, any>({
      query: (args: any) => {
        return {
          method: "get",
          url: `${COMMON_API_URL.getAllDocs}/${args}`,
        };
      },
    }),

    deleteJob: builder.mutation({
      query: (data) => {
        return {
          url: `${COMMON_API_URL.getJobs}/${data}`,
          method: "delete",
        };
      },
    }),

    createJob: builder.mutation({
      query: (data) => {
        return {
          url: `${COMMON_API_URL.createJob}`,
          method: "post",
          data,
          headers: {
            "Content-Type": "multipart/form-data",
          },
        };
      },
    }),
    stringMatch: builder.mutation({
      query: (data) => {
        return {
          url: `${COMMON_API_URL.baseUrl}/stringmatch`,
          method: "post",
          data,
        };
      },
    }),
  }),
});
export const {
  useGetJobQuery,
  useGetAllJobsQuery,
  useCreateJobMutation,
  useGetAllDocumentsQuery,
  useGetDocumentQuery,
  useSearchJobsQuery,
  useFilterJobsQuery,
  useListMethodQuery,
  useDeleteJobMutation,
  useStringMatchMutation,
} = jobsApis;
