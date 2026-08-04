import { createApi } from "@reduxjs/toolkit/query/react";
import { COMMON_API_URL } from "../../../constants/apiUrls";
import { axiosBaseQuery } from "../../../utils/helper";

export const docQueryApis = createApi({
  baseQuery: axiosBaseQuery({
    baseUrl: ``,
  }),
  keepUnusedDataFor: 5,
  refetchOnMountOrArgChange: true,
  reducerPath: "doc-queries",
  endpoints: (builder) => ({
    listDocInstances: builder.query<any, any>({
      query: () => {
        return {
          method: "GET",
          url: `${COMMON_API_URL.listDocInstance}`,
        };
      },
    }),
    getDocInstance: builder.query<any, any>({
      query: (data) => {
        return {
          method: "GET",
          url: `${COMMON_API_URL.getDocInstance}/${data}`,
        };
      },
    }),

    queryHistory: builder.query<any, any>({
      query: (data) => {
        return {
          method: "GET",
          url: `${COMMON_API_URL.queryHistory}/${data}`,
        };
      },
    }),

    renameInstance: builder.mutation({
      query: (data) => {
        const { id, ...body } = data;
        return {
          url: `${COMMON_API_URL.getDocInstance}/${id}`,
          method: "PATCH",
          data: body,
        };
      },
    }),

    addQuery: builder.mutation({
      query: (data) => {
        const { id, ...body } = data;
        return {
          url: `${COMMON_API_URL.addQuery}/${id}`,
          method: "POST",
          data: body,
        };
      },
    }),

    addDataSource: builder.mutation({
      query: ({ id, formData }) => {
        // const {id, ...body} = data
        return {
          url: `${COMMON_API_URL.addDataSource}/${id}`,
          method: "PUT",
          data: formData,
          headers: {
            "Content-Type": "multipart/form-data",
          },
        };
      },
    }),
    createDocInstance: builder.mutation({
      query: (data) => {
        return {
          url: `${COMMON_API_URL.createDocInstance}`,
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
          url: `${COMMON_API_URL.getDocInstance}/${data}`,
          method: "delete",
        };
      },
    }),

    deleteQa: builder.mutation({
      query: (data) => {
        return {
          url: `${COMMON_API_URL.queryHistory}/${data}`,
          method: "delete",
        };
      },
    }),
    deleteDataSource: builder.mutation({
      query: (data) => {
        return {
          url: `${COMMON_API_URL.deleteDataSource}/${data}`,
          method: "delete",
        };
      },
    }),
  }),
});
export const {
  useCreateDocInstanceMutation,
  useListDocInstancesQuery,
  useGetDocInstanceQuery,
  useDeleteInstanceMutation,
  useRenameInstanceMutation,
  useDeleteDataSourceMutation,
  useAddDataSourceMutation,
  useAddQueryMutation,
  useQueryHistoryQuery,
  useDeleteQaMutation,
} = docQueryApis;
