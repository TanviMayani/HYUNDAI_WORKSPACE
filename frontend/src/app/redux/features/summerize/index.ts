import { createApi } from "@reduxjs/toolkit/query/react";
import { COMMON_API_URL } from "../../../constants/apiUrls";
import { axiosBaseQuery } from "../../../utils/helper";

export const summerizeApi = createApi({
  baseQuery: axiosBaseQuery({
    baseUrl: ``,
  }),
  reducerPath: "summerize",
  keepUnusedDataFor: 5,
  refetchOnMountOrArgChange: true,
  endpoints: (builder) => ({
    listSummerize: builder.query<any, any>({
      query: () => {
        return {
          method: "GET",
          url: `${COMMON_API_URL.listSummerize}`,
        };
      },
    }),
    getDocSummerize: builder.query<any, any>({
      query: (data) => {
        return {
          method: "GET",
          url: `${COMMON_API_URL.listSummerize}/${data}`,
        };
      },
    }),

    summerizeHistory: builder.query<any, any>({
      query: (data) => {
        return {
          method: "GET",
          url: `${COMMON_API_URL.summerizeHistory}/${data}`,
        };
      },
    }),

    renameInstance: builder.mutation({
      query: (data) => {
        const {id, ...body} = data
        return {
          url: `${COMMON_API_URL.listSummerize}/${id}`,
          method: "PATCH",
          data: body,
        };
      },
    }),

    addSummerize: builder.mutation({
      query: (data) => {
        const {id, ...body} = data
        return {
          url: `${COMMON_API_URL.addSummerize}/${id}`,
          method: "POST",
          data: body,
        };
      },
    }),

    addDataSource: builder.mutation({
      query: ({id, formData}) => {
        return {
          url: `${COMMON_API_URL.addSummarizeDoc}/${id}`,
          method: "PUT",
          data: formData,
          headers: {
            "Content-Type": "multipart/form-data",
          },
        };
      },
    }),
    createSummerize: builder.mutation({
      query: (data) => {
        return {
          url: `${COMMON_API_URL.listSummerize}`,
          method: "POST",
          data: data,
          headers: {
            "Content-Type": "multipart/form-data",
          },
        };
      },
    }),
    deleteInstance: builder.mutation({
      query: (data) => {
        return {
          url: `${COMMON_API_URL.listSummerize}/${data}`,
          method: "delete",
        };
      },
    }),
    deleteDataSource: builder.mutation({
      query: (data) => {
        return {
          url: `${COMMON_API_URL.deleteSummarizeDoc}/${data}`,
          method: "delete",
        };
      },
    }),
  }),
});
export const {
  useCreateSummerizeMutation,
  useListSummerizeQuery,
  useGetDocSummerizeQuery,
  useDeleteInstanceMutation,
  useRenameInstanceMutation,
  useDeleteDataSourceMutation,
  useAddDataSourceMutation,
  useAddSummerizeMutation,
  useSummerizeHistoryQuery
} = summerizeApi;
