import { createApi } from "@reduxjs/toolkit/query/react";
import { COMMON_API_URL } from "../../../constants/apiUrls";
import { axiosBaseQuery } from "../../../utils/helper";

export const translationApi = createApi({
  baseQuery: axiosBaseQuery({
    baseUrl: ``,
  }),
  reducerPath: "translation",
  keepUnusedDataFor: 5,
  refetchOnMountOrArgChange: true,
  endpoints: (builder) => ({
    listTranslate: builder.query<any, any>({
      query: () => {
        return {
          method: "GET",
          url: `${COMMON_API_URL.createTranslate}`,
        };
      },
    }),

    languageList: builder.query<any, any>({
      query: () => {
        return {
          method: "GET",
          url: `${COMMON_API_URL.languageList}`,
        };
      },
    }),

    getTranslate: builder.query<any, any>({
      query: (data) => {
        return {
          method: "GET",
          url: `${COMMON_API_URL.createTranslate}/${data}`,
        };
      },
    }),

    translateHistory: builder.query<any, any>({
      query: (data) => {
        return {
          method: "GET",
          url: `${COMMON_API_URL.translateHistory}/${data}`,
        };
      },
    }),

    classificationHistory: builder.query<any, any>({
      query: (data) => {
        return {
          method: "GET",
          url: `${COMMON_API_URL.classificationHistory}/${data}`,
        };
      },
    }),

    getClassificationList: builder.query<any, any>({
      query: (data) => {
        return {
          method: "GET",
          url: `${COMMON_API_URL.classification}`,
        };
      },
    }),

    getClassification: builder.query<any, any>({
      query: (data) => {
        return {
          method: "GET",
          url: `${COMMON_API_URL.classification}/${data}`,
        };
      },
    }),

    renameInstance: builder.mutation({
      query: (data) => {
        const { id, ...body } = data;
        return {
          url: `${COMMON_API_URL.createTranslate}/${id}`,
          method: "PATCH",
          data: body,
        };
      },
    }),

    addSummerize: builder.mutation({
      query: (data) => {
        const { id, ...body } = data;
        return {
          url: `${COMMON_API_URL.addSummerize}/${id}`,
          method: "POST",
          data: body,
        };
      },
    }),

    addDataSource: builder.mutation({
      query: ({ id, formData }) => {
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
    createTranslation: builder.mutation({
      query: (data) => {
        return {
          url: `${COMMON_API_URL.createTranslate}`,
          method: "POST",
          data: data,
          headers: {
            "Content-Type": "multipart/form-data",
          },
        };
      },
    }),

    createClassification: builder.mutation({
      query: (data) => {
        return {
          url: `${COMMON_API_URL.classification}`,
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
          url: `${COMMON_API_URL.createTranslate}/${data}`,
          method: "delete",
        };
      },
    }),
    deleteClassification: builder.mutation({
      query: (data) => {
        return {
          url: `${COMMON_API_URL.classification}/${data}`,
          method: "delete",
        };
      },
    }),

    renameClassification: builder.mutation({
      query: (data) => {
        const { id, ...body } = data;
        return {
          url: `${COMMON_API_URL.classification}/${id}`,
          method: "PATCH",
          data: body,
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

    deleteClassificationDoc: builder.mutation({
      query: (data) => {
        return {
          url: `${COMMON_API_URL.deleteClassificationDoc}/${data}`,
          method: "delete",
        };
      },
    }),
  }),
});
export const {
  useCreateTranslationMutation,
  useCreateClassificationMutation,
  useListTranslateQuery,
  useGetTranslateQuery,
  useDeleteInstanceMutation,
  useDeleteClassificationDocMutation,
  useRenameInstanceMutation,
  useDeleteDataSourceMutation,
  useAddDataSourceMutation,
  useAddSummerizeMutation,
  useLanguageListQuery,
  useTranslateHistoryQuery,
  useGetClassificationListQuery,
  useClassificationHistoryQuery,
  useGetClassificationQuery,
  useDeleteClassificationMutation,
  useRenameClassificationMutation,
} = translationApi;
